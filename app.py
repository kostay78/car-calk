import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime

# Настройка страницы
st.set_page_config(page_title="EV Calc 2026 Pro", page_icon="⚡")

# --- ФУНКЦИЯ С НОВЫМ ИМЕНЕМ (СБРОС КЭША) ---
@st.cache_data(ttl=600) # Кэш на 10 минут
def fetch_fuel_prices():
    # Стандартный набор данных (всегда под рукой)
    default_prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    
    try:
        url = "https://petrolplus.ru/fuel_prices/sankt-peterburg/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            new_prices = default_prices.copy()
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    name = cols[0].text.strip()
                    try:
                        val = float(cols[1].text.strip().replace(',', '.'))
                        if "92" in name: new_prices["АИ-92"] = val
                        if "95" in name: new_prices["АИ-95"] = val
                        if "Дизель" in name: new_prices["Дизель"] = val
                    提取except: continue
            return new_prices, True
    except:
        pass
    
    # Если что-то пошло не так, возвращаем базу
    return default_prices, False

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
st.title("⚡ EV Calc 2026: Динамические данные")

# БЕЗОПАСНЫЙ ВЫЗОВ (Защита 43-й строки)
try:
    current_prices, is_live = fetch_fuel_prices()
except:
    current_prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    is_live = False

if is_live:
    st.success(f"✅ Цены обновлены из сети ({datetime.date.today()})")
else:
    st.warning("⚠️ Режим офлайн: используются данные 2026 года")

# --- БЛОК ВВОДА ---
st.header("1. Исходные данные")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Автомобиль с ДВС")
    fuel_type = st.selectbox("Тип топлива", list(current_prices.keys()))
    fuel_price = st.number_input("Цена за литр (руб)", value=current_prices.get(fuel_type, 71.50))
    price_ice = st.number_input("Цена покупки (руб)", value=2200000, step=50000)
    cons_ice = st.number_input("Расход топлива (л/100 км)", value=8.5)

with col2:
    st.subheader("🔋 Электромобиль")
    price_ev = st.number_input("Цена покупки ЭД (руб)", value=3600000, step=50000)
    cons_ev = st.number_input("Расход энергии (кВт*ч/100 км)", value=18.0)
    elec_price = st.number_input("Тариф ЭЭ (руб/кВт*ч)", value=3.85)

st.divider()
annual_km = st.slider("Годовой пробег (км)", 5000, 100000, 20000)

# --- РАСЧЕТ ---
cost_1km_ice = (cons_ice / 100) * fuel_price
cost_1km_ev = (cons_ev / 100) * elec_price
annual_saving = (cost_1km_ice - cost_1km_ev) * annual_km
price_diff = price_ev - price_ice

if st.button("РАССЧИТАТЬ", type="primary"):
    if annual_saving > 0:
        payback = price_diff / annual_saving
        st.metric("Срок окупаемости", f"{round(payback, 1)} лет")
        st.write(f"Экономия в год: **{round(annual_saving):,} руб.**")
    else:
        st.error("Электромобиль не окупится.")
        
