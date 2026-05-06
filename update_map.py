import requests
from bs4 import BeautifulSoup
import folium
from geopy.geocoders import Nominatim
import time

def run_final_monitor():
    # 1. Настройки и границы (GeoJSON)
    geojson_url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson'
    url = "https://t.me/s/lpr1_treugolnik"
    
    # 2. Сбор постов из Telegram
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    messages = soup.find_all('div', class_='tgme_widget_message_text')
    times = soup.find_all('time', class_='time')

    # 3. Создание темной карты (Dark Mode)
    m = folium.Map(location=[50, 40], zoom_start=5, tiles='CartoDB dark_matter')

    # Словарь регионов для закраски
    status_map = {}
    regions_dict = {
        'белгород': 'Belgorod Oblast', 'курск': 'Kursk Oblast', 
        'брянск': 'Bryansk Oblast', 'воронеж': 'Voronezh Oblast',
        'ростов': 'Rostov Oblast', 'крым': 'Republic of Crimea',
        'севастополь': 'Republic of Crimea', 'донецк': 'Donetsk Oblast',
        'луганск': 'Luhansk Oblast', 'запорож': 'Zaporizhia Oblast',
        'херсон': 'Kherson Oblast', 'оренбург': 'Orenburg Oblast'
    }

    # Анализ последних 30 сообщений для заливки областей
    for msg in messages[-30:]:
        text = msg.get_text().lower()
        color = "#f1c40f" # Желтый (опасность)
        if any(x in text for x in ['пуск', 'ракета', 'ракетная']): 
            color = "#c0392b" # Красный (ракеты)
        elif any(x in text for x in ['бпла', 'герань', 'беспилотник']): 
            color = "#e67e22" # Оранжевый (дроны)

        for key, geo_name in regions_dict.items():
            if key in text:
                status_map[geo_name] = color

    # 4. Отрисовка закрашенных регионов
    folium.GeoJson(
        geojson_url,
        style_function=lambda feature: {
            'fillColor': status_map.get(feature['properties']['name'], 'transparent'),
            'color': 'white', 'weight': 0.7, 'fillOpacity': 0.4,
        }
    ).add_to(m)

    # 5. Установка иконок (вспышки, ракеты)
    geo = Nominatim(user_agent="global_monitor_2026")
    for i, msg in enumerate(messages[-15:]):
        raw_text = msg.get_text()
        msg_time = times[i].get_text() if i < len(times) else ""
        
        words = [w.strip('.,!') for w in raw_text.split() if w and w[0].isupper() and len(w) > 4]
        for word in words:
            try:
                loc = geo.geocode(f"{word}, Russia", timeout=5)
                if loc and (43 < loc.latitude < 65):
                    icon_type, icon_color = 'info-sign', 'orange'
                    if 'пво' in raw_text.lower() or 'сбито' in raw_text.lower():
                        icon_type, icon_color = 'fire', 'red'
                    
                    folium.Marker(
                        location=[loc.latitude, loc.longitude],
                        popup=f"<b>{word}</b> [{msg_time}]<br>{raw_text[:150]}",
                        icon=folium.Icon(color=icon_color, icon=icon_type)
                    ).add_to(m)
                    time.sleep(0.3)
            except: continue

    # 6. HTML-шапка для авто-обновления и легенда
    header_html = '<meta http-equiv="refresh" content="300">' # Сайт будет сам обновляться каждые 5 мин
    m.get_root().header.add_child(folium.Element(header_html))

    legend_html = '''
     <div style="position: fixed; bottom: 30px; left: 30px; width: 220px; 
     background: rgba(30,30,30,0.9); color: white; border-radius: 8px;
     padding: 12px; z-index:9999; font-family: Arial; border: 1px solid #444;">
     <b style="font-size: 14px;">МОНИТОРИНГ КАРТА</b><br><br>
     <small><span style="color:#f1c40f;">●</span> Потенциальная опасность</small><br>
     <small><span style="color:#e67e22;">●</span> Фиксация БПЛА</small><br>
     <small><span style="color:#c0392b;">●</span> Ракетная угроза</small>
     </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save("index.html") # Результат сохраняется в index.html
    print("Файл index.html создан.")

if __name__ == "__main__":
    run_final_monitor()
  
