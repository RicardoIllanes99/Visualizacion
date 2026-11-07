"""
StreamView Analytics - EP2 Visualización de Datos (ADY1104)
Análisis exploratorio y reglas de integración.

Replica en Python EXACTAMENTE las mismas reglas que aplica Power Query
(src/powerquery/*.m), para validar que los KPIs del dashboard son correctos.

Uso:  python src/eda_streamview.py      (desde la raíz del proyecto)
Salida: images/*.png  y  data/processed/kpis_validacion.json
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT_IMG = os.path.join(ROOT, "images")
OUT_DATA = os.path.join(ROOT, "data", "processed")
os.makedirs(OUT_IMG, exist_ok=True); os.makedirs(OUT_DATA, exist_ok=True)

# ---------------- Paleta (misma que el tema de Power BI) ----------------
C_MOVIE, C_TV, C_ACC = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": .6,
    "axes.titleweight": "bold", "axes.titlesize": 12, "axes.titlecolor": INK,
    "figure.dpi": 150, "savefig.bbox": "tight", "figure.facecolor": "white"})

# ---------------- Diccionarios de homologación ----------------
GENRE_MAP = {
    "Drama": "Drama", "Comedy": "Comedia", "Animation": "Animación",
    "Thriller": "Suspenso", "Action": "Acción y Aventura",
    "Adventure": "Acción y Aventura", "Action & Adventure": "Acción y Aventura",
    "Crime": "Crimen", "Family": "Familiar", "Mystery": "Misterio",
    "Romance": "Romance", "Horror": "Terror",
    "Science Fiction": "Ciencia Ficción y Fantasía", "Fantasy": "Ciencia Ficción y Fantasía",
    "Sci-Fi & Fantasy": "Ciencia Ficción y Fantasía", "Documentary": "Documental",
    "Reality": "Reality", "Kids": "Infantil", "History": "Historia",
    "Talk": "Talk Show", "Soap": "Telenovela", "TV Movie": "Película para TV",
    "Music": "Música", "War": "Bélico y Política", "War & Politics": "Bélico y Política",
    "Western": "Western", "News": "Noticias", "Unknown": "Sin información"}

LANG_MAP = {"af":"Afrikáans","am":"Amárico","ar":"Árabe","as":"Asamés","az":"Azerí","bg":"Búlgaro",
 "bn":"Bengalí","bs":"Bosnio","ca":"Catalán","cn":"Cantonés","cs":"Checo","cy":"Galés","da":"Danés",
 "de":"Alemán","dz":"Dzongkha","el":"Griego","en":"Inglés","es":"Español","et":"Estonio","eu":"Euskera",
 "fa":"Persa","fi":"Finés","fr":"Francés","ga":"Irlandés","gl":"Gallego","he":"Hebreo","hi":"Hindi",
 "hr":"Croata","ht":"Criollo haitiano","hu":"Húngaro","hy":"Armenio","id":"Indonesio","is":"Islandés",
 "it":"Italiano","ja":"Japonés","ka":"Georgiano","kk":"Kazajo","kl":"Groenlandés","km":"Jemer",
 "kn":"Canarés","ko":"Coreano","ku":"Kurdo","ky":"Kirguís","la":"Latín","lb":"Luxemburgués",
 "lt":"Lituano","lv":"Letón","mi":"Maorí","mk":"Macedonio","ml":"Malayalam","mn":"Mongol",
 "mr":"Maratí","ms":"Malayo","mt":"Maltés","nb":"Noruego bokmål","ne":"Nepalí","nl":"Neerlandés",
 "no":"Noruego","or":"Oriya","pa":"Panyabí","pl":"Polaco","ps":"Pastún","pt":"Portugués",
 "ro":"Rumano","ru":"Ruso","si":"Cingalés","sk":"Eslovaco","sl":"Esloveno","sr":"Serbio",
 "sv":"Sueco","ta":"Tamil","te":"Telugu","th":"Tailandés","tl":"Tagalo","tr":"Turco",
 "uk":"Ucraniano","ur":"Urdu","vi":"Vietnamita","xx":"Sin idioma","yo":"Yoruba","za":"Zhuang",
 "zh":"Chino mandarín","zu":"Zulú"}

M_BAYES = 200                # votos "de confianza" para la valoración ponderada (fórmula tipo IMDb)
MIN_FIN = 10_000             # USD: umbral de validez de budget y revenue
MIN_BUDGET_ROI = 1_000_000   # USD: presupuesto mínimo para el ranking de ROI


def segmento(va, vc):
    if vc == 0: return "Sin votos"
    if va >= 8: return "Excelente (≥8)"
    if va >= 7: return "Alta (7–7,9)"
    if va >= 5: return "Media (5–6,9)"
    return "Baja (<5)"


def cargar():
    m = pd.read_csv(os.path.join(RAW, "netflix_movies_detailed_up_to_2025.csv"))
    t = pd.read_csv(os.path.join(RAW, "netflix_tv_shows_detailed_up_to_2025.csv"))
    calidad = {
        "filas_movies": len(m), "filas_tv": len(t),
        "ids_duplicados_tv": int(t.show_id.duplicated().sum()),
        "ids_compartidos_entre_datasets": len(set(m.show_id) & set(t.show_id)),
        "duration_nula_movies": int(m.duration.isna().sum()),
        "duration_valores_tv": t.duration.value_counts().to_dict(),
        "rating_igual_vote_average_%": float(((pd.concat([m, t]).rating ==
                                              pd.concat([m, t]).vote_average).mean()) * 100),
        "nulos_movies": m.isna().sum()[lambda s: s > 0].to_dict(),
        "nulos_tv": t.isna().sum()[lambda s: s > 0].to_dict(),
        "sin_votos_movies": int((m.vote_count == 0).sum()),
        "sin_votos_tv": int((t.vote_count == 0).sum()),
        "budget_0": int((m.budget == 0).sum()), "revenue_0": int((m.revenue == 0).sum()),
        "budget_entre_1_y_9999": int(((m.budget > 0) & (m.budget < MIN_FIN)).sum()),
        "revenue_entre_1_y_9999": int(((m.revenue > 0) & (m.revenue < MIN_FIN)).sum()),
        "titulos_por_anio": "1.000 películas y 1.000 series por año (2010–2025)",
    }
    # --- Integración (igual que Power Query) ---
    m["budget_usd"], m["revenue_usd"] = m.budget, m.revenue
    t["budget_usd"], t["revenue_usd"] = np.nan, np.nan
    cols = ["show_id", "type", "title", "director", "cast", "country", "date_added",
            "release_year", "genres", "language", "popularity", "vote_count",
            "vote_average", "budget_usd", "revenue_usd"]
    a = pd.concat([m[cols], t[cols]], ignore_index=True)
    a["tipo"] = a.type.map({"Movie": "Película", "TV Show": "Serie"})
    a["id_contenido"] = np.where(a.type == "Movie", "M-", "T-") + a.show_id.astype(str)
    a = a.drop_duplicates("id_contenido", keep="first")
    for c in ["title", "director", "cast", "country", "genres"]:
        a[c] = a[c].str.strip()
    a["date_added"] = pd.to_datetime(a.date_added)
    a["pais_principal"] = a.country.fillna("Sin información").str.split(",").str[0].str.strip()
    a["genero_principal"] = a.genres.fillna("Unknown").str.split(",").str[0].str.strip().map(GENRE_MAP)
    a["idioma"] = a.language.map(LANG_MAP).fillna(a.language)
    a["valoracion"] = np.where(a.vote_count > 0, a.vote_average, np.nan)
    a["segmento_valoracion"] = [segmento(x, y) for x, y in zip(a.vote_average, a.vote_count)]
    # Valoración ponderada: WR = v/(v+m)*R + m/(v+m)*C   (C = promedio del tipo)
    C = a.groupby("tipo").valoracion.transform("mean")
    v = a.vote_count
    a["valoracion_ponderada"] = (v / (v + M_BAYES)) * a.vote_average.where(v > 0, 0) + (M_BAYES / (v + M_BAYES)) * C
    # Contenido "estrella": valoración >= 7, >= 50 votos y popularidad >= mediana de su tipo
    a["pop_mediana_tipo"] = a.groupby("tipo").popularity.transform("median")
    a["es_estrella"] = (a.valoracion >= 7) & (a.vote_count >= 50) & (a.popularity >= a.pop_mediana_tipo)
    fin = (a.type == "Movie") & (a.budget_usd >= MIN_FIN) & (a.revenue_usd >= MIN_FIN)
    a["financiero_valido"] = fin
    a["roi"] = np.where(fin, a.revenue_usd / a.budget_usd, np.nan)
    calidad["filas_integradas"] = len(a)
    calidad["peliculas_financiero_valido"] = int(fin.sum())
    return a, calidad


def puente(a, col, mapa=None, nombre="valor"):
    b = a[["id_contenido", col]].dropna().copy()
    b[nombre] = b[col].str.split(",")
    b = b.explode(nombre)
    b[nombre] = b[nombre].str.strip()
    if mapa: b[nombre] = b[nombre].map(mapa).fillna(b[nombre])
    return b[["id_contenido", nombre]].drop_duplicates()


def main():
    a, calidad = cargar()
    bg = puente(a, "genres", GENRE_MAP, "genero")
    bp = puente(a, "country", None, "pais")
    k = {"calidad": calidad}

    # ---------- KPIs de catálogo ----------
    k["catalogo"] = {
        "total": len(a), "peliculas": int((a.tipo == "Película").sum()),
        "series": int((a.tipo == "Serie").sum()), "paises": int(bp.pais.nunique()),
        "idiomas": int(a.language.nunique()),
        "generos": int(bg[bg.genero != "Sin información"].genero.nunique()),
        "periodo": f"{a.release_year.min()}–{a.release_year.max()}"}

    # ---------- Popularidad / valoración ----------
    k["popularidad"] = {
        "media_total": round(a.popularity.mean(), 2), "mediana_total": round(a.popularity.median(), 2),
        "mediana_pelicula": round(a[a.tipo == "Película"].popularity.median(), 2),
        "mediana_serie": round(a[a.tipo == "Serie"].popularity.median(), 2),
        "media_pelicula": round(a[a.tipo == "Película"].popularity.mean(), 2),
        "media_serie": round(a[a.tipo == "Serie"].popularity.mean(), 2)}
    k["valoracion"] = {
        "promedio_total": round(a.valoracion.mean(), 2),
        "promedio_pelicula": round(a[a.tipo == "Película"].valoracion.mean(), 2),
        "promedio_serie": round(a[a.tipo == "Serie"].valoracion.mean(), 2),
        "pct_alta_o_excelente": round(a.valoracion.ge(7).sum() / a.valoracion.notna().sum() * 100, 1),
        "estrellas": int(a.es_estrella.sum()), "pct_estrellas": round(a.es_estrella.mean() * 100, 1),
        "estrellas_pelicula": int(a[a.tipo == "Película"].es_estrella.sum()), "estrellas_serie": int(a[a.tipo == "Serie"].es_estrella.sum()),
        "spearman_pop_val": round(a[["popularity", "valoracion"]].dropna().corr("spearman").iloc[0, 1], 3),
        "segmentos": a.segmento_valoracion.value_counts().to_dict()}

    g = bg.merge(a, on="id_contenido")
    gen = g.groupby("genero").agg(titulos=("id_contenido", "nunique"),
                                  pop_med=("popularity", "median"),
                                  val=("valoracion", "mean")).sort_values("titulos", ascending=False)
    k["generos"] = gen.round(2).reset_index().to_dict("records")
    gen_t = g.groupby(["genero", "tipo"]).agg(n=("id_contenido", "nunique"),
                                              pop_med=("popularity", "median"),
                                              val=("valoracion", "mean")).round(2).reset_index()
    k["estrella_por_genero"] = g.groupby("genero").es_estrella.mean().mul(100).round(1).sort_values(ascending=False).to_dict()
    k["generos_por_tipo"] = gen_t.to_dict("records")

    p = bp.merge(a, on="id_contenido")
    pais = p.groupby("pais").agg(titulos=("id_contenido", "nunique"), pop_med=("popularity", "median"),
                                 val=("valoracion", "mean")).sort_values("titulos", ascending=False)
    k["paises_top15"] = pais.head(15).round(2).reset_index().to_dict("records")
    k["paises_mejor_val_min300"] = pais[pais.titulos >= 300].sort_values("val", ascending=False).head(10).round(2).reset_index().to_dict("records")

    idi = a.groupby("idioma").agg(titulos=("id_contenido", "size"), pop_med=("popularity", "median"),
                                  val=("valoracion", "mean")).sort_values("titulos", ascending=False)
    k["idiomas_top12"] = idi.head(12).round(2).reset_index().to_dict("records")
    share = a.assign(ing=a.language.eq("en")).groupby(["release_year", "tipo"]).ing.mean().unstack()
    k["pct_ingles_por_anio"] = (share * 100).round(1).to_dict()

    top = lambda d, c, n=10: d.sort_values(c, ascending=False).head(n)[["title", "tipo", "release_year", "popularity", "valoracion", "valoracion_ponderada", "vote_count"]].round(2).to_dict("records")
    k["top_popular_pelis"] = top(a[a.tipo == "Película"], "popularity")
    k["top_popular_series"] = top(a[a.tipo == "Serie"], "popularity")
    k["top_val_pelis"] = top(a[a.tipo == "Película"], "valoracion_ponderada")
    k["top_val_series"] = top(a[a.tipo == "Serie"], "valoracion_ponderada")
    k["top_votos"] = top(a, "vote_count")

    # ---------- Temporal ----------
    k["temporal"] = {
        "pop_mediana_anio": a.groupby(["release_year", "tipo"]).popularity.median().unstack().round(2).to_dict(),
        "val_anio": a.groupby(["release_year", "tipo"]).valoracion.mean().unstack().round(2).to_dict(),
        "pct_sin_votos_anio": a.assign(s=a.vote_count.eq(0)).groupby(["release_year", "tipo"]).s.mean().unstack().mul(100).round(1).to_dict()}
    gy = g.groupby(["release_year", "genero"]).id_contenido.nunique().unstack().fillna(0)
    k["generos_crecimiento"] = ((gy.loc[2021:2025].sum() / gy.loc[2010:2014].sum() - 1) * 100).round(1).sort_values().to_dict()

    # ---------- Producción ----------
    dirs = a.director.dropna().str.split(",").explode().str.strip()
    k["top_directores"] = dirs.value_counts().head(10).to_dict()
    cast = a.cast.dropna().str.split(",").explode().str.strip()
    k["top_actores"] = cast.value_counts().head(10).to_dict()

    # ---------- Financiero ----------
    f = a[a.financiero_valido].copy()
    k["financiero"] = {
        "peliculas_validas": len(f), "pct_de_peliculas": round(len(f) / (a.tipo == "Película").sum() * 100, 1),
        "presupuesto_total": int(f.budget_usd.sum()), "ingresos_totales": int(f.revenue_usd.sum()),
        "presupuesto_promedio": round(f.budget_usd.mean()), "ingreso_promedio": round(f.revenue_usd.mean()),
        "roi_agregado": round(f.revenue_usd.sum() / f.budget_usd.sum(), 2),
        "roi_mediano": round(f.roi.median(), 2),
        "pct_rentables_roi_gt1": round((f.roi > 1).mean() * 100, 1),
        "spearman_budget_revenue": round(f[["budget_usd", "revenue_usd"]].corr("spearman").iloc[0, 1], 3),
        "pearson_log": round(np.log10(f[["budget_usd", "revenue_usd"]]).corr().iloc[0, 1], 3)}
    k["top_ingresos"] = f.sort_values("revenue_usd", ascending=False).head(10)[["title", "release_year", "budget_usd", "revenue_usd", "roi"]].round(2).to_dict("records")
    k["top_roi"] = f[f.budget_usd >= MIN_BUDGET_ROI].sort_values("roi", ascending=False).head(10)[["title", "release_year", "budget_usd", "revenue_usd", "roi"]].round(2).to_dict("records")
    k["exitos_bajo_presupuesto"] = f[f.budget_usd < 5_000_000].sort_values("revenue_usd", ascending=False).head(10)[["title", "release_year", "budget_usd", "revenue_usd", "roi"]].round(2).to_dict("records")
    fg = bg.merge(f, on="id_contenido")
    k["roi_por_genero"] = fg.groupby("genero").agg(n=("id_contenido", "nunique"), roi_med=("roi", "median"),
                                                   ingreso_med=("revenue_usd", "median")).query("n>=50").sort_values("roi_med", ascending=False).round(2).reset_index().to_dict("records")
    f["tramo"] = pd.cut(f.budget_usd, [0, 5e6, 20e6, 60e6, 1e10], labels=["<5M", "5–20M", "20–60M", ">60M"])
    k["roi_por_tramo"] = f.groupby("tramo", observed=True).agg(n=("roi", "size"), roi_med=("roi", "median"),
                                                               pct_rent=("roi", lambda s: (s > 1).mean() * 100)).round(2).reset_index().astype(str).to_dict("records")

    # ---------- Índice de oportunidad por género (popularidad × valoración, por tipo) ----------
    with open(os.path.join(OUT_DATA, "kpis_validacion.json"), "w", encoding="utf-8") as fh:
        json.dump(k, fh, ensure_ascii=False, indent=1, default=str)

    graficos(a, g, p, f, gen, gen_t, share, gy)
    print(json.dumps({x: k[x] for x in ["catalogo", "popularidad", "valoracion", "financiero"]}, ensure_ascii=False, indent=1))
    return k


def miles(x, _=None):
    return f"{x:,.0f}".replace(",", ".")


def graficos(a, g, p, f, gen, gen_t, share, gy):
    # 1. Géneros predominantes por tipo (barras horizontales agrupadas)
    top = gen[gen.index != "Sin información"].head(12).index[::-1]
    piv = gen_t.pivot(index="genero", columns="tipo", values="n").reindex(top).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 5.2)); y = np.arange(len(top)); h = .38
    ax.barh(y + h / 2, piv["Película"], h, color=C_MOVIE, label="Películas")
    ax.barh(y - h / 2, piv["Serie"], h, color=C_TV, label="Series")
    ax.set_yticks(y, top); ax.xaxis.set_major_formatter(mt.FuncFormatter(miles)); ax.grid(axis="y", visible=False)
    ax.set_title("Drama y Comedia dominan el catálogo en ambos formatos", loc="left")
    ax.set_xlabel("N.º de títulos (un título puede tener varios géneros)"); ax.legend(frameon=False, loc="lower right")
    fig.text(0, -.02, "Fuente: catálogo StreamView 2010–2025 (31.991 títulos). Géneros homologados películas/series.\nSuspenso, Romance y Terror no existen en la taxonomía de series de origen.", color=INK2, fontsize=8)
    fig.savefig(os.path.join(OUT_IMG, "Generos tipo.png")); plt.close(fig)

    # 2. % títulos en inglés por año (línea)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(share.index, share["Película"] * 100, color=C_MOVIE, lw=2, marker="o", ms=4, label="Películas")
    ax.plot(share.index, share["Serie"] * 100, color=C_TV, lw=2, marker="o", ms=4, label="Series")
    ax.set_ylim(0, 80); ax.yaxis.set_major_formatter(mt.PercentFormatter())
    ax.set_title("El catálogo se internacionaliza: cae el peso del inglés", loc="left")
    ax.set_ylabel("% de títulos en inglés"); ax.legend(frameon=False)
    fig.text(0, -.03, "Fuente: catálogo StreamView, año de estreno 2010–2025. Cada año aporta 1.000 películas y 1.000 series.", color=INK2, fontsize=8)
    fig.savefig(os.path.join(OUT_IMG, "Ingles año.png")); plt.close(fig)

    # 3. Popularidad mediana vs valoración por género (dispersión, por tipo)
    fig, axs = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    for ax, ty, col in zip(axs, ["Película", "Serie"], [C_MOVIE, C_TV]):
        d = gen_t[(gen_t.tipo == ty) & (gen_t.n >= 150) & (gen_t.genero != "Sin información")]
        ax.scatter(d.pop_med, d.val, s=d.n / 12, color=col, alpha=.75, edgecolor="white", lw=1.5)
        txt = [ax.text(r.pop_med, r.val, r.genero, fontsize=7, color=INK2) for _, r in d.iterrows()]
        try:
            from adjustText import adjust_text
            adjust_text(txt, ax=ax, arrowprops=dict(arrowstyle="-", color=GRID, lw=.6))
        except ImportError:
            pass
        ax.axhline(d.val.mean(), color=INK2, lw=.8, ls="--"); ax.axvline(d.pop_med.median(), color=INK2, lw=.8, ls="--")
        ax.set_title(f"{ty}s", loc="left"); ax.set_xlabel("Popularidad mediana (índice TMDB)")
    axs[0].set_ylabel("Valoración promedio (0–10)")
    fig.suptitle("Mapa de oportunidad por género: arriba-derecha = popular y bien evaluado", x=.06, ha="left", fontweight="bold")
    fig.text(0, -.03, "Tamaño = n.º de títulos. Escalas de popularidad NO comparables entre películas y series (regla de negocio 2).", color=INK2, fontsize=8)
    fig.savefig(os.path.join(OUT_IMG, "Oportunidad generos.png")); plt.close(fig)

    # 4. Países productores (top 12)
    pais = p.groupby("pais").id_contenido.nunique().sort_values(ascending=False).head(12)[::-1]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh(pais.index, pais.values, color=C_MOVIE); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(mt.FuncFormatter(miles))
    for i, v in enumerate(pais.values): ax.text(v + 80, i, miles(v), va="center", fontsize=8, color=INK2)
    ax.set_title("EE.UU. concentra un tercio del catálogo; Asia es el segundo polo", loc="left")
    ax.set_xlabel("N.º de títulos (coproducciones cuentan en cada país)")
    fig.savefig(os.path.join(OUT_IMG, "Paises.png")); plt.close(fig)

    # 5. Presupuesto vs ingresos (log-log)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(f.budget_usd, f.revenue_usd, s=10, color=C_MOVIE, alpha=.35, edgecolor="none")
    lim = [1e4, 4e9]; ax.plot(lim, lim, color=C_TV, lw=1.5, ls="--", label="ROI = 1 (punto de equilibrio)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e4, 1e9); ax.set_ylim(1e4, 4e9)
    fmt = mt.FuncFormatter(lambda x, _: f"${x/1e6:,.0f}M" if x >= 1e6 else f"${x/1e3:,.0f}K")
    ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
    ax.set_xlabel("Presupuesto (USD, escala log)"); ax.set_ylabel("Ingresos (USD, escala log)")
    ax.set_title("A mayor presupuesto, mayores ingresos… pero con alta dispersión", loc="left"); ax.legend(frameon=False)
    fig.text(0, -.03, f"Sólo películas con budget y revenue ≥ USD 10.000 (n = {len(f):,}). Series excluidas (regla 3).".replace(",", "."), color=INK2, fontsize=8)
    fig.savefig(os.path.join(OUT_IMG, "Budget revenue.png")); plt.close(fig)

    # 6. ROI mediano por tramo de presupuesto
    f2 = f.copy(); f2["tramo"] = pd.cut(f2.budget_usd, [0, 5e6, 20e6, 60e6, 1e10], labels=["< 5M", "5–20M", "20–60M", "> 60M"])
    r = f2.groupby("tramo", observed=True).roi.median()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(r.index.astype(str), r.values, color=C_MOVIE, width=.55); ax.grid(axis="x", visible=False)
    for i, v in enumerate(r.values): ax.text(i, v + .05, f"{v:.2f}x".replace(".", ","), ha="center", color=INK, fontsize=9)
    ax.axhline(1, color=C_TV, ls="--", lw=1.2); ax.set_ylabel("ROI mediano (Ingresos / Presupuesto)")
    ax.set_xlabel("Tramo de presupuesto (USD)")
    ax.set_title("El retorno mediano mejora con presupuestos medios y altos", loc="left")
    fig.savefig(os.path.join(OUT_IMG, "Roi tramo.png")); plt.close(fig)

    # 7. Popularidad mediana por año y tipo
    pm = a.groupby(["release_year", "tipo"]).popularity.median().unstack()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(pm.index, pm["Película"], color=C_MOVIE, lw=2, marker="o", ms=4, label="Películas")
    ax.plot(pm.index, pm["Serie"], color=C_TV, lw=2, marker="o", ms=4, label="Series")
    ax.set_ylabel("Popularidad mediana (índice)"); ax.legend(frameon=False)
    ax.set_title("Las series son ~3 veces más 'populares' que las películas en el índice", loc="left")
    fig.text(0, -.03, "Popularidad = índice relativo TMDB; no son reproducciones (regla 5). 2025 incompleto en votos.", color=INK2, fontsize=8)
    fig.savefig(os.path.join(OUT_IMG, "Popularidad año.png")); plt.close(fig)


if __name__ == "__main__":
    main()
