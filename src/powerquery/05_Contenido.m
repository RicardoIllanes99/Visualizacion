// ===================================================================
// CONSULTA: Contenido   (TABLA DE HECHOS - SÍ se carga)
// Integra películas + series en una sola tabla, 1 fila = 1 contenido.
// ===================================================================
let
    // 1. Integración de las dos fuentes
    Union = Table.Combine({src_Peliculas, src_Series}),
    Renombrar = Table.RenameColumns(Union, {{"type", "tipo_origen"}}),

    // 2. Clave única: show_id se repite en 397 casos ENTRE datasets -> clave compuesta
    ConId = Table.AddColumn(Renombrar, "id_contenido", each
        (if [tipo_origen] = "Movie" then "M-" else "T-") & Text.From([show_id]), type text),

    // 3. Eliminar duplicados (9 show_id repetidos en series)
    SinDuplicados = Table.Distinct(ConId, {"id_contenido"}),

    // 4. Limpieza de espacios en textos
    Limpio = Table.TransformColumns(SinDuplicados, {
        {"title", Text.Trim, type text}, {"director", Text.Trim, type nullable text},
        {"cast", Text.Trim, type nullable text}, {"country", Text.Trim, type nullable text},
        {"genres", Text.Trim, type nullable text}, {"language", Text.Trim, type text}
    }),

    // 5. Atributos derivados
    Tipo = Table.AddColumn(Limpio, "tipo", each
        if [tipo_origen] = "Movie" then "Película" else "Serie", type text),
    PaisPrincipal = Table.AddColumn(Tipo, "pais_principal", each
        if [country] = null then "Sin información"
        else Text.Trim(List.First(Text.Split([country], ","))), type text),
    GeneroPrincipal = Table.AddColumn(PaisPrincipal, "genero_principal", each
        Record.FieldOrDefault(map_Generos,
            if [genres] = null then "Unknown" else Text.Trim(List.First(Text.Split([genres], ","))),
            "Sin información"), type text),

    // 6. Valoración: con 0 votos el promedio (0) no es una calificación real -> nulo
    Valoracion = Table.AddColumn(GeneroPrincipal, "valoracion", each
        if [vote_count] > 0 then [vote_average] else null, type nullable number),
    Segmento = Table.AddColumn(Valoracion, "segmento_valoracion", each
        if [vote_count] = 0 then "Sin votos"
        else if [vote_average] >= 8 then "Excelente (≥8)"
        else if [vote_average] >= 7 then "Alta (7–7,9)"
        else if [vote_average] >= 5 then "Media (5–6,9)"
        else "Baja (<5)", type text),
    SegmentoOrden = Table.AddColumn(Segmento, "segmento_orden", each
        if [segmento_valoracion] = "Excelente (≥8)" then 1
        else if [segmento_valoracion] = "Alta (7–7,9)" then 2
        else if [segmento_valoracion] = "Media (5–6,9)" then 3
        else if [segmento_valoracion] = "Baja (<5)" then 4 else 5, Int64.Type),

    // 7. Estadísticos por tipo (las escalas de películas y series NO son comparables)
    Stats = Table.Group(SegmentoOrden, {"tipo"}, {
        {"C_tipo", each List.Average(List.RemoveNulls([valoracion])), type number},
        {"pop_mediana_tipo", each List.Median([popularity]), type number}
    }),
    Unido = Table.NestedJoin(SegmentoOrden, {"tipo"}, Stats, {"tipo"}, "st", JoinKind.LeftOuter),
    Expandido = Table.ExpandTableColumn(Unido, "st", {"C_tipo", "pop_mediana_tipo"}),

    // 8. Valoración ponderada (bayesiana, estilo IMDb): evita que un título con
    //    pocos votos y nota 10 encabece el ranking.  WR = v/(v+m)*R + m/(v+m)*C , m = 200
    Ponderada = Table.AddColumn(Expandido, "valoracion_ponderada", each
        ([vote_count] / ([vote_count] + 200)) * (if [vote_count] > 0 then [vote_average] else 0)
        + (200 / ([vote_count] + 200)) * [C_tipo], type number),

    // 9. Contenido "estrella": valoración >= 7, >= 50 votos y popularidad >= mediana de su tipo
    Estrella = Table.AddColumn(Ponderada, "es_estrella", each
        [valoracion] <> null and [valoracion] >= 7 and [vote_count] >= 50
        and [popularity] >= [pop_mediana_tipo], type logical),

    // 10. Financiero: SOLO películas con budget y revenue >= USD 10.000
    //     (0 = sin dato; valores 1–9.999 son registros de prueba / errores de carga)
    Financiero = Table.AddColumn(Estrella, "financiero_valido", each
        [tipo_origen] = "Movie" and [budget] <> null and [revenue] <> null
        and [budget] >= 10000 and [revenue] >= 10000, type logical),
    Presupuesto = Table.AddColumn(Financiero, "presupuesto_usd", each
        if [financiero_valido] then [budget] else null, type nullable number),
    Ingresos = Table.AddColumn(Presupuesto, "ingresos_usd", each
        if [financiero_valido] then [revenue] else null, type nullable number),
    ROI = Table.AddColumn(Ingresos, "roi", each
        if [financiero_valido] then [revenue] / [budget] else null, type nullable number),
    Tramo = Table.AddColumn(ROI, "tramo_presupuesto", each
        if not [financiero_valido] then null
        else if [budget] < 5000000 then "< 5M"
        else if [budget] < 20000000 then "5–20M"
        else if [budget] < 60000000 then "20–60M"
        else "> 60M", type nullable text),
    TramoOrden = Table.AddColumn(Tramo, "tramo_orden", each
        if [tramo_presupuesto] = "< 5M" then 1
        else if [tramo_presupuesto] = "5–20M" then 2
        else if [tramo_presupuesto] = "20–60M" then 3
        else if [tramo_presupuesto] = "> 60M" then 4 else null, Int64.Type),

    // 11. Nombres finales
    Nombres = Table.RenameColumns(TramoOrden, {
        {"date_added", "fecha_incorporacion"}, {"release_year", "anio_estreno"}}),
    Final = Table.RemoveColumns(Nombres, {"C_tipo"})
in
    Final
