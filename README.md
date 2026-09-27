# Data Meets Home — Housing Price Prediction in Valencia

Analysis and prediction of housing prices in Valencia using data from [Idealista](https://www.idealista.com/) (2018 and 2025). It combines API scraping, data cleaning, exploratory analysis, district clustering and Machine Learning models.

📄 [Full Report: Data Meets Home](./docs/Memoria_Data_Meets_Home.pdf)

Project developed for the **Proyectos II** course in the second year of the Bachelor's Degree in Data Science at the Universitat Politècnica de València (UPV).

---

## Project Structure

```
├── data/
│   ├── Valencia_Sale.rda                    # Idealista 2018 dataset (~20.000 homes)
│   ├── propiedades_valencia.xlsx            # Idealista 2025 dataset (without metro distance)
│   ├── propiedades_valencia_2025.xlsx       # Idealista 2025 dataset (with metro distance)
│   ├── estaciones_metro.xlsx                # Metro/tram stations with coordinates
│   ├── barris.csv                           # Valencia neighbourhood polygons
│   ├── IPC.xlsx                             # Consumer Price Index (INE)
│   ├── IPV.xlsx                             # Housing Price Index (INE)
│   └── IPV_ComunidadValenciana.xlsx         # Housing Price Index for the Valencian Community (INE)
├── notebooks/
│   ├── 01_api_scraping.ipynb                # Extraction of homes for sale via the Idealista API (OAuth)
│   ├── 02_distancia_metro.ipynb             # Metro/tram stations (Overpass/OSM) + minimum Haversine distance
│   ├── 03_limpieza_2018.Rmd                 # 2018 dataset cleaning
│   ├── 04_limpieza_2025.Rmd                 # 2025 dataset cleaning
│   ├── 05_limpieza18_con_modelos.Rmd        # Predictive models (LR, RF, XGBoost, LightGBM)
│   └── 06_ajuste_ipv.Rmd                    # Temporal adjustment with the IPV
├── docs/
│   ├── Memoria_Data_Meets_Home.pdf
│   └── Presentacion_Data_Meets_Home.pdf
└── README.md
```

---

## Methodology

### 1. Data Collection

- **Idealista API**: Extraction of ~2.865 properties for sale in Valencia (2025) through the official API, using a custom Python script. The 2018 dataset (~20.000 listings) was obtained from a public repository in .RDA format.
- **Overpass API (OpenStreetMap)**: Retrieval of 100+ metro and tram station locations in the Valencia metropolitan area to compute the distance to the nearest public transport stop using the Haversine formula.
- **IPV (INE)**: Quarterly Housing Price Index from 2007 to 2024 for the Valencian Community.

### 2. Cleaning and Preparation

- Removal of duplicates and irrelevant variables.
- Parsing of nested JSON columns (priceInfo, detailedType, parkingSpace).
- Detection and treatment of anomalous values (multivariate PCA for outliers in 2025).
- Imputation of missing values in the floor variable (median).
- Feature engineering: bedrooms/bathrooms ratio, discretized price ranges, minimum distance to a metro station, unified `status` variable, one-hot encoding of districts.

### 3. Exploratory Analysis (Objective 1)

Compare how the influence of a home's features on its price changed between 2018 and 2025:

- **PCA**: Physical features (floor area, bedrooms, bathrooms) are the main contributors to price in both years. Location variables point in the opposite direction.
- **Pearson correlations**: Built area goes from a correlation of 0,76 (2018) to 0,58 (2025) with price — it is still the most influential variable but loses strength.
- **Conclusion**: The market is moving towards a more complex model where size alone is no longer enough; functional layout, accessibility and centrality gain weight.

<p align="center">
  <img src="https://github.com/user-attachments/assets/b416fcd9-465e-4b70-997f-a4b941fbf705" width="800" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/753bff7f-f65d-44ec-b367-89a52e28cb37" width="800" alt="PCA plots 2018 and 2025" />
</p>

### 4. District Clustering (Objective 2)

Study the evolution of housing prices by district:

- Price was discretized into 3 ranges (Cheap / Medium / Expensive) with thresholds adapted to each year.
- K-Means clustering: **5 clusters in 2018**, **4 in 2025** — the market has simplified into more clearly defined profiles.
- Central districts such as Ciutat Vella and L'Eixample show clear signs of **gentrification**.
- The median price almost doubled: **€148.000 (2018) → €330.000 (2025)**.

<p align="center">
  <img src="https://github.com/user-attachments/assets/d4bc5f74-1a8d-4a3a-83c7-d176fa2f25ba" width="800" alt="Valencia clustering" />
</p>

### 5. Predictive Models (Objective 3)

Find the best model to predict the price of a home in Valencia using 2018 data:

| Model | RMSE (€) | MAE (€) | R² | Notes |
|---|---|---|---|---|
| Linear Regression | 100.403 | 60.232 | 0,671 | Baseline |
| Random Forest (initial) | 67.661 | 32.814 | 0,851 | Substantial improvement over LR |
| Random Forest (tuned) | 66.644 | 32.860 | 0,856 | Hyperparameter tuning |
| XGBoost | 70.005 | 34.859 | 0,840 | Good performance, does not beat RF |
| LightGBM | 72.355 | 39.015 | 0,829 | Similar to XGBoost |
| RF (filtered + log)¹ | 38.747 | 25.343 | 0,836 | P95 + LOGPRICE |

¹ **Not directly comparable with the others:** this model was trained and evaluated excluding the 5% most expensive homes (95th percentile), while the others were evaluated on the full data. Its lower RMSE/MAE is largely due to removing extreme prices, which are the ones that generate the most error. In addition, its R² (0,836) is lower than that of the tuned Random Forest (0,856).

On the full dataset, the best model is the **tuned Random Forest** (R² 0,856, MAE €32.860). The variant with log transformation and 95th-percentile filtering reduces the MAE to €25.343, but it only applies to the 95% of lowest-priced homes. The most important variables: built area (25,6%), number of bathrooms (21,1%), distance to the city centre (15,9%) and elevator (10,2%).

Cluster-segmented models (5 and 2 clusters) were also tested, but none outperformed the global model.

<p align="center">
  <img src="https://github.com/user-attachments/assets/3e6f2e19-ddbf-420e-ba73-c863e07caf93" width="900" alt="Random Forest variable importance and scatter plot" />
</p>

### 6. Temporal Adjustment with the IPV (Objective 4)

Assess whether the 2018 model can predict 2025 prices and correct the time gap:

| Scenario | RMSE (€) | MAE (€) | R² |
|---|---|---|---|
| 2018 model → 2025 data (uncorrected) | 317.013 | 213.572 | 0,676 |
| 2018 model → 2025 data (IPV-corrected ×1,5) | 235.324 | 144.677 | 0,676 |

The IPV correction reduces the mean absolute error by ~€69.000, confirming that the model's structure is valid but needs temporal recalibration. The remaining error is due to the inherent complexity of predicting prices 7 years apart.

---

## Technologies

**R**: dplyr · ggplot2 · caret · randomForest · xgboost · lightgbm · sf · leaflet · FactoMineR · factoextra · NbClust · corrplot · readxl · jsonlite · tidyr

**Python**: requests · pandas · numpy · openpyxl

---

## Detailed Reports (RPubs)

- [2018 Cleaning](https://rpubs.com/mcmihala/limpieza2018)
- [2025 Cleaning](https://rpubs.com/roberttorres/1315191)
- [Clustering](https://rpubs.com/mcmihala/1315148)
- [Predictive Models](https://rpubs.com/cachupinto/1315184)
- [IPV Adjustment](https://rpubs.com/roberttorres/1315187)

---

## Reproduction

1. Clone the repository.
2. Install the R and Python dependencies.
3. Run the notebooks in numerical order (`01_` → `06_`).

> **Note:** The `01_api_scraping.ipynb` notebook requires your own Idealista API credentials, set in the `IDEALISTA_API_KEY` and `IDEALISTA_API_SECRET` environment variables. The processed data is already available in `data/`.

---

## Team

| Member | Contribution |
|---|---|
| **Jorge Acín Zurita** | 2018 cleaning, training/evaluation/selection of predictive models, metro distances |
| Robert Torres Mingarro | 2018 cleaning, IPV prediction adjustment, submissions |
| Mihai Cristian Mihalache Farcas | 2025 cleaning, exploratory analysis, data scraping, clustering |
| Rubén Tormo Piles | 2025 cleaning, exploratory analysis, data scraping, clustering |

---

Academic project — Bachelor's Degree in Data Science, Universitat Politècnica de València (UPV).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-jorgeacin-blue?logo=linkedin)](https://linkedin.com/in/jorgeacin)
[![GitHub](https://img.shields.io/badge/GitHub-JorgeAcin-black?logo=github)](https://github.com/JorgeAcin)
