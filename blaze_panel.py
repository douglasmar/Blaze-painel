
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from datetime import datetime
import streamlit as st

# Configurações do Chrome headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

BLAZE_URL = "https://blaze.bet.br/pt/games/double?modal=double_history-v2_index&roomId=1"

@st.cache_data(ttl=5)  # Atualiza a cada 5 segundos
def get_blaze_results():
    driver = webdriver.Chrome(options=options)
    driver.get(BLAZE_URL)
    time.sleep(3)  # Aguarda carregamento

    try:
        # Captura últimas 20 entradas
        circles = driver.find_elements("css selector", ".entry-color")[:20]
    except:
        driver.quit()
        return pd.DataFrame()

    results = []
    for circle in circles:
        color_class = circle.get_attribute("class").split(" ")[-1]
        time_now = datetime.now().strftime("%H:%M:%S")

        # Mapeia cor
        if "red" in color_class:
            color = "🔴 Vermelho"
        elif "black" in color_class:
            color = "⚫ Preto"
        elif "white" in color_class:
            color = "⚪ Branco"
        else:
            color = color_class

        results.append({"Hora": time_now, "Cor": color})

    driver.quit()

    # Filtra somente :00
    df = pd.DataFrame(results)
    df = df[df['Hora'].str.endswith(":00")]
    return df

# --- UI ---
st.set_page_config(page_title="Painel Blaze Double", layout="centered")
st.markdown("<h1 style='text-align:center;'>🎰 Painel Blaze Double</h1>", unsafe_allow_html=True)
st.write("Exibindo resultados no exato **início de cada minuto**.")

df_resultados = get_blaze_results()

if df_resultados.empty:
    st.warning("Nenhum resultado encontrado no momento. Aguarde a próxima rodada...")
else:
    st.table(df_resultados.style.hide(axis="index"))

st.caption("Atualiza automaticamente a cada 5 segundos.")
