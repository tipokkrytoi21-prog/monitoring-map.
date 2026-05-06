import os
import re
import requests
from datetime import datetime, timedelta

# Настройки
CHANNELS = ['monitoring_war', 'vanek_nikolaev'] # Добавь свои каналы сюда
KEYWORDS = ['пуск', 'бпла', 'взрыв', 'ракета', 'угроза', 'баллистика', 'вылет']
# Словарь координат для крупных городов (чтобы не нагружать систему поиском)
CITY_COORDS = {
    'Миллерово': [48.92, 40.39],
    'Ростов': [47.23, 39.72],
    'Орск': [51.23, 58.46],
    'Оренбург': [51.76, 55.09],
    'Белгород': [50.59, 36.58],
    'Курск': [51.73, 36.19],
    'Воронеж': [51.67, 39.18]
}

def get_coordinates(text):
    # Сначала ищем по словарю
    for city, coords in CITY_COORDS.items():
        if city.lower() in text.lower():
            return coords
    # Если города нет в словаре, ставим в центр РФ (заглушка)
    return [55.75, 37.61] 

def generate_map(alerts):
    # Шаблон HTML с поддержкой пульсации
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Мониторинг Карта</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            #map { height: 100vh; width: 100%; background: #1a1a1a; }
            body { margin: 0; }
            .pulsating-marker {
                background: red;
                border-radius: 50%;
                box-shadow: 0 0 0 rgba(255, 0, 0, 0.4);
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(255, 0, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([50.0, 40.0], 5);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

            var alerts = """ + str(alerts) + """;
            
            alerts.forEach(function(alert) {
                var markerOptions = {};
                // Если алерту меньше 60 минут - он пульсирует
                if (alert.is_new) {
                    var pulseIcon = L.divIcon({
                        className: 'pulsating-marker',
                        iconSize: [12, 12]
                    });
                    L.marker(alert.coords, {icon: pulseIcon}).addTo(map)
                        .bindPopup("<b>НОВАЯ УГРОЗА!</b><br>" + alert.text);
                } else {
                    L.circleMarker(alert.coords, {radius: 8, color: 'orange'}).addTo(map)
                        .bindPopup(alert.text);
                }
            });
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

# Имитация сбора данных (заменится на реальный парсинг позже)
def main():
    # Пример данных, которые мы "нашли"
    test_alerts = [
        {"coords": [48.92, 40.39], "text": "Миллерово - угроза БПЛА", "is_new": True},
        {"coords": [47.23, 39.72], "text": "Ростовская область - зафиксированы вылеты", "is_new": False},
        {"coords": [51.23, 58.46], "text": "Орск - метео-мониторинг", "is_new": False}
    ]
    generate_map(test_alerts)

if __name__ == "__main__":
    main()
    
