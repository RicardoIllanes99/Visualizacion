// ===================================================================
// CONSULTA: Puente_Genero   (SÍ se carga)
// "genres" trae varios géneros separados por coma -> 1 fila por par
// (contenido, género). Relación con Contenido: * <-> 1, filtro AMBOS.
// ===================================================================
let
    Base = Table.SelectColumns(Contenido, {"id_contenido", "genres"}),
    Lista = Table.TransformColumns(Base, {{"genres", each
        if _ = null then {"Unknown"} else List.Transform(Text.Split(_, ","), Text.Trim)}}),
    Expandida = Table.ExpandListColumn(Lista, "genres"),
    Homologada = Table.TransformColumns(Expandida, {{"genres", each
        Record.FieldOrDefault(map_Generos, _, _), type text}}),
    Renombrada = Table.RenameColumns(Homologada, {{"genres", "genero"}}),
    // "Action" + "Adventure" en el mismo título -> 1 sola fila "Acción y Aventura"
    SinDuplicados = Table.Distinct(Renombrada)
in
    SinDuplicados
