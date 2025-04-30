import requests

# Bounding box más amplia: sur, oeste, norte, este
# Abarca Torrent, Alboraia, Picanya, etc.
query = """
[out:json][timeout:60];
(
  node["railway"="station"](39.3, -0.5, 39.6, -0.25);
  node["railway"="tram_stop"](39.3, -0.5, 39.6, -0.25);
);
out body;
"""

# Enviar consulta a Overpass
response = requests.post("http://overpass-api.de/api/interpreter", data={"data": query})
data = response.json()

# Procesar los resultados
stations = []
for element in data["elements"]:
    name = element.get("tags", {}).get("name", "Desconocido")
    lat = element["lat"]
    lon = element["lon"]
    stations.append((name, lat, lon))

# Mostrar los primeros resultados
for s in stations[:20]:
    print(f"{s[0]} - {s[1]} - {s[2]}")

print(f"\nTotal estaciones encontradas: {len(stations)}")

import csv

with open("estaciones_valencia.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Nombre", "Latitud", "Longitud"])
    for s in stations:
        writer.writerow(s)



