import streamlit as st
import requests
import time

# Função para obter as últimas cores do Blaze pela API pública
def obter_ultimas_cores():
    try:
        url = "https://blaze.com/api/roulette_games/recent"
        resposta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        dados = resposta.json()
        
        cores = []
        for jogo in dados[:15]:  # Pega os 15 últimos resultados
            cor = jogo["color"]
            if cor == 1:
                cores.append("🔴")  # Vermelho
            elif cor == 2:
                cores.append("⚫")  # Preto
            elif cor == 0:
                cores.append("⚪")  # Branco
        return cores
    except Exception as e:
        return ["Erro:", str(e)]

# Configuração do painel
st.set_page_config(page_title="Painel Blaze - Cores ao Vivo", layout="centered")
st.title("🎯 Painel de Cores da Blaze - Ao Vivo")
st.write("As últimas cores do jogo *Double* na Blaze (atualização automática):")

# Área dinâmica
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
