
import streamlit as st
import requests
import time

st.set_page_config(page_title="Painel Blaze Duplo - API", page_icon="🎰", layout="centered")

st.title("🎰 Painel Blaze Duplo - Tempo Real (API Pública)")
st.write("Conectado à Blaze Double pela API pública — atualizando automaticamente.")

placeholder = st.empty()

API_URL = "https://blaze.com/api/roulette_games/recent"

def get_results():
    try:
        r = requests.get(API_URL, timeout=5)
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except Exception as e:
        return []

while True:
    results = get_results()
    if results:
        with placeholder.container():
            st.subheader("Últimos resultados:")
            for game in results[:20]:
                color = game['color']
                number = game['roll']
                if color == 1:
                    bg = "🔴 Vermelho"
                elif color == 2:
                    bg = "⚫ Preto"
                else:
                    bg = "⚪ Branco"
                st.write(f"{bg} — {number}")
    else:
        st.write("Erro ao buscar resultados. Tentando novamente...")
    
    time.sleep(5)
