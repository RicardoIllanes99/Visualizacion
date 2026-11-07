// ===================================================================
// CONSULTA: map_Generos   (NO cargar al modelo: clic derecho > desmarcar "Habilitar carga")
// Homologa la taxonomía de géneros de películas y series (TMDB usa
// géneros distintos para cada tipo) y los traduce al español.
// ===================================================================
let
    Mapa = [
        Drama = "Drama",
        Comedy = "Comedia",
        Animation = "Animación",
        Thriller = "Suspenso",
        Action = "Acción y Aventura",
        Adventure = "Acción y Aventura",
        #"Action & Adventure" = "Acción y Aventura",
        Crime = "Crimen",
        Family = "Familiar",
        Mystery = "Misterio",
        Romance = "Romance",
        Horror = "Terror",
        #"Science Fiction" = "Ciencia Ficción y Fantasía",
        Fantasy = "Ciencia Ficción y Fantasía",
        #"Sci-Fi & Fantasy" = "Ciencia Ficción y Fantasía",
        Documentary = "Documental",
        Reality = "Reality",
        Kids = "Infantil",
        History = "Historia",
        Talk = "Talk Show",
        Soap = "Telenovela",
        #"TV Movie" = "Película para TV",
        Music = "Música",
        War = "Bélico y Política",
        #"War & Politics" = "Bélico y Política",
        Western = "Western",
        News = "Noticias",
        Unknown = "Sin información"
    ]
in
    Mapa
