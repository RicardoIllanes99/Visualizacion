// ===================================================================
// CONSULTA: src_Peliculas   (NO cargar al modelo)
// Lee el CSV ORIGINAL sin modificarlo. Cultura "en-US" para que el
// punto decimal se lea bien en un PC configurado en español (Chile).
// ===================================================================
let
    Origen = Csv.Document(
        File.Contents(RutaDatos & "netflix_movies_detailed_up_to_2025.csv"),
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
        {"popularity", type number}, {"vote_count", Int64.Type},
        {"vote_average", type number}, {"budget", type number}, {"revenue", type number}
    }, "en-US"),
    // "rating" es idéntica a vote_average (100% de coincidencia) y "duration" viene 100% vacía
    // en películas -> no se usan. Se seleccionan las columnas comunes + financieras.
    Seleccion = Table.SelectColumns(Tipos, {
        "show_id", "type", "title", "director", "cast", "country", "date_added",
        "release_year", "genres", "language", "description", "popularity",
        "vote_count", "vote_average", "budget", "revenue"
    })
in
    Seleccion
