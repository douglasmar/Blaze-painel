
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from datetime import datetime
import streamlit as st

# Configurações do Chrome para rodar headless
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# URL da Blaze Double
BLAZE_URL = "https://blaze.bet.br/pt/games/double?modal=double_history-v2_index&roomId=1"

@st.cache_data(ttl=10)  # Atualiza a cada 10 segundos
def get_blaze_results():
    driver = webdriver.Chrome(options=options)
    driver.get(BLAZE_URL)
    time.sleep(5)  # Tempo para carregar os resultados

    # Coleta dos elementos de histórico
    try:
        circles = driver.find_elements("css selector", ".entry-color")[:50]  # Últimos 50
    except:
        driver.quit()
        return pd.DataFrame()

    results = []
    for circle in circles:
        color = circle.get_attribute("class").split(" ")[-1]
        time_now = datetime.now().strftime("%H:%M:%S")
        results.append({"hora": time_now, "cor": color})

    driver.quit()

    df = pd.DataFrame(results)

    # Filtrar: apenas se segundos == 00 (antes de cada minuto)
    df = df[df['hora'].str.endswith(":00")]
    return df

# --- Streamlit UI ---
st.set_page_config(page_title="Painel Blaze Double", layout="centered")
st.title("🎰 Painel Blaze Double – Resultados por Minuto")
st.write("Mostrando os resultados com timestamp final **:00** (antes de cada minuto).")

df_resultados = get_blaze_results()

st.dataframe(df_resultados)
st.info("Atualiza automaticamente a cada 10 segundos.")
