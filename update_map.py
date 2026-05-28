import requests
import json

cities = {
    'Orsk': [51.23, 58.46],
    'Orenburg': [51.76, 55.09],
    'Krasnodar': [45.04, 38.97]
}

def main():
    markers = []
    for name, coords in cities.items():
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m&wind_speed_unit=ms"
            res = requests.get(url, timeout=5).json()
            temp = res['current']['temperature_2m']
            markers.append({"coords": coords, "name": f"{name}: {temp}°C"})
        except:
            markers.append({"coords": coords, "name": f"{name}: No data"})

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>#map {{ height: 100vh; width: 100%; }}</style>
    </head>
    <body>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([50.0, 50.0], 4);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
            var data = {json.dumps(markers)};
            data.forEach(function(item) {{
                L.marker(item.coords).addTo(map).bindPopup(item.name);
            }});
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    main()
    
