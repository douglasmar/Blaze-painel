import streamlit as st
import websocket
import json
import threading
import time

# ---------- Configuração do painel ----------
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
    .black { background-color: black; color: white; border: 2px solid #333; }
    .red { background-color: red; color: white; border: 2px solid #400; }
    .white { background-color: white; color: black; border: 2px solid #ddd; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Lista para armazenar resultados ----------
if "results" not in st.session_state:
    st.session_state.results = []

# ---------- Função para receber mensagens ----------
def on_message(ws, message):
    try:
        data = json.loads(message)
        payload = data.get("payload") if isinstance(data, dict) else None
        if isinstance(payload, dict) and "color" in payload:
            color_code = payload.get("color")
            number = payload.get("roll") or payload.get("number") or payload.get("result")
            if color_code == 0:
                color = "white"
            elif color_code == 1:
                color = "red"
            elif color_code == 2:
                color = "black"
            else:
                color = "white"
            st.session_state.results.insert(0, (color, number))
            st.session_state.results = st.session_state.results[:20]
    except Exception:
        pass

# ---------- Função para iniciar WebSocket ----------
def start_ws():
    ws_url = "wss://api-v2.blaze.com/replication/?EIO=3&transport=websocket"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message)
    while True:
        try:
            ws.run_forever(ping_interval=10, ping_timeout=5)
        except Exception:
            time.sleep(5)

# ---------- Iniciar conexão em segundo plano ----------
if "ws_started" not in st.session_state:
    threading.Thread(target=start_ws, daemon=True).start()
    st.session_state.ws_started = True

# ---------- Interface ----------
st.title("🎰 Painel Blaze Double - Tempo Real")
st.write("Conectado ao Blaze Double (sem login) — resultados ao vivo.")

# ---------- Mostrar resultados ----------
placeholder = st.empty()
while True:
    with placeholder.container():
        st.subheader("Últimos resultados:")
        cols = st.columns(10)
        for i, (color, number) in enumerate(st.session_state.results):
            html = f'<div class="result-box {color}">{number if number is not None else ""}</div>'
            col = cols[i % len(cols)]
            col.markdown(html, unsafe_allow_html=True)
    time.sleep(1)
