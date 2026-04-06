import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import re

# 1. Настройка страницы (мягкая тема)
st.set_page_config(page_title="EV Calc 2026 Pro", page_icon="⚡", layout="centered")

# 2. Функция получения цен (максимальная защита)
@st.cache_data(ttl=3600)
def get_fuel_prices():
    # Базовые цены 2026 года для СПб
    prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    status = False
    
    try:
        # Пробуем получить данные с сайта мониторинга
        url = "https://fuelprices.ru/st-petersburg"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tds = soup.find_all('td')
            for i in range(len(tds)):
                text = tds[i].get_text()
                if "95" in text and i+1 < len(tds):
                    val = tds[i+1].get_text().strip().replace(',', '.')
                    prices["АИ-95"] = float(re.findall(r"\d+\.\d+", val)[0])
                if "92" in text and i+1 < len(tds):
                    val = tds[i+1].get_text().strip().replace(',', '.')
                    prices["АИ-92"] = float(re.findall(r"\d+\.\d+", val)[0])
            status = True
    except:
        pass # При любой ошибке просто используем базу
    return prices, status

# --- ИНТЕРФЕЙС ---
st.title("⚡ Экономика электромобиля 2026")

current_prices, is_live = get_fuel_prices()

# Плашка статуса (профессиональный стиль)
if is_live:
    st.success(f"✅ Цены обновлены автоматически ({datetime.date.today().strftime('%d.%m.%Y')})")
else:
    st.info("ℹ️ Приложение работает в автономном режиме (база данных 2026)")

st.divider()

# 3. Ввод данных в две колонки
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Бензиновый авто")
    fuel_type = st.selectbox("Тип топлива", list(current_prices.keys()))
    fuel_price = st.number_input("Цена за литр (₽)", value=current_prices[fuel_type], step=0.1)
    price_ice = st.number_input("Стоимость авто (₽)", value=2200000, step=50000)
    cons_ice = st.number_input("Расход (л/100 км)", value=9.0, step=0.5)

with col2:
    st.subheader("🔋 Электромобиль")
    # Тариф 2026 года (ночной/день усредненный)
    elec_price = st.number_input("Тариф за кВт⋅ч (₽)", value=3.85, step=0.1)
    price_ev = st.number_input("Стоимость ЭД (₽)", value=3600000, step=50000)
    cons_ev = st.number_input("Расход (кВт⋅ч/100 км)", value=18.0, step=1.0)

st.write("") # Отступ

# 4. ТОТ САМЫЙ УДОБНЫЙ ПОЛЗУНОК ПРОБЕГА
st.subheader("🛣️ Ваша эксплуатация")
annual_km = st.select_slider(
    "Средний годовой пробег (километров)",
    options=[5000, 10000, 15000, 20000, 25000, 30000, 40000, 50000, 75000, 100000],
    value=20000,
    help="Выберите наиболее близкое к вашему стилю езды значение"
)

st.divider()

# 5. Расчетная логика
if st.button("РАССЧИТАТЬ ОКУПАЕМОСТЬ", type="primary", use_container_width=True):
    # Стоимость 1 км пути
    cost_1km_ice = (cons_ice / 100) * fuel_price
    cost_1km_ev = (cons_ev / 100) * elec_price
    
    # Экономия
    annual_saving = (cost_1km_ice - cost_1km_ev) * annual_km
    price_diff = price_ev - price_ice
    
    if annual_saving > 0:
        payback_years = price_diff / annual_saving
        
        # Красивый вывод результата
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
        
