import streamlit as st
import requests
import time

# Função para obter as últimas cores e números
def obter_ultimos_resultados():
    try:
        url = "https://blaze.com/api/roulette_games/recent"
        resposta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        dados = resposta.json()

        # Se vier dicionário, pegar lista correta
        if isinstance(dados, dict):
            if "records" in dados:
                dados = dados["records"]
            else:
                return []

        resultados = []
        for jogo in dados[:15]:
            cor = jogo.get("color")
            numero = jogo.get("roll")

            # Define cor de fundo igual ao Blaze
            if cor == 1:  # Vermelho
                cor_bg = "#ff4d4d"
            elif cor == 2:  # Preto
                cor_bg = "#333333"
            elif cor == 0:  # Branco
                cor_bg = "#ffffff"
            else:
                cor_bg = "#cccccc"

            # Bolinha estilizada
            html_bolinha = f"""
            <div style="
                display: inline-block;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: {cor_bg};
                color: {'#000000' if cor == 0 else '#ffffff'};
                text-align: center;
                line-height: 40px;
                font-weight: bold;
                font-size: 16px;
                margin: 2px;
                border: 2px solid #000;
            ">
                {numero}
            </div>
            """
            resultados.append(html_bolinha)

        return resultados

    except Exception as e:
        return [f"<p>Erro: {e}</p>"]

# Configuração do painel
st.set_page_config(page_title="Painel Blaze - Bolinhas", layout="centered")
st.title("🎯 Painel da Blaze - Ao Vivo")
st.write("Últimos resultados do jogo *Double* com visual da roleta:")

placeholder = st.empty()

while True:
    with placeholder.container():
        resultados = obter_ultimos_resultados()
        st.markdown("".join(resultados), unsafe_allow_html=True)
        st.info("Atualizando em 5 segundos...")
    time.sleep(5)
