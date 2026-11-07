// ===================================================================
// CONSULTA: src_Series   (NO cargar al modelo)
// Mismo esquema que src_Peliculas. Las series NO tienen budget/revenue:
// se agregan como columnas nulas para poder unir ambas tablas
// (regla de negocio 3 y 9: no se inventan valores).
// ===================================================================
let
    Origen = Csv.Document(
        File.Contents(RutaDatos & "netflix_tv_shows_detailed_up_to_2025.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    VaciosANulo = Table.ReplaceValue(Encabezados, "", null, Replacer.ReplaceValue,
        {"director", "cast", "country", "genres", "description"}),
    Tipos = Table.TransformColumnTypes(VaciosANulo, {
        {"show_id", Int64.Type}, {"type", type text}, {"title", type text},
        {"director", type text}, {"cast", type text}, {"country", type text},
        {"date_added", type date}, {"release_year", Int64.Type},
        {"genres", type text}, {"language", type text}, {"description", type text},
        {"popularity", type number}, {"vote_count", Int64.Type}, {"vote_average", type number}
    }, "en-US"),
    // "duration" en series vale siempre "1 Seasons" (sin variabilidad) -> no se usa.
    Seleccion = Table.SelectColumns(Tipos, {
        "show_id", "type", "title", "director", "cast", "country", "date_added",
        "release_year", "genres", "language", "description", "popularity",
        "vote_count", "vote_average"
    }),
    ConBudget = Table.AddColumn(Seleccion, "budget", each null, type nullable number),
    ConRevenue = Table.AddColumn(ConBudget, "revenue", each null, type nullable number)
in
    ConRevenue
