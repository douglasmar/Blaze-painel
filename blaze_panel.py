import streamlit as st
import requests
import time

st.set_page_config(page_title="Painel Blaze com Login", layout="centered")
st.title("🎰 Painel Blaze Double com Login")

if "token" not in st.session_state:
    st.session_state.token = None

def login_blaze(usuario, senha):
    url_login = "https://blaze.com/api/auth/login"
    payload = {"login": usuario, "password": senha}
    try:
        res = requests.post(url_login, json=payload)
        res.raise_for_status()
        data = res.json()
        return data.get("token")
    except Exception as e:
        st.error(f"Erro ao logar: {e}")
        return None

if st.session_state.token is None:
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Logar"):
        token = login_blaze(usuario, senha)
        if token:
            st.session_state.token = token
            st.success("Login efetuado com sucesso!")
            st.experimental_rerun()
        else:
            st.error("Falha no login. Verifique usuário e senha.")
else:
    st.write("✅ Você está logado!")

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    API_URL = "https://blaze.com/api/roulette_games/recent"

    placeholder = st.empty()

    def cor_por_valor(valor):
        if valor == 0:
            return "🟢 Verde"
        elif valor == 2:
            return "⚫ Preto"
        elif valor == 1:
            return "🔴 Vermelho"
        else:
            return "❓"

    while True:
        try:
            res = requests.get(API_URL, headers=headers)
            res.raise_for_status()
            resultados = res.json().get("items", [])
            with placeholder.container():
                st.write("Últimos resultados:")
                for r in resultados[:10]:
                    st.write(f"Número: {r['number']} - Cor: {cor_por_valor(r['color'])}")
            time.sleep(5)
        except Exception as e:
            st.error(f"Erro ao buscar resultados: {e}")
            break
