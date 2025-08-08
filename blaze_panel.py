
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
