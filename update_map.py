import os
import requests
import json
from datetime import datetime, timedelta, timezone

# Список городов
CITY_DB = {
    'орск': [51.23, 58.46],
    'оренбург': [51.76, 55.09],
    'новороссийск': [44.71, 37.76],
    'краснодар': [45.04, 38.97],
    'сочи': [43.60, 39.72],
    'ростов-на-дону': [47.23, 39.72],
    'белгород': [50.59, 36.58],
    'курск': [51.73, 36.19],
    'воронеж': [51.67, 39.18]
}

def main():
    tz_orsk = timezone(timedelta(hours=5))
    current_time = datetime.now(tz_orsk).strftime("%H:%M")
    
    alerts = []
    for city, coords in CITY_DB.items():
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m,wind_speed_10m&wind_speed_unit=ms&timezone=auto"
            res = requests.get(url, timeout=5).json()
            temp = res['current']['temperature_2m']
            wind = res['current']['wind_speed_10m']
            
            # Если ветер > 10 м/с, считаем опасным (красный), иначе спокойным (зеленый)
            is_danger = wind > 10
            alerts.append({
                "coords": coords,
                "text": f"{city.upper()}: {temp}°C, Ветер {wind} м/с",
                "is_danger": is_danger
            })
        except:
            continue

    # Формируем HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>#map {{ height: 100vh; width: 100%; }}</style>
    </head>
    <body>
        <div style="position:absolute; top:10px; right:10px; z-index:1000; background:white; padding:10px;">
            Обновлено: {current_time}
        </div>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([48.0, 48.0], 5);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
            var data = {json.dumps(alerts)};
            data.forEach(function(item) {{
                L.circleMarker(item.coords, {{
                    color: item.is_danger ? 'red' : 'green',
                    radius: 8
                }}).addTo(map).bindPopup(item.text);
            }});
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    main()
    
