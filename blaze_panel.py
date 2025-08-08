import streamlit as st
import requests
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
    .black { background-color: black; color: white; }
    .red { background-color: red; color: white; }
    .white { background-color: white; color: black; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Lista para armazenar resultados ----------
results = []

# ---------- Função para autenticar ----------
def login_blaze(email, password):
    url = "https://blaze.com/api/auth/password"
    payload = {"username": email, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("accessToken")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
    return None

# ---------- Função para receber mensagens ----------
def on_message(ws, message):
    try:
        data = json.loads(message)
        if "payload" in data and isinstance(data["payload"], dict) and "color" in data["payload"]:
            color_code = data["payload"]["color"]
            number = data["payload"]["roll"]
            if color_code == 0:
                color = "white"
            elif color_code == 1:
                color = "red"
            elif color_code == 2:
                color = "black"
            results.insert(0, (color, number))
            if len(results) > 20:
                results.pop()
    except:
        pass

# ---------- Função para iniciar WebSocket ----------
def start_ws(token):
    ws = websocket.WebSocketApp(
        "wss://api-v2.blaze.com/replication/?EIO=3&transport=websocket",
        on_message=on_message
    )
    while True:
        try:
            ws.run_forever()
        except:
            time.sleep(5)  # tenta reconectar se cair

# ---------- Interface ----------
st.title("🎰 Painel Blaze Double - Tempo Real")
st.write("Digite seu login da Blaze para acompanhar as cores ao vivo.")

if "connected" not in st.session_state:
    st.session_state.connected = False

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    submitted = st.form_submit_button("Entrar")

if submitted:
    token = login_blaze(email, password)
    if token:
        st.success("✅ Login realizado com sucesso! Conectando...")
        threading.Thread(target=start_ws, args=(token,), daemon=True).start()
        st.session_state.connected = True
    else:
        st.error("❌ Falha no login. Verifique seu email/senha.")

# ---------- Mostrar resultados ----------
if st.session_state.connected:
    placeholder = st.empty()
    while True:
        with placeholder.container():
            st.subheader("Últimos resultados:")
            for color, number in results:
                st.markdown(f'<div class="result-box {color}">{number}</div>', unsafe_allow_html=True)
        time.sleep(1)
