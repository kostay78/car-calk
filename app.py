import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import re

# Настройка страницы
st.set_page_config(page_title="EV Calc 2026 Pro", page_icon="⚡")

# --- ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ЦЕН С НОВОГО САЙТА ---
@st.cache_data(ttl=600) # Кэшируем на 10 минут
def fetch_fuel_prices():
    # Базовые цены на 2026 год (наш запасной план)
    default_prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    
    try:
        # Используем более простой сайт для парсинга
        url = "https://www.benzin-price.ru/price_fuel.php?region_id=78"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table', class_='probel')
            
            new_prices = default_prices.copy()
            for table in tables:
                text = table.get_text()
                # Ищем цены с помощью регулярных выражений
                if "АИ-95" in text or "95" in text:
                    match = re.search(r'(\d{2}[\.,]\d{2})', text)
                    if match: new_prices["АИ-95"] = float(match.group(1).replace(',', '.'))
                if "АИ-92" in text or "92" in text:
                    match = re.search(r'(\d{2}[\.,]\d{2})', text)
                    if match: new_prices["АИ-92"] = float(match.group(1).replace(',', '.'))
                if "Дизель" in text:
                    match = re.search(r'(\d{2}[\.,]\d{2})', text)
                    if match: new_prices["Дизель"] = float(match.group(1).replace(',', '.'))
            
            return new_prices, True # Если всё супер, возвращаем цены и статус True
    except:
        pass # Если любая ошибка сети - просто идем дальше
    
    # Если сайт не ответил, возвращаем наши базовые цены и статус False
    return default_prices, False

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
st.title("⚡ EV Calc 2026: Динамические данные")

# Железобетонный вызов функции (программа не упадет никогда)
try:
    current_prices, is_live = fetch_fuel_prices()
except:
    current_prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    is_live = False

# Выводим плашку статуса
if is_live:
    st.success(f"✅ Цены обновлены из сети ({datetime.date.today()})")
else:
    st.warning("⚠️ Режим отказоустойчивости: используются базовые данные 2026 года")

# --- БЛОК ВВОДА ---
st.header("1. Исходные данные")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Автомобиль с ДВС")
    fuel_type = st.selectbox("Тип топлива", list(current_prices.keys()))
    # .get() защищает от ошибки, если тип топлива не найден
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
        # Красиво форматируем тысячные разделители пробелом
        st.write(f"Экономия в год: **{round(annual_saving):,} руб.**".replace(',', ' '))
    else:
        st.error("Электромобиль не окупится при таких параметрах.")
        
