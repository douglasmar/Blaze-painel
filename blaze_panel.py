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

# ---------- Função para autenticar ----------
def login_blaze(email, password):
    # Nota: endpoint pode mudar; esse é um exemplo baseado em implementações conhecidas.
    url = "https://blaze.com/api/auth/password"
    payload = {"username": email, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            # retorno pode variar; tentamos pegar accessToken ou token de sessão
            data = response.json()
            token = data.get("accessToken") or data.get("token") or data.get("access_token")
            return token
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        return None

# ---------- Função para receber mensagens ----------
def on_message(ws, message):
    try:
        data = json.loads(message)
        # a estrutura da mensagem do Blaze pode variar; este bloco tenta capturar eventos de rodada
        if isinstance(data, dict):
            payload = data.get("payload") or data.get("data") or data
            if isinstance(payload, dict) and "color" in payload:
                color_code = payload.get("color")
                number = payload.get("roll") or payload.get("number") or payload.get("result")
                if color_code is not None:
                    if color_code == 0:
                        color = "white"
                    elif color_code == 1:
                        color = "red"
                    elif color_code == 2:
                        color = "black"
                    else:
                        color = "white"
                    st.session_state.results.insert(0, (color, number))
                    # manter só 20 últimos
                    st.session_state.results = st.session_state.results[:20]
    except Exception:
        pass

# ---------- Função para iniciar WebSocket ----------
def start_ws(token):
    # endpoint público observado para replicação (pode mudar no futuro)
    ws_url = "wss://api-v2.blaze.com/replication/?EIO=3&transport=websocket"
    def _on_open(ws):
        # se for necessário enviar autenticação na subprotocol/headers, ajustar aqui
        return None

    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=_on_open)
    while True:
        try:
            ws.run_forever(ping_interval=10, ping_timeout=5)
        except Exception:
            time.sleep(5)

# ---------- Interface ----------
st.title("🎰 Painel Blaze Double - Tempo Real")
st.write("Digite seu login da Blaze para acompanhar as cores ao vivo. As credenciais NÃO serão armazenadas por este app.")

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
        # inicia thread do websocket em segundo plano
        thread = threading.Thread(target=start_ws, args=(token,), daemon=True)
        thread.start()
        st.session_state.connected = True
    else:
        st.error("❌ Falha no login. Verifique seu email/senha. Se o endpoint mudou, a autenticação pode falhar.")

# ---------- Mostrar resultados ----------
if st.session_state.connected:
    placeholder = st.empty()
    # Atualiza a visualização a cada segundo
    while True:
        with placeholder.container():
            st.subheader("Últimos resultados:")
            cols = st.columns(10)
            # mostramos a lista (20 itens) dividida nas colunas
            for i, (color, number) in enumerate(st.session_state.results):
                # criar HTML do círculo
                html = f'<div class="result-box {color}">{number if number is not None else ""}</div>'
                # distribuir pelas colunas para visual compacto
                col = cols[i % len(cols)]
                col.markdown(html, unsafe_allow_html=True)
        time.sleep(1)
