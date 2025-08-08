
import streamlit as st
import requests
import time

st.set_page_config(page_title="Painel Blaze - Tempo Real", page_icon="🎯", layout="centered")

st.title("🎯 Painel Blaze - Último Resultado (Tempo Real)")
st.write("Mostrando o último resultado do Blaze Double em tempo real.")

# Função para pegar último resultado
def get_ultimo_resultado():
    try:
        url = "https://api-v2.blaze.com/games/double/recent"  # endpoint alternativo
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 0:
                return data[0]  # último resultado
    except Exception as e:
        return None
    return None

# Loop de atualização automática
placeholder = st.empty()

while True:
    resultado = get_ultimo_resultado()
    if resultado:
        numero = resultado["roll"]
        cor = resultado["color"]  # 0=vermelho, 1=preto, 2=verde

        if cor == 0:
            cor_nome = "🔴 Vermelho"
            cor_hex = "#d90429"
        elif cor == 1:
            cor_nome = "⚫ Preto"
            cor_hex = "#000000"
        else:
            cor_nome = "🟢 Verde"
            cor_hex = "#00ff00"

        with placeholder.container():
            st.markdown(f"### Último Resultado: {cor_nome}")
            st.markdown(
                f'<div style="width:80px;height:80px;border-radius:50%;background-color:{cor_hex};display:flex;align-items:center;justify-content:center;font-size:28px;color:white;">{numero}</div>',
                unsafe_allow_html=True
            )
    else:
        with placeholder.container():
            st.error("Erro ao buscar resultado. Tentando novamente...")

    time.sleep(5)
