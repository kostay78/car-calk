import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime

# Настройка страницы
st.set_page_config(page_title="EV Calc 2026 Pro", page_icon="⚡")

@st.cache_data(ttl=3600)
def get_live_fuel_data():
    # Базовые цены (на всякий случай)
    prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    
    try:
        # Пробуем альтернативный источник (Мониторинг цен)
        url = "https://fuelprices.ru/st-petersburg"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Ищем все ячейки таблицы
            tds = soup.find_all('td')
            for i in range(len(tds)):
                text = tds[i].get_text()
                if "95" in text and i+1 < len(tds):
                    val = tds[i+1].get_text().strip().replace(',', '.')
                    prices["АИ-95"] = float(''.join(re.findall(r"\d+\.\d+", val)) or 71.50)
                if "92" in text and i+1 < len(tds):
                    val = tds[i+1].get_text().strip().replace(',', '.')
                    prices["АИ-92"] = float(''.join(re.findall(r"\d+\.\d+", val)) or 65.80)
            return prices, True
    except:
        pass
    return prices, False

import re # Добавляем для очистки текста от лишних символов

# --- ИНТЕРФЕЙС ---
st.title("⚡ EV Calc 2026: Честный расчет")

current_prices, is_live = get_live_fuel_data()

if is_live:
    st.success(f"✅ Данные получены из сети в реальном времени ({datetime.date.today()})")
else:
    # Если даже этот сайт забанит, мы честно об этом скажем
    st.info("ℹ️ Сейчас используются усредненные данные по региону (автономный режим)")

# --- ДАЛЬШЕ ТВОЙ КОД РАСЧЕТОВ ---
st.header("1. Ввод параметров")
c1, c2 = st.columns(2)

with c1:
    st.subheader("🚗 Бензин")
    fuel_type = st.selectbox("Тип", list(current_prices.keys()))
    f_price = st.number_input("Цена за литр", value=current_prices[fuel_type])
    p_ice = st.number_input("Цена авто", value=2200000)
    cons_i = st.number_input("Расход", value=8.5)

with c2:
    st.subheader("🔋 Электро")
    p_ev = st.number_input("Цена ЭД", value=3600000)
    cons_e = st.number_input("Расход кВт", value=18.0)
    e_price = st.number_input("Тариф ЭЭ", value=3.85)

km = st.slider("Пробег в год", 5000, 100000, 20000)

if st.button("РАССЧИТАТЬ", type="primary"):
    diff = p_ev - p_ice
    save = ((cons_i/100 * f_price) - (cons_e/100 * e_price)) * km
    
    if save > 0:
        years = diff / save
        st.balloons() # Эффект праздника при расчете
        st.metric("Окупится через", f"{round(years, 1)} лет")
        st.write(f"Ваша чистая экономия: **{round(save):,}** руб/год".replace(',', ' '))
    else:
        st.error("При таких ценах электромобиль не выгоднее бензина.")
        
