import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import re

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="EV Calc 2026 Pro", page_icon="⚡", layout="centered")

# --- ФУНКЦИЯ ПОЛУЧЕНИЯ ЦЕН ---
@st.cache_data(ttl=3600)
def get_fuel_prices():
    prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    status = False
    
    try:
        url = "https://www.benzin-price.ru/price_fuel.php?region_id=78"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
            'Referer': 'https://yandex.ru/'
        }
        
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            match_95 = re.search(r'95.*?(\d{2}[\.,]\d{2})', page_text)
            match_92 = re.search(r'92.*?(\d{2}[\.,]\d{2})', page_text)
            match_dt = re.search(r'Дизель.*?(\d{2}[\.,]\d{2})', page_text)
            
            if match_95:
                prices["АИ-95"] = float(match_95.group(1).replace(',', '.'))
                status = True
            if match_92:
                prices["АИ-92"] = float(match_92.group(1).replace(',', '.'))
                status = True
            if match_dt:
                prices["Дизель"] = float(match_dt.group(1).replace(',', '.'))
    except:
        pass 
    
    return prices, status

# --- ИНТЕРФЕЙС ---
st.title("⚡ Экономика электромобиля 2026")

current_prices, is_live = get_fuel_prices()

# Плашка статуса
if is_live:
    st.success(f"✅ Цены обновлены автоматически ({datetime.date.today().strftime('%d.%m.%Y')})")
else:
    st.info("ℹ️ Приложение работает в автономном режиме (база данных 2026)")

st.divider()

# --- ВВОД ДАННЫХ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Бензиновый авто")
    fuel_type = st.selectbox("Тип топлива", list(current_prices.keys()))
    fuel_price = st.number_input("Цена за литр (₽)", value=current_prices[fuel_type], step=0.1)
    price_ice = st.number_input("Стоимость авто (₽)", value=2200000, step=50000)
    cons_ice = st.number_input("Расход (л/100 км)", value=9.0, step=0.5)

with col2:
    st.subheader("🔋 Электромобиль")
    elec_price = st.number_input("Тариф за кВт⋅ч (₽)", value=3.85, step=0.1)
    price_ev = st.number_input("Стоимость ЭД (₽)", value=3600000, step=50000)
    cons_ev = st.number_input("Расход (кВт⋅ч/100 км)", value=18.0, step=1.0)

st.write("")

# --- ПЛАВНЫЙ ПОЛЗУНОК ПРОБЕГА ---
st.subheader("🛣️ Ваша эксплуатация")
annual_km = st.slider(
    "Средний годовой пробег (километров)",
    min_value=5000,
    max_value=100000,
    value=20000,
    step=500,
    help="Потяните ползунок, чтобы выбрать ваш примерный пробег за год"
)

st.divider()

# --- ЛОГИКА РАСЧЕТА ---
if st.button("РАССЧИТАТЬ ОКУПАЕМОСТЬ", type="primary", use_container_width=True):
    cost_1km_ice = (cons_ice / 100) * fuel_price
    cost_1km_ev = (cons_ev / 100) * elec_price
    
    annual_saving = (cost_1km_ice - cost_1km_ev) * annual_km
    price_diff = price_ev - price_ice
    
    if annual_saving > 0:
        payback_years = price_diff / annual_saving
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Срок окупаемости", f"{round(payback_years, 1)} лет")
        with c2:
            st.metric("Экономия в год", f"{round(annual_saving):,} ₽".replace(',', ' '))
            
        if payback_years <= 5:
            st.balloons()
            st.success("🔥 Отличный результат! Электромобиль очень выгоден.")
        elif payback_years <= 10:
            st.warning("⚖️ Хороший результат. Окупаемость в пределах разумного.")
        else:
            st.info("⏳ Окупаемость долгая, но вы вносите вклад в экологию.")
    else:
        st.error("При таких параметрах электромобиль не окупится.")
        
