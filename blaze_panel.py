
import websocket
import json
import pandas as pd
from datetime import datetime
import streamlit as st
from threading import Thread
import os

results = []

def on_message(ws, message):
    global results
    try:
        data = json.loads(message)
        if data.get("type") == "roulette":
            game = data["payload"]
            ts = datetime.fromisoformat(game["created_at"].replace("Z", "+00:00"))
            hora = ts.strftime("%H:%M:%S")
            color_num = game["color"]

            if color_num == 0:
                color = "🔴 Vermelho"
            elif color_num == 1:
                color = "⚫ Preto"
            elif color_num == 2:
                color = "⚪ Branco"
            else:
                color = "❓ Desconhecido"

            results.insert(0, {"Hora": hora, "Cor": color})
            results = results[:50]

            # Salvar CSV
            df_hist = pd.DataFrame(results)
            df_hist.to_csv("blaze_history.csv", index=False)
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

def on_error(ws, error):
    print(f"Erro WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Conexão WebSocket fechada")

def on_open(ws):
    print("Conectado ao WebSocket da Blaze")

def start_ws():
    ws = websocket.WebSocketApp(
        "wss://api-v2.blaze.com/replication/?EIO=4&transport=websocket",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

Thread(target=start_ws, daemon=True).start()

st.set_page_config(page_title="Painel Blaze Double - Ao Vivo", layout="centered")
st.markdown("<h1 style='text-align:center;'>🎰 Painel Blaze Double - Tempo Real</h1>", unsafe_allow_html=True)
st.write("Resultados aparecem assim que a rodada encerra.")

placeholder = st.empty()

while True:
    if results:
        df = pd.DataFrame(results)
        df = df[df["Hora"].str.endswith(":00")]
        placeholder.table(df.style.hide(axis="index"))

        # Contar cores para gráfico
        counts = df["Cor"].value_counts()
        st.bar_chart(counts)

    st.sleep(1)
