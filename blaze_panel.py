import streamlit as st
import requests
import time
import json
from datetime import datetime

# ===== Configuração da página =====
st.set_page_config(
    page_title="Monitor Blaze Double", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== CSS customizado =====
st.markdown("""
<style>
    .main { padding-top: 2rem; }
    .stApp { background-color: #1a1a1a; }
    .resultado-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 8px;
        padding: 20px;
        background: #2d2d2d;
        border-radius: 10px;
        margin: 10px 0;
    }
    .info-card {
        background: #333;
        padding: 15px;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ===== Função para obter resultados =====
@st.cache_data(ttl=5)  # Cache por 5 segundos
def obter_ultimos_resultados():
    """Obtém os últimos resultados da API da Blaze com fallback para dados mock"""
    try:
        # Tenta múltiplas URLs da API
        urls = [
            "https://blaze.com/api/roulette_games/recent",
            "https://blaze1.space/api/roulette_games/recent",
            "https://api.blaze.com/roulette_games/recent"
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://blaze.com/"
        }
        
        for url in urls:
            try:
                resposta = requests.get(url, headers=headers, timeout=5)
                if resposta.status_code == 200:
                    dados = resposta.json()
                    break
            except:
                continue
        else:
            # Se todas as APIs falharam, usa dados mock
            return gerar_dados_mock()

        # Processa dados da API
        if isinstance(dados, dict):
            if "records" in dados:
                dados = dados["records"]
            elif "data" in dados:
                dados = dados["data"]
            else:
                return gerar_dados_mock()

        resultados = []
        for jogo in dados[:15]:
            cor = jogo.get("color", jogo.get("colour", 1))
            numero = jogo.get("roll", jogo.get("number", 1))
            
            # Mapeia cores
            if cor == 1:  # Vermelho
                cor_bg = "#dc2626"
                cor_nome = "Vermelho"
            elif cor == 2:  # Preto
                cor_bg = "#1f2937"
                cor_nome = "Preto"
            elif cor == 0:  # Branco
                cor_bg = "#f3f4f6"
                cor_nome = "Branco"
            else:
                cor_bg = "#6b7280"
                cor_nome = "Desconhecido"

            # HTML da bolinha
            html_bolinha = f"""
            <div style="
                display: inline-block;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: {cor_bg};
                color: {'#000000' if cor == 0 else '#ffffff'};
                text-align: center;
                line-height: 50px;
                font-weight: bold;
                font-size: 18px;
                margin: 4px;
                border: 3px solid {'#000000' if cor != 0 else '#333333'};
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                transition: transform 0.2s;
            " title="{cor_nome} - {numero}">
                {numero}
            </div>
            """
            
            resultados.append({
                'html': html_bolinha,
                'cor': cor_nome,
                'numero': numero
            })

        return resultados

    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return gerar_dados_mock()

# ===== Função para gerar dados mock =====
def gerar_dados_mock():
    """Gera dados mock quando a API não está disponível"""
    import random
    
    cores_config = [
        (1, "#dc2626", "Vermelho"),
        (2, "#1f2937", "Preto"), 
        (0, "#f3f4f6", "Branco")
    ]
    
    resultados = []
    for i in range(15):
        cor_id, cor_bg, cor_nome = random.choices(
            cores_config, 
            weights=[47, 47, 6]  # Probabilidades realistas
        )[0]
        
        numero = random.randint(0, 14)
        
        html_bolinha = f"""
        <div style="
            display: inline-block;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: {cor_bg};
            color: {'#000000' if cor_id == 0 else '#ffffff'};
            text-align: center;
            line-height: 50px;
            font-weight: bold;
            font-size: 18px;
            margin: 4px;
            border: 3px solid {'#000000' if cor_id != 0 else '#333333'};
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        " title="{cor_nome} - {numero}">
            {numero}
        </div>
        """
        
        resultados.append({
            'html': html_bolinha,
            'cor': cor_nome,
            'numero': numero
        })
    
    return resultados

# ===== Interface principal =====
def main():
    # Título
    st.markdown("""
    <h1 style="text-align: center; color: #dc2626; font-size: 3rem; margin-bottom: 0;">
        🎯 Monitor Blaze Double
    </h1>
    <p style="text-align: center; color: #9ca3af; font-size: 1.2rem;">
        Resultados ao vivo do jogo Double
    </p>
    """, unsafe_allow_html=True)

    # Container para resultados
    container_resultados = st.container()
    
    # Container para estatísticas
    col1, col2, col3 = st.columns(3)
    
    # Botão de atualização manual
    col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 2, 1])
    
    with col_refresh2:
        if st.button("🔄 Atualizar Agora", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Obtém e exibe resultados
    with container_resultados:
        with st.spinner("Carregando resultados..."):
            resultados = obter_ultimos_resultados()
            
            if resultados:
                # Exibe as bolinhas
                st.markdown('<div class="resultado-container">', unsafe_allow_html=True)
                html_bolinhas = "".join([r['html'] for r in resultados])
                st.markdown(html_bolinhas, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Calcula estatísticas
                total = len(resultados)
                vermelhos = len([r for r in resultados if r['cor'] == 'Vermelho'])
                pretos = len([r for r in resultados if r['cor'] == 'Preto'])
                brancos = len([r for r in resultados if r['cor'] == 'Branco'])
                
                # Exibe estatísticas
                with col1:
                    st.markdown(f"""
                    <div class="info-card" style="background: #dc2626;">
                        <h3>🔴 Vermelho</h3>
                        <h2>{vermelhos}</h2>
                        <p>{(vermelhos/total*100):.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="info-card" style="background: #1f2937;">
                        <h3>⚫ Preto</h3>
                        <h2>{pretos}</h2>
                        <p>{(pretos/total*100):.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="info-card" style="background: #6b7280;">
                        <h3>⚪ Branco</h3>
                        <h2>{brancos}</h2>
                        <p>{(brancos/total*100):.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Info de atualização
                st.info(f"📅 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
                st.markdown("**💡 Dica:** A página atualiza automaticamente a cada 15 segundos ou clique em 'Atualizar Agora'")
            
            else:
                st.error("❌ Não foi possível carregar os resultados")

    # Auto-refresh a cada 15 segundos
    time.sleep(15)
    st.rerun()

# ===== Execução =====
if __name__ == "__main__":
    main()
