// ===================================================================
// CONSULTA: Puente_Pais   (SÍ se carga)
// Coproducciones: un título cuenta para cada país participante.
// Relación con Contenido: * <-> 1, filtro AMBOS.
// ===================================================================
let
    Base = Table.SelectColumns(Contenido, {"id_contenido", "country"}),
    Lista = Table.TransformColumns(Base, {{"country", each
        if _ = null then {"Sin información"} else List.Transform(Text.Split(_, ","), Text.Trim)}}),
    Expandida = Table.ExpandListColumn(Lista, "country"),
    Renombrada = Table.RenameColumns(Expandida, {{"country", "pais"}}),
    Tipo = Table.TransformColumnTypes(Renombrada, {{"pais", type text}}),
    SinDuplicados = Table.Distinct(Tipo)
in
    SinDuplicados
