"""Genera el diagrama del modelo de datos y el wireframe del dashboard (images/)."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B, O, G, INK, INK2, LINE = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#b8b7b1"

def caja(ax, x, y, w, h, titulo, filas, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc="white", ec=color, lw=2))
    ax.add_patch(FancyBboxPatch((x, y + h - .42), w, .42, boxstyle="round,pad=0.02,rounding_size=0.08", fc=color, ec=color))
    ax.text(x + w / 2, y + h - .21, titulo, ha="center", va="center", color="white", fontsize=9.5, weight="bold")
    for i, f in enumerate(filas):
        ax.text(x + .12, y + h - .68 - i * .27, f, fontsize=7.4, color=INK2, va="center")

def modelo():
    fig, ax = plt.subplots(figsize=(11, 6.4)); ax.set_xlim(0, 11); ax.set_ylim(0, 6.4); ax.axis("off")
    caja(ax, 4.1, 1.2, 2.8, 4.2, "Contenido (hechos)", ["id_contenido (PK)", "tipo · title · anio_estreno", "fecha_incorporacion", "language · pais_principal", "genero_principal", "popularity · vote_count", "valoracion · valoracion_ponderada", "segmento_valoracion · es_estrella", "presupuesto_usd · ingresos_usd", "roi · tramo_presupuesto", "financiero_valido"], B)
    caja(ax, .3, 4.1, 2.5, 1.3, "Puente_Genero", ["id_contenido", "genero (22 homologados)"], O)
    caja(ax, .3, 2.25, 2.5, 1.3, "Puente_Pais", ["id_contenido", "pais (147)"], O)
    caja(ax, .3, .4, 2.5, 1.3, "dim_Idioma", ["codigo (PK)", "idioma · grupo_idioma"], G)
    caja(ax, 8.2, 4.1, 2.5, 1.3, "Puente_Director", ["id_contenido", "director"], O)
    caja(ax, 8.2, 2.25, 2.5, 1.3, "Puente_Actor", ["id_contenido", "actor"], O)
    caja(ax, 8.2, .4, 2.5, 1.3, "Calendario", ["Fecha (PK) · Año", "Mes · Trimestre"], G)
    rel = [((2.8, 4.75), (4.1, 4.6), "* ⟷ 1  (ambas)"), ((2.8, 2.9), (4.1, 3.0), "* ⟷ 1  (ambas)"),
           ((2.8, 1.05), (4.1, 1.6), "1 → *"), ((8.2, 4.75), (6.9, 4.6), "1 → *"),
           ((8.2, 2.9), (6.9, 3.0), "1 → *"), ((8.2, 1.05), (6.9, 1.6), "1 → *")]
    for a, b, t in rel:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-", color=LINE, lw=1.6))
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + .13, t, ha="center", fontsize=7, color=INK2)
    ax.text(0.3, 6.15, "Modelo estrella con tablas puente (Power BI)", fontsize=13, weight="bold", color=INK)
    ax.text(0.3, 5.8, "Azul = hechos · Naranja = puentes multivalor · Verde = dimensiones", fontsize=8.5, color=INK2)
    fig.savefig(os.path.join(ROOT, "images", "Modelo datos.png"), dpi=170, bbox_inches="tight", facecolor="white"); plt.close(fig)

def wireframe():
    fig, ax = plt.subplots(figsize=(12.8, 7.2)); ax.set_xlim(0, 1920); ax.set_ylim(1080, 0); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1920, 1080, fc="#F4F5F7"))
    box = lambda x, y, w, h, fc="white", ec="#E6E5E1": ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=10", fc=fc, ec=ec))
    box(20, 8, 980, 80); ax.text(36, 40, "Resumen Ejecutivo", fontsize=15, weight="bold", va="center")
    ax.text(36, 70, "¿Cómo está el catálogo hoy?  ·  Estreno 2010–2025  ·  Fuente: catálogo StreamView", fontsize=8, color=INK2, va="center")
    for i, p in enumerate(["Inicio", "Catálogo", "Popularidad", "Tendencias", "Financiero", "Hallazgos"]):
        x = 1020 + i * 148; box(x, 22, 140, 44, fc=B if i == 0 else "white", ec=B)
        ax.text(x + 70, 44, p, ha="center", va="center", fontsize=8, color="white" if i == 0 else B, weight="bold")
    for j, (t, hh) in enumerate([("Tipo  [Película] [Serie]", 95), ("Año  ●━━━━━━●", 120), ("Género ▼", 85), ("País ▼", 85), ("Idioma ▼", 85)]):
        y = [100, 205, 335, 430, 525][j]; box(1600, y, 300, hh); ax.text(1616, y + 30, t, fontsize=8.5, va="center")
    box(1640, 625, 220, 48, fc=B, ec=B); ax.text(1750, 649, "Limpiar filtros", ha="center", va="center", color="white", fontsize=8.5, weight="bold")
    k1 = ["Total\n31.991", "Películas\n16.000", "Series\n15.991", "Países\n147", "Idiomas\n83", "Géneros\n22"]
    k2 = ["Popularidad\n22,07", "Nota prom.\n6,63", "% nota ≥ 7\n42,0 %", "% no inglés\n56,3 %", "Estrella\n3.832", "ROI\n2,92x"]
    w = (1560 - 14 * 5) / 6
    for r, ks in enumerate([k1, k2]):
        for i, t in enumerate(ks):
            x = 20 + i * (w + 14); y = 100 + r * 122; box(x, y, w, 110)
            ax.text(x + w / 2, y + 55, t, ha="center", va="center", fontsize=9.5, weight="bold")
    for (x, y), t in zip([(20, 345), (810, 345), (20, 708), (810, 708)],
                         ["Áreas: evolución del catálogo", "Líneas: % contenido no inglés", "Treemap: géneros", "Barras: Top 10 países"]):
        box(x, y, 770, 350); ax.text(x + 16, y + 30, t, fontsize=9, weight="bold")
    fig.savefig(os.path.join(ROOT, "images", "Wireframe resumen.png"), dpi=110, bbox_inches="tight", facecolor="white"); plt.close(fig)

if __name__ == "__main__":
    modelo(); wireframe()
