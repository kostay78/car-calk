import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime

# Настройка страницы
st.set_page_config(page_title="EV Calc 2026 Pro", page_icon="⚡")

# --- ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ЦЕН С САЙТА ---
@st.cache_data(ttl=3600)  # Кэшируем данные на 1 час, чтобы не спамить сайт запросами
def get_real_prices():
    # Базовые цены (запасной вариант на 2026 год)
    prices = {"АИ-92": 65.80, "АИ-95": 71.50, "Дизель": 68.20}
    
    try:
        # Пример адреса (в 2026 году пути могут быть другими, это демонстрационный URL)
        url = "https://petrolplus.ru/fuel_prices/sankt-peterburg/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Здесь логика поиска конкретных цифр на странице
            # Это примерный поиск, так как верстка сайтов меняется
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    fuel_name = cols[0].text.strip()
                    price_val = cols[1].text.strip().replace(',', '.')
                    if "92" in fuel_name: prices["АИ-92"] = float(price_val)
                    if "95" in fuel_name: prices["АИ-95"] = float(price_val)
                    if "Дизель" in fuel_name: prices["Дизель"] = float(price_val)
            return prices, True
    except Exception as e:
        return prices, False # Возвращаем базу, если интернет упал или сайт заблокировал нас

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
st.title("⚡ EV Calc 2026: Динамические данные")

# Загружаем цены
current_prices, is_live = get_real_prices()

if is_live:
    st.success(f"✅ Цены на топливо обновлены автоматически ({datetime.date.today()})")
else:
    st.warning("⚠️ Не удалось подключиться к серверу цен. Используются архивные данные 2026 года.")

# --- БЛОК ВВОДА (оставляем как в прошлой версии) ---
st.header("1. Исходные данные")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Автомобиль с ДВС")
    fuel_type = st.selectbox("Тип топлива", list(current_prices.keys()))
    # По умолчанию ставим актуальную цену из интернета, но даем пользователю ее подправить
    fuel_price = st.number_input("Цена за литр (руб)", value=current_prices[fuel_type])
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
        st.write(f"Экономия в год: {round(annual_saving):,} руб.")
    else:
        st.error("Электромобиль не окупится при таких параметрах.")
