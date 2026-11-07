// ===================================================================
// CONSULTA: Puente_Director   (SÍ se carga)
// Relación con Contenido: * <- 1, filtro ÚNICO (Contenido filtra al puente).
// ===================================================================
let
    Base = Table.SelectRows(Table.SelectColumns(Contenido, {"id_contenido", "director"}), each [director] <> null),
    Lista = Table.TransformColumns(Base, {{"director", each List.Transform(Text.Split(_, ","), Text.Trim)}}),
    Expandida = Table.ExpandListColumn(Lista, "director"),
    Tipo = Table.TransformColumnTypes(Expandida, {{"director", type text}}),
    SinDuplicados = Table.Distinct(Tipo)
in
    SinDuplicados
