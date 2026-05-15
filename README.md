# Data Meets Home — Predicción de Precios de Vivienda en Valencia

Análisis y predicción de precios de vivienda en Valencia utilizando datos de [Idealista](https://www.idealista.com/) (2018 y 2025). Combina scraping de APIs, limpieza de datos, análisis exploratorio, clustering de distritos y modelos de Machine Learning.

📄 [Haz clic aquí para ver la Memoria Completa (PDF)](./docs/Memoria_Data_Meets_Home.pdf)

Proyecto desarrollado en la asignatura **Proyectos II** del tercer curso del Grado en Ciencia de Datos de la Universitat Politècnica de València (UPV).

---

## Estructura del Proyecto

```
├── data/
│   ├── Valencia_Sale.rda                    # Dataset Idealista 2018 (~20.000 viviendas)
│   ├── propiedades_valencia.xlsx            # Dataset Idealista 2025 (sin distancia metro)
│   ├── propiedades_valencia_2025.xlsx       # Dataset Idealista 2025 (con distancia metro)
│   ├── estaciones_metro.xlsx                # Estaciones de metro/tranvía con coordenadas
│   ├── barris.csv                           # Polígonos de barrios de Valencia
│   ├── IPC.xlsx                             # Índice de Precios de Consumo (INE)
│   ├── IPV.xlsx                             # Índice de Precios de Vivienda (INE)
│   └── IPV_ComunidadValenciana.xlsx         # IPV específico Comunidad Valenciana (INE)
├── notebooks/
│   ├── 01_api_scraping.py                   # Extracción de estaciones OSM + cálculo
│   ├── 02_distancia_metro.py                # Extracción de estaciones OSM + cálculo Haversine
│   ├── 03_limpieza_2018.Rmd                 # Limpieza dataset 2018
│   ├── 04_limpieza_2025.Rmd                 # Limpieza dataset 2025
│   ├── 05_limpieza18_con_modelos.Rmd        # Modelos predictivos (LR, RF, XGBoost, LightGBM)
│   └── 06_ajuste_ipv.Rmd                    # Ajuste temporal con IPV
├── docs/
│   ├── Memoria_Data_Meets_Home.pdf
│   └── Presentacion_Data_Meets_Home.pdf
└── README.md
```

---

## Metodología

### 1. Obtención de Datos

- **API de Idealista**: Extracción de ~2.865 propiedades en venta en Valencia (2025) mediante la API oficial, con un script Python propio. El dataset de 2018 (~20.000 anuncios) se obtuvo de un repositorio público en formato .RDA.
- **API de Overpass (OpenStreetMap)**: Obtención de 100+ ubicaciones de estaciones de metro y tranvía en el área metropolitana de Valencia para calcular la distancia al transporte público más cercano mediante la fórmula de Haversine.
- **IPV (INE)**: Índice de Precios de la Vivienda por trimestre desde 2007 hasta 2024 para la Comunidad Valenciana.

### 2. Limpieza y Preparación

- Eliminación de duplicados y variables irrelevantes.
- Parsing de columnas JSON anidadas (priceInfo, detailedType, parkingSpace).
- Detección y tratamiento de valores anómalos (PCA multivariante para outliers en 2025).
- Imputación de valores faltantes en la variable planta (mediana).
- Feature engineering: ratio habitaciones/baños, rangos de precio discretizados, distancia mínima a estación de metro, variable `status` unificada, one-hot encoding de distritos.

### 3. Análisis Exploratorio (Objetivo 1)

Comparar cómo ha cambiado la influencia de las características de una vivienda sobre su precio entre 2018 y 2025:

- **PCA**: Las características físicas (superficie, habitaciones, baños) son los principales contribuyentes al precio en ambos años. Las variables de ubicación muestran dirección opuesta.
- **Correlaciones de Pearson**: La superficie construida pasa de una correlación de 0.76 (2018) a 0.58 (2025) con el precio — sigue siendo la más influyente pero pierde fuerza.
- **Conclusión**: El mercado evoluciona hacia un modelo más complejo donde ya no basta con el tamaño; la distribución funcional, la accesibilidad y la centralidad ganan peso.

### 4. Clustering de Distritos (Objetivo 2)

Estudiar la evolución del precio de la vivienda por distrito:

- Se discretizó el precio en 3 rangos (Barato / Medio / Caro) con umbrales adaptados a cada año.
- Clustering con K-Means: **5 clústeres en 2018**, **4 en 2025** — el mercado se ha simplificado en perfiles más definidos.
- Distritos centrales como Ciutat Vella y L'Eixample muestran claros signos de **gentrificación**.
- La mediana de precio casi se duplicó: **€148.000 (2018) → €330.000 (2025)**.

### 5. Modelos Predictivos (Objetivo 3)

Encontrar el mejor modelo para predecir el precio de una vivienda en Valencia con datos de 2018:

| Modelo | RMSE (€) | MAE (€) | R² | Notas |
|---|---|---|---|---|
| Regresión Lineal | 100.403 | 60.232 | 0,671 | Baseline |
| Random Forest (inicial) | 67.661 | 32.814 | 0,851 | Mejora sustancial sobre LR |
| Random Forest (optimizado) | 66.644 | 32.860 | 0,856 | Ajuste de hiperparámetros |
| XGBoost | 70.005 | 34.859 | 0,840 | Buen rendimiento, no supera RF |
| LightGBM | 72.355 | 39.015 | 0,829 | Similar a XGBoost |
| **RF (filtrado + log)** | **38.747** | **25.343** | **0,836** | **Mejor modelo — P95 + LOGPRICE** |

El modelo ganador usa **Random Forest con transformación logarítmica del precio y filtrado del percentil 95**, consiguiendo el menor MAE (€25.343). Las variables más importantes: superficie construida (25,6%), nº de baños (21,1%), distancia al centro (15,9%) y ascensor (10,2%).

También se probaron modelos segmentados por clústeres (5 y 2 clústeres), pero ninguno superó al modelo global.

### 6. Ajuste Temporal con IPV (Objetivo 4)

Evaluar si el modelo de 2018 puede predecir precios de 2025 y corregir el desfase:

| Escenario | RMSE (€) | MAE (€) | R² |
|---|---|---|---|
| Modelo 2018 → datos 2025 (sin corregir) | 317.013 | 213.572 | 0,676 |
| Modelo 2018 → datos 2025 (corregido IPV ×1,5) | 235.324 | 144.677 | 0,676 |

La corrección con el IPV reduce el error medio absoluto en ~€69.000, confirmando que la estructura del modelo es válida pero necesita recalibración temporal. El error residual se debe a la complejidad inherente de predecir precios con 7 años de diferencia.

---

## Tecnologías

**R**: dplyr · ggplot2 · caret · randomForest · xgboost · lightgbm · sf · leaflet · FactoMineR · factoextra · NbClust · corrplot · readxl · jsonlite · tidyr

**Python**: requests · pandas · numpy · openpyxl

---

## Informes Detallados (RPubs)

- [Limpieza 2018](https://rpubs.com/mcmihala/limpieza2018)
- [Limpieza 2025](https://rpubs.com/roberttorres/1315191)
- [Clustering](https://rpubs.com/mcmihala/1315148)
- [Modelos Predictivos](https://rpubs.com/cachupinto/1315184)
- [Ajuste IPV](https://rpubs.com/roberttorres/1315187)

---

## Reproducción

1. Clonar el repositorio.
2. Instalar las dependencias de R y Python.
3. Ejecutar los notebooks en orden numérico (`01_` → `06_`).

> **Nota:** El notebook `01_api_scraping.ipynb` requiere credenciales propias de la API de Idealista. Los datos ya procesados están en `data/`.

---

## Equipo

| Miembro | Contribución |
|---|---|
| **Jorge Acín Zurita** | Limpieza 2018, entrenamiento/evaluación/selección de modelos predictivos, distancias al metro |
| Robert Torres Mingarro | Limpieza 2018, ajuste de predicciones con IPV, entregas |
| Mihai Cristian Mihalache Farcas | Limpieza 2025, análisis exploratorio, scraping de datos, clustering |
| Rubén Tormo Piles | Limpieza 2025, análisis exploratorio, scraping de datos, clustering |

---

Proyecto académico — Grado en Ciencia de Datos, Universitat Politècnica de València (UPV).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jorgeacin-blue?logo=linkedin)](https://linkedin.com/in/jorgeacin)
[![GitHub](https://img.shields.io/badge/GitHub-JorgeAcin-black?logo=github)](https://github.com/JorgeAcin)
