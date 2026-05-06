import os
import requests
from datetime import datetime

# Список городов и их точных координат
CITY_DB = {
    'миллерово': [48.92, 40.39],
    'морозовск': [48.35, 41.82],
    'ростов': [47.23, 39.72],
    'таганрог': [47.23, 38.89],
    'шахты': [47.70, 40.21],
    'новочеркасск': [47.42, 40.09],
    'каменск': [48.32, 40.26],
    'гуково': [48.06, 39.93],
    'орск': [51.23, 58.46],
    'оренбург': [51.76, 55.09],
    'белгород': [50.59, 36.58],
    'курск': [51.73, 36.19],
    'воронеж': [51.67, 39.18]
}

def generate_map(alerts):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Мониторинг Карта 2.0</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            #map { height: 100vh; width: 100%; background: #1a1a1a; }
            body { margin: 0; padding: 0; }
            .pulse {
                width: 15px; height: 15px;
                background: red; border-radius: 50%;
                box-shadow: 0 0 0 rgba(255, 0, 0, 0.4);
                animation: pulse-red 1.5s infinite;
            }
            @keyframes pulse-red {
                0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(255, 0, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
            }
            .update-time {
                position: absolute; bottom: 10px; left: 10px; z-index: 1000;
                background: rgba(0,0,0,0.7); color: white; padding: 5px 10px;
                font-family: sans-serif; font-size: 12px; border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="update-time">Обновлено: """ + datetime.now().strftime("%H:%M:%S") + """</div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([48.0, 40.0], 6);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

            var alerts = """ + str(alerts) + """;
            
            alerts.forEach(function(alert) {
                if (alert.is_new) {
                    var icon = L.divIcon({ className: 'pulse', iconSize: [15, 15] });
                    L.marker(alert.coords, {icon: icon}).addTo(map).bindPopup("<b>СРОЧНО:</b><br>" + alert.text);
                } else {
                    L.circleMarker(alert.coords, {radius: 7, color: 'orange', fillOpacity: 0.8}).addTo(map)
                        .bindPopup(alert.text);
                }
            });
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

def main():
    # Имитация сбора данных (здесь бот будет искать города в тексте)
    # Позже мы подключим сюда реальный парсер каналов
    raw_messages = [
        "Угроза БПЛА в районе Миллерово! Всем в укрытие.",
        "Ростовская область - работает ПВО",
        "Орск: мониторинг паводковой ситуации в норме",
        "Взрывы в районе города Морозовск"
    ]
    
    found_alerts = []
    for msg in raw_messages:
        for city, coords in CITY_DB.items():
            if city in msg.lower():
                is_urgent = any(word in msg.lower() for word in ['угроза', 'взрыв', 'бпла', 'сбито'])
                found_alerts.append({
                    "coords": coords,
                    "text": msg,
                    "is_new": is_urgent
                })
    
    generate_map(found_alerts)

if __name__ == "__main__":
    main()
    
