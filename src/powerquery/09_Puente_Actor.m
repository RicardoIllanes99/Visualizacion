// ===================================================================
// CONSULTA: Puente_Actor   (SÍ se carga)
// Relación con Contenido: * <- 1, filtro ÚNICO.
// ===================================================================
let
    Base = Table.SelectRows(Table.SelectColumns(Contenido, {"id_contenido", "cast"}), each [cast] <> null),
    Lista = Table.TransformColumns(Base, {{"cast", each List.Transform(Text.Split(_, ","), Text.Trim)}}),
    Expandida = Table.ExpandListColumn(Lista, "cast"),
    Renombrada = Table.RenameColumns(Expandida, {{"cast", "actor"}}),
    Tipo = Table.TransformColumnTypes(Renombrada, {{"actor", type text}}),
    SinDuplicados = Table.Distinct(Tipo)
in
    SinDuplicados
