
import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# Função para obter cores ao vivo da Blaze (simulando scraping de uma fonte pública)
def obter_ultimas_cores():
    try:
        url = "https://blaze.com/pt/games/double"  # URL pública da Blaze
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Procurar cores no HTML
        historico = soup.find_all("div", class_="entry")
        cores = []
        for item in historico[:15]:  # pega os 15 últimos
            if "red" in item["class"]:
                cores.append("🔴")
            elif "white" in item["class"]:
                cores.append("⚪")
            elif "black" in item["class"]:
                cores.append("⚫")
        return cores
    except Exception as e:
        return ["Erro ao obter cores:", str(e)]

# Título do painel
st.set_page_config(page_title="Painel Blaze - Cores ao Vivo", layout="centered")
st.title("🎯 Painel de Cores da Blaze - Ao Vivo")
st.write("As últimas cores do jogo *Double* na Blaze (atualização automática):")

# Área dinâmica com atualização a cada X segundos
placeholder = st.empty()

while True:
    with placeholder.container():
        cores = obter_ultimas_cores()
        if isinstance(cores, list):
            st.markdown(" ".join(cores))
        else:
            st.warning("Não foi possível carregar as cores.")
        st.info("Atualizando em 5 segundos...")
    time.sleep(5)
    placeholder.empty()
{
  "numero": 7,
  "cor": "preto"
}
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
