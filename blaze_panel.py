import requests
import pandas as pd
from datetime import datetime
import streamlit as st

BLAZE_API = "https://blaze.com/api/roulette_games/recent"

@st.cache_data(ttl=5)  # Atualiza a cada 5 segundos
def get_blaze_results():
    try:
        response = requests.get(BLAZE_API, timeout=5)
        data = response.json()
    except:
        return pd.DataFrame()

    results = []
    for game in data[:50]:  # Últimos 50 resultados
        ts = datetime.fromisoformat(game["created_at"].replace("Z", "+00:00"))
        hora = ts.strftime("%H:%M:%S")
        color_num = game["color"]

        # Mapeia cor da Blaze (0 = vermelho, 1 = preto, 2 = branco)
        if color_num == 0:
            color = "🔴 Vermelho"
        elif color_num == 1:
            color = "⚫ Preto"
        elif color_num == 2:
            color = "⚪ Branco"
        else:
            color = "❓ Desconhecido"

        results.append({"Hora": hora, "Cor": color})

    df = pd.DataFrame(results)

    # Filtrar só resultados no segundo 00
    df = df[df["Hora"].str.endswith(":00")]
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

