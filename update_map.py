import os
import requests
from datetime import datetime, timedelta, timezone

# РАСШИРЕННАЯ БАЗА ГОРОДОВ (Координаты: [широта, долгота])
CITY_DB = {
    # Твой регион и Оренбуржье
    'орск': [51.23, 58.46],
    'оренбург': [51.76, 55.09],
    
    # Юг России
    'новороссийск': [44.71, 37.76],
    'темрюк': [45.26, 37.38],
    'краснодар': [45.04, 38.97],
    'сочи': [43.60, 39.72],
    'ростов-на-дону': [47.23, 39.72],
    'таганрог': [47.23, 38.89],
    
    # Приграничные и центральные регионы
    'белгород': [50.59, 36.58],
    'курск': [51.73, 36.19],
    'брянск': [53.25, 34.37],
    'воронеж': [51.67, 39.18],
    'москва': [55.75, 37.61],
    'донецк': [48.01, 37.80]
}

def get_weather_alerts():
    """Получает данные о погодных опасностях и аномалиях"""
    alerts = []
    
    for city, coords in CITY_DB.items():
        try:
            # Запрашиваем текущую погоду и экстренные параметры
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m,wind_speed_10m,weather_code&wind_speed_unit=ms&timezone=auto"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('current', {})
                temp = data.get('temperature_2m', 0)
                wind = data.get('wind_speed_10m', 0)
                code = data.get('weather_code', 0)
                
                is_danger = False
                reasons = []
                
                # Критерии опасности (Шторм, Аномальный зной/мороз, ливни)
                if wind >= 15: # Штормовой ветер
                    is_danger = True
                    reasons.append(f"Штормовой ветер ({wind} м/с)")
                if temp >= 38: # Аномальная жара
                    is_danger = True
                    reasons.append(f"Аномальная жара ({temp}°C)")
                if temp <= -30: # Экстремальный мороз
                    is_danger = True
                    reasons.append(f"Сильный мороз ({temp}°C)")
                
                # Коды сильной непогоды (Гроза, град, ливень)
                if code in [65, 67, 75, 82, 86, 95, 96, 99]:
                    is_danger = True
                    reasons.append("Опасные осадки / Гроза")

                if is_danger:
                    # Маркер для реальной угрозы
                    alerts.append({
                        "coords": coords,
                        "text": f"<b>{city.upper()}</b>:<br>⚠️ ОБЪЯВЛЕНА УГРОЗА!<br>Причина: {', '.join(reasons)}",
                        "is_new": True
                    })
                else:
                    # Обстановка стабильная, но мониторинг идет
                    alerts.append({
                        "coords": coords,
                        "text": f"<b>{city.upper()}</b>:<br>Обстановка под контролем.<br>Температура: {temp}°C, Ветер: {wind} м/с",
                        "is_new": False
                    })
                    
        except Exception as e:
            print(f"Ошибка проверки города {city}: {e}")
            
    return alerts

def generate_map(alerts):
    # Принудительно выставляем часовой пояс UTC+5 (Орск / Екатеринбург)
    tz_orsk = timezone(timedelta(hours=5))
    current_time = datetime.now(tz_orsk).strftime("%H:%M")

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LIVE Мониторинг Опасностей РФ</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            #map { height: 100vh; width: 100%; background: #111; }
            body { margin: 0; padding: 0; }
            .pulse {
                width: 18px; height: 18px;
                background: #ff3333; border-radius: 50%;
                box-shadow: 0 0 0 rgba(255, 51, 51, 0.4);
                animation: pulse-red 1.2s infinite;
                border: 2px solid white;
            }
            @keyframes pulse-red {
                0% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(255, 51, 51, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0); }
            }
            .update-tag {
                position: absolute; top: 10px; right: 10px; z-index: 1000;
                background: rgba(20, 20, 20, 0.85); color: #fff; padding: 6px 12px;
                border-radius: 20px; font-family: sans-serif; font-weight: bold; font-size: 12px;
                border: 1px solid #333; box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            }
        </style>
    </head>
    <body>
        <div class="update-tag">ОБНОВЛЕНО: """ + current_time + """</div>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            // Центрируем карту между Югом и Уралом
            var map = L.map('map').setView([48.0, 48.0], 5);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

            var alerts = """ + str(alerts) + """;
            alerts.forEach(function(alert) {
                if (alert.is_new) {
                    // 1. Рисуем большую полупрозрачную красную зону опасности (радиус 70 км)
                    L.circle(alert.coords, {
                        radius: 70000,
                        color: '#ff3333',
                        fillColor: '#ff3333',
                        fillOpacity: 0.25,
                        weight: 2
                    }).addTo(map).bindPopup(alert.text);

                    // 2. Ставим в центр зоны мигающий маркер-пульсар
                    var icon = L.divIcon({ className: 'pulse', iconSize: [18, 18] });
                    L.marker(alert.coords, {icon: icon}).addTo(map).bindPopup(alert.text);
                } else {
                    // Зеленая точка, когда обстановка спокойная
                    L.circleMarker(alert.coords, {
                        radius: 6, 
                        color: '#22c55e', 
                        fillColor: '#22c55e',
                        fillOpacity: 0.6,
                        weight: 1
                    }).addTo(map).bindPopup(alert.text);
                }
            });
        </script>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

def main():
    print("Запуск мониторинга опасных зон...")
    all_alerts = get_weather_alerts()
    
    if not all_alerts:
        all_alerts.append({"coords": [51.23, 58.46], "text": "Система работает. Опасностей не обнаружено.", "is_new": False})
        
    generate_map(all_alerts)
    print("Карта успешно обновлена!")

if __name__ == "__main__":
    main()
    
