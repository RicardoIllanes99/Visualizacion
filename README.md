# StreamView Analytics: dashboard de Visual Analytics en Power BI

Proyecto de la **Evaluación Parcial N.º 2** de **ADY1104 Visualización de Datos** (Duoc UC, Escuela de Informática y Telecomunicaciones).

Actuamos como equipo consultor de **StreamView Analytics**, una plataforma de streaming latinoamericana. El trabajo transforma su catálogo de **31.991 películas y series (2010–2025)** en un dashboard interactivo, un informe ejecutivo y una presentación con recomendaciones de negocio.

**Equipo:** Ricardo Illanes · Marvin Francisconi
**Docente:** Pablo Espinoza · **Sección:** 001V

---

## Inicio rápido (ver el dashboard en 1 minuto)

1. En GitHub, pulsa **Code → Download ZIP** y extrae el archivo descargado (clic derecho → *Extraer todo*).
2. Instala **Power BI Desktop** (gratis, en Microsoft Store) si no lo tienes.
3. Abre **`dashboard/StreamView_Dashboard.pbix`**.

El `.pbix` trae los datos incluidos, así que se ve completo al instante en cualquier computador, sin configurar nada.

## Contenido del repositorio

```
StreamView/
├── README.md                      ← este archivo
├── StreamView.code-workspace      ← abre el proyecto en VS Code (configuración, extensiones y tareas)
├── requirements.txt               ← librerías de Python (sólo para validación)
├── dashboard/
│   ├── StreamView_Dashboard.pbix  ← ABRIR ESTE ARCHIVO (dashboard listo, con datos)
│   ├── StreamView_EP2.pbip        ← versión proyecto (para editar o versionar en Git)
│   ├── StreamView_EP2.Report/     ← páginas y visuales del informe (formato PBIR)
│   ├── StreamView_EP2.SemanticModel/  ← modelo de datos, medidas DAX y consultas (TMDL)
│   └── tema_streamview.json       ← tema de colores del dashboard
├── docs/
│   ├── Informe_Ejecutivo_StreamView.docx
│   └── Presentacion_StreamView.pptx   (+ versiones PDF)
├── data/
│   ├── raw/                       ← los 2 CSV originales del caso (sin modificar)
│   └── processed/kpis_validacion.json ← KPIs de referencia calculados en Python
├── notebooks/
│   └── 01_EDA_StreamView.ipynb    ← análisis exploratorio y calidad de datos
├── src/
│   ├── powerquery/                ← código M de las 10 consultas de Power Query
│   ├── dax/                       ← tablas calculadas y medidas DAX
│   ├── eda_streamview.py          ← mismas reglas que Power Query, en Python
│   └── diagramas.py               ← diagrama del modelo y wireframe
└── images/                        ← gráficos estáticos usados en informe y presentación
```

## Cómo editar el proyecto (versión PBIP)

Para sólo ver el dashboard, usa el `.pbix` del inicio rápido. El `.pbip` sirve para editar y ver los cambios en Git.

1. Instala **Power BI Desktop**: es gratis y está en Microsoft Store.
2. Abre **`dashboard/StreamView_EP2.pbip`**. Las carpetas `StreamView_EP2.Report` y `StreamView_EP2.SemanticModel` deben estar al lado del archivo; no lo abras desde dentro de un .zip.
3. El modelo trae los datos en caché, así que se ve de inmediato. Para recargar desde los CSV, ajusta la ruta de datos (ver más abajo) y luego **Inicio → Actualizar**.
4. Para compartirlo en un solo archivo: **Archivo → Guardar como → Archivo de Power BI (.pbix)**.

En Power BI Desktop, los botones de navegación se usan con **Ctrl + clic**. En Power BI Service funcionan con un clic normal.

### Si la carpeta cambia de lugar

El parámetro `RutaDatos` apunta a `C:\Users\Administrador\Desktop\StreamView_Final\data\raw\`. En otro PC:
**Inicio → Transformar datos → Editar parámetros → RutaDatos** → escribe la ruta de tu carpeta `data\raw\`, terminada en `\` → **Actualizar**.

## Cómo abrirlo en VS Code

1. Instala **Visual Studio Code**.
2. Haz doble clic en **`StreamView.code-workspace`**, o en VS Code usa **Archivo → Abrir carpeta → StreamView**.
3. Cuando VS Code lo sugiera, instala las **extensiones recomendadas**:
   - **TMDL**: colorea el modelo de Power BI.
   - **Python** y **Jupyter**: para el notebook.
   - **Rainbow CSV**: para leer los datos.
   - **Markdown**: para este README.
4. Para las tareas listas, usa **Terminal → Ejecutar tarea…**:
   - *Abrir dashboard en Power BI*
   - *Instalar dependencias de Python*
   - *Regenerar KPIs de validación y gráficos*

## Páginas del dashboard

| # | Página                     | Audiencia                 | Pregunta de negocio                                  |
| - | --------------------------- | ------------------------- | ---------------------------------------------------- |
| 1 | Resumen Ejecutivo           | Directorio                | ¿Cómo está el catálogo hoy?                      |
| 2 | Catálogo                   | Contenidos y Adquisición | ¿Qué tenemos, de dónde viene y quién lo produce? |
| 3 | Popularidad y Valoración   | Marketing                 | ¿Qué contenidos conviene promocionar?              |
| 4 | Tendencias                  | Directorio y Producto     | ¿Cómo cambia la composición en el tiempo?         |
| 5 | Financiero Películas       | Directorio y Adquisición | ¿Qué películas rinden y con qué presupuesto?     |
| 6 | Hallazgos y Recomendaciones | Todos                     | ¿Qué decisiones tomar?                             |

Todas las páginas comparten los mismos **filtros sincronizados** (Tipo, Año, Género, País e Idioma), el botón **Limpiar filtros** y la navegación por botones. En Hallazgos, los botones **"Ver evidencia"** llevan al gráfico que respalda cada conclusión.

## Fuentes y reglas de transformación

Fuentes: `netflix_movies_detailed_up_to_2025.csv` y `netflix_tv_shows_detailed_up_to_2025.csv`, con 16.000 registros cada una. Todas las transformaciones se hacen en Power Query; los archivos originales no se modifican.

| # | Regla                                                                                                                                                |
| - | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Se unen películas y series. La clave `id_contenido` es `M-`/`T-` + `show_id`, porque 397 IDs se repiten entre los dos datasets              |
| 2 | Se eliminan 9 `show_id` duplicados en series, lo que deja 31.991 contenidos                                                                        |
| 3 | `rating` es idéntica a `vote_average`, así que no sirve como clasificación por edad. En su lugar se crea `segmento_valoracion`              |
| 4 | `duration` se excluye: está vacía en películas y en series siempre dice "1 Seasons"                                                             |
| 5 | Un título con 0 votos queda sin valoración, en vez de contar como nota 0. Los rankings usan una valoración ponderada bayesiana (m = 200)          |
| 6 | Los indicadores financieros sólo usan películas con presupuesto e ingresos de al menos USD 10.000 (3.492 películas). ROI = ingresos / presupuesto |
| 7 | Los géneros de películas y series se homologan a 22 géneros en español. Género, país, director y actor van en tablas puente                    |
| 8 | La popularidad de películas y series no se compara directamente. El KPI principal es la mediana                                                     |

## KPIs principales

| KPI                                                      | Valor (catálogo completo)            |
| -------------------------------------------------------- | ------------------------------------- |
| Total de contenidos / películas / series                | 31.991 / 16.000 / 15.991              |
| Países · idiomas · géneros                           | 147 · 83 · 22                       |
| Popularidad mediana                                      | 22,07                                 |
| Calificación promedio                                   | 6,63 (películas 6,31 · series 7,02) |
| % de títulos con nota ≥ 7                              | 42,0 %                                |
| Contenidos estrella                                      | 3.832 (12,0 %)                        |
| % contenido no inglés · asiático · iberoamericano    | 56,3 % · 31,2 % · 6,7 %             |
| ROI agregado · ROI mediano · % de películas rentables | 2,92x · 1,72x · 63,7 %              |

Las 60 medidas DAX están en `src/dax/` y en `dashboard/StreamView_EP2.SemanticModel/definition/tables/_Medidas.tmdl`.

## Principales hallazgos

1. **El catálogo se internacionaliza:** el inglés baja de 60,6 % a 54,9 % en las películas, y el contenido asiático y en español es más popular.
2. **Animación** es el único género de películas que es popular y bien evaluado a la vez, con un ROI mediano de 2,29x.
3. **Popular no es lo mismo que bien evaluado:** la correlación entre ambas es de 0,32.
4. **Las películas rinden 2,92x en conjunto,** pero el tramo de presupuesto de USD 5 a 20 M es el más riesgoso.

## Herramientas

Power BI Desktop (Power Query M, DAX, PBIP/TMDL) · Python 3 (pandas, matplotlib, Jupyter) · Visual Studio Code · GitHub
