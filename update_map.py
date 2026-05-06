import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# НАСТРОЙКИ КАНАЛОВ
CHANNELS = ['lpr1_treugolnik', 'monitoring_war', 'vanek_nikolaev'] 

# БАЗА ГОРДОВ (Координаты)
CITY_DB = {
    'миллерово': [48.92, 40.39],
    'морозовск': [48.35, 41.82],
    'ростов': [47.23, 39.72],
    'таганрог': [47.23, 38.89],
    'шахты': [47.70, 40.21],
    'новошахтинск': [47.76, 39.94],
    'каменск': [48.32, 40.26],
    'гуково': [48.06, 39.93],
    'донецк рф': [48.33, 39.94],
    'орск': [51.23, 58.46],
    'оренбург': [51.76, 55.09],
    'белгород': [50.59, 36.58],
    'курск': [51.73, 36.19]
}

def get_telegram_data(channel):
    alerts = []
    try:
        # Используем RSS мост для чтения постов
        url = f"https://rsshub.app/telegram/channel/{channel}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text or ""
                description = item.find('description').text or ""
                full_text = (title + " " + description).lower()
                
                for city, coords in CITY_DB.items():
                    if city in full_text:
                        # Проверка на срочность
                        is_urgent = any(word in full_text for word in ['угроза', 'взрыв', 'бпла', 'ракет', 'пуск', 'пво', 'внимание', 'тревога'])
                        alerts.append({
                            "coords": coords,
                            "text": f"<b>{city.upper()}</b>: {title[:80]}...", 
                            "is_new": is_urgent
                        })
    except Exception as e:
        print(f"Ошибка канала {channel}: {e}")
    return alerts

def generate_map(alerts):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LIVE Мониторинг</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            #map { height: 100vh; width: 100%; background: #111; }
            body { margin: 0; padding: 0; }
            .pulse {
                width: 18px; height: 18px;
                background: #ff0000; border-radius: 50%;
                box-shadow: 0 0 0 rgba(255, 0, 0, 0.4);
                animation: pulse-red 1.2s infinite;
                border: 2px solid white;
            }
            @keyframes pulse-red {
                0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
                70% { box-shadow: 0 0 0 20px rgba(255, 0, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
            }
            .update-tag {
                position: absolute; top: 10px; right: 10px; z-index: 1000;
                background: rgba(255, 255, 255, 0.9); padding: 5px 10px;
                border-radius: 20px; font-family: sans-serif; font-weight: bold; font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="update-tag">ОБНОВЛЕНО: """ + datetime.now().strftime("%H:%M") + """</div>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([48.5, 39.5], 7);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

            var alerts = """ + str(alerts) + """;
            alerts.forEach(function(alert) {
                if (alert.is_new) {
                    var icon = L.divIcon({ className: 'pulse', iconSize: [18, 18] });
                    L.marker(alert.coords, {icon: icon}).addTo(map).bindPopup(alert.text);
                } else {
                    L.circleMarker(alert.coords, {radius: 8, color: '#ffa500', fillOpacity: 0.7}).addTo(map).bindPopup(alert.text);
                }
            });
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

def main():
    all_alerts = []
    for chan in CHANNELS:
        all_alerts.extend(get_telegram_data(chan))
    
    if not all_alerts:
        # Заглушка, чтобы карта не была пустой при запуске
        all_alerts.append({"coords": [48.92, 40.39], "text": "Связь установлена. Ожидаем данные из каналов...", "is_new": False})
        
    generate_map(all_alerts)

if __name__ == "__main__":
    main()
    
