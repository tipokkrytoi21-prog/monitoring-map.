import os
import requests
import json
import subprocess

# Список городов
cities = {
    'Orsk': [51.23, 58.46],
    'Orenburg': [51.76, 55.09],
    'Krasnodar': [45.04, 38.97]
}

def main():
    # 1. Собираем данные
    markers = []
    for name, coords in cities.items():
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m&wind_speed_unit=ms"
            res = requests.get(url, timeout=5).json()
            temp = res['current']['temperature_2m']
            markers.append({"coords": coords, "name": f"{name}: {temp}°C"})
        except:
            markers.append({"coords": coords, "name": f"{name}: No data"})

    # 2. Генерируем HTML
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
    
    # 3. Сохраняем файл
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 4. Автоматически отправляем в репозиторий
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", "index.html"], check=True)
        # Коммит только если есть изменения
        result = subprocess.run(["git", "commit", "-m", "Auto-update map"], capture_output=True)
        if result.returncode == 0:
            subprocess.run(["git", "push"], check=True)
            print("Карта успешно обновлена и отправлена в репозиторий.")
        else:
            print("Изменений нет, ничего не отправляем.")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

if __name__ == "__main__":
    main()
    
