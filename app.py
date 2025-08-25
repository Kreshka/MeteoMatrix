from bs4 import BeautifulSoup
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium


st.markdown("""
    <style>
    .block-container {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 1180px !important;
    }
    .weather-text {
        display: inline-block;
        width: 150px;
        height: 150px;
        text-align: center;
        line-height: 140px; 
        font-size: 4rem !important;
        font-style: Courier New;
        border: 3px solid white !important;
        border-radius: 25px;
    }
    .weather-news {
        display: flex;
        width: 433px;
        height: 150px;
        font-size: 20px !important;
        font-style: Courier New;
        border: 3px solid white !important;
        border-radius: 25px;
        text-align: center;
        margin-right: 100px !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .moon-phase-text {
        display: inline-block;
        width: 150px;
        height: 150px;
        text-align: center;
        line-height: 140px; 
        font-size: 1rem !important;
        font-style: Courier New;
        border: 3px solid white !important;
        border-radius: 25px;
    }
    .pcol {
        display: flex;
        width: 52px;
        height: 150px;
        text-align: center;
        font-size: 1rem !important;
        font-style: Courier New;
        border: 3px solid white !important;
        border-radius: 15px;
        align-items: center !important;
        justify-content: center !important;
    }
    iframe {
        border-radius: 25px !important;
        border: 3px solid white !important;
    }
    .info-frame-text {
        display: flex;
        width: 140px;
        height: 140px;
        text-align: center;
        align-items: center !important;
        justify-content: center !important; 
        font-size: 1.5rem !important;
        font-style: Courier New;
        border: 3px solid white !important;
        border-radius: 25px;
    }
    .centered-title {
        text-align: center !important;
        font-size: 5rem !important;
        font-weight: bold !important;
        margin-bottom: 3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="centered-title">MeteoMatrix</div>', unsafe_allow_html=True)
def get_pos_by_place_name(place_name):
    url_for_cords = f"https://geocode-maps.yandex.ru/v1/?apikey=0c288416-3e87-4e76-ab53-b9dc30931908&geocode={place_name}&format=json"

    page = requests.get(url_for_cords)
    lon, lat = page.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
        "pos"].split()
    return lon, lat
def get_weather(place=None, pos=None):
    if pos is None:
        lon, lat = get_pos_by_place_name(place)
    else:
        lon, lat = pos

    url = f"https://yandex.ru/pogoda/ru/moscow?lat={lat}&lon={lon}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    sign = soup.find("span", class_="AppFactTemperature_sign__1MeN4").text
    value = soup.find("span", class_="AppFactTemperature_value__2qhsG").text
    news = soup.find("p", class_="AppFact_warning__8kUUn").text
    weather_week = soup.find_all("div", class_="AppShortForecastDay_container__r4hyT")
    datas = soup.find_all("p", class_="AppWellBeingCard_description__subtitle__ORKH4")
    facts = soup.find_all("li", class_="AppFact_details__item__QFIXI")
    return [sign, value, news, weather_week, datas, facts]


mcol1, mcol2 = st.columns([4, 4], gap="medium")


def visualize_weather(place=None, pos=None):
    weather = get_weather(place, pos)
    with mcol1:
        col1, col2 = st.columns([1, 3], gap="medium")
        with col1:
            st.markdown(f'<p class="weather-text">{weather[0]}{weather[1]}°</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="moon-phase-text">{weather[4][-1].text.capitalize()}</p>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<p class="weather-news">{weather[2]}</p>', unsafe_allow_html=True)
            pcols = st.columns(7, gap="medium")
            for num, col in enumerate(pcols):
                day = weather[3][num]
                one_day = BeautifulSoup(str(day), "html.parser")
                day_num = one_day.find("a", class_="AppLink_link___0246")
                wthr = one_day.find_all("span", class_="AppShortForecastDay_temperature__DV3oM")
                d1, d2, t1, t2 = day_num.text[:2], day_num.text[2:], wthr[0].text, wthr[1].text
                with col:
                    if d2 != "Сегодня":
                        st.markdown(f'<p class="pcol">{d1}\n{d2}\n{t1}\n{t2}</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="pcol">{d1}\n{t1}\n{t2}</p>', unsafe_allow_html=True)
        cols2 = st.columns(len(weather[5]), gap="medium")
        for num, col in enumerate(cols2):
            fct = weather[5][num].text
            with col:
                if fct[-1] == "°":
                    st.markdown(f'<p class="info-frame-text">t°C воды: {fct}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="info-frame-text">{fct}</p>', unsafe_allow_html=True)



# Создаем карту
with mcol2:
    m = folium.Map(location=[55.755863, 37.6177], zoom_start=10)
    map_data = st_folium(m, width=568, height=330)


    name = st.text_input("Введите любое место", "Москва2.0")
    if st.button("Показать погоду"):
        visualize_weather(place=name.title())
        m = folium.Map(location=get_pos_by_place_name(name.title()), zoom_start=10)
    elif map_data.get("last_clicked"):
        latt = map_data["last_clicked"]["lat"]
        lng = map_data["last_clicked"]["lng"]

        visualize_weather(pos=(lng, latt))

