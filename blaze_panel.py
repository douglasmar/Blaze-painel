
import websocket
import json
import pandas as pd
from datetime import datetime
import streamlit as st
from threading import Thread
import os
import time

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

    time.sleep(1)
import streamlit as st
import requests
import websocket
import json
import threading

# Configuração do tema Blaze
st.set_page_config(
    page_title="Painel Blaze Double",
    page_icon="🎰",
    layout="wide"
)

st.markdown(
    """
    <style>
    body { background-color: #000000; color: white; }
    .stButton>button {
        background-color: #FF0000;
        color: white;
        font-weight: bold;
    }
    .result-box {
        display: inline-block;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin: 5px;
        text-align: center;
        line-height: 60px;
        font-weight: bold;
        font-size: 18px;
    }
    .black { background-color: black; color: white; }
    .red { background-color: red; color: white; }
    .white { background-color: white; color: black; }
    </style>
    """,
    unsafe_allow_html=True
)

# Variáveis globais
results = []

# Função para autenticar na Blaze
def login_blaze(email, password):
    url = "https://blaze.com/api/auth/password"
    payload = {"username": email, "password": password}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("accessToken")
    return None

# Função para lidar com mensagens do WebSocket
def on_message(ws, message):
    data = json.loads(message)
    if "payload" in data and "color" in data["payload"]:
        color = data["payload"]["color"]
        if color == 0:
            results.insert(0, ("white", data["payload"]["roll"]))
        elif color == 1:
            results.insert(0, ("red", data["payload"]["roll"]))
        elif color == 2:
            results.insert(0, ("black", data["payload"]["roll"]))
        if len(results) > 20:
            results.pop()

# Conexão WebSocket
def start_ws(token):
    ws = websocket.WebSocketApp(
        "wss://api-v2.blaze.com/replication/?EIO=3&transport=websocket",
        on_message=on_message
    )
    ws.run_forever()

# Formulário de login
st.title("🎰 Painel Blaze Double - Tempo Real")
st.write("Digite seu login da Blaze para acompanhar as cores ao vivo.")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    submitted = st.form_submit_button("Entrar")

if submitted:
    token = login_blaze(email, password)
    if token:
        st.success("✅ Login realizado com sucesso!")
        threading.Thread(target=start_ws, args=(token,), daemon=True).start()
    else:
        st.error("❌ Falha no login. Verifique seu email/senha.")

# Mostrar resultados
if results:
    st.subheader("Últimos resultados:")
    for color, number in results:
        st.markdown(f'<div class="result-box {color}">{number}</div>', unsafe_allow_html=True)
