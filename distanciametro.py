# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 10:28:55 2025

@author: Jorge Acín Zurita
"""

import pandas as pd
import numpy as np

# Leer archivos
estaciones = pd.read_excel("estaciones_valencia.xlsx")
propiedades = pd.read_excel("propiedades_valencia_2025.xlsx")

# Arreglar decimales
estaciones["Latitud"] = estaciones["Latitud"].astype(str).str.replace(",", ".").astype(float)
estaciones["Longitud"] = estaciones["Longitud"].astype(str).str.replace(",", ".").astype(float)
propiedades["latitude"] = propiedades["latitude"].astype(str).str.replace(",", ".").astype(float)
propiedades["longitude"] = propiedades["longitude"].astype(str).str.replace(",", ".").astype(float)

# Función rápida para calcular distancia entre coordenadas (Haversine)
def haversine_np(lat1, lon1, lat2, lon2):
    R = 6371000  # radio Tierra en metros
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

# Para cada propiedad, calcular la distancia a todas las estaciones y tomar la mínima
def calcular_min_distancia(propiedades_df, estaciones_df):
    min_distancias = []
    for i, row in propiedades_df.iterrows():
        dists = haversine_np(
            row["latitude"],
            row["longitude"],
            estaciones_df["Latitud"].values,
            estaciones_df["Longitud"].values
        )
        min_distancias.append(dists.min())
    return min_distancias

# Calcular y añadir columna
propiedades["distancia_min_estacion_m"] = calcular_min_distancia(propiedades, estaciones)

# Guardar resultado
propiedades.to_excel("propiedades_valencia_2025_con_distancia.xlsx", index=False)

