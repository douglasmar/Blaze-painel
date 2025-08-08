
# Painel Blaze Double - Versão WebSocket Ao Vivo 🎰

Este painel Streamlit conecta via WebSocket na Blaze para mostrar os resultados do jogo Double em tempo real.

## Como rodar localmente

1. Instale as dependências:
```
pip install -r requirements.txt
```

2. Execute o painel:
```
streamlit run blaze_panel.py
```

## Publicar no Streamlit Cloud

1. Crie um repositório no GitHub e envie os arquivos.
2. Acesse https://streamlit.io/cloud e conecte com sua conta GitHub.
3. Clique em "New app", selecione o repositório e o arquivo `blaze_panel.py`.
4. Clique em "Deploy".

## Funcionalidades

- Atualização instantânea via WebSocket
- Gráfico ao vivo da contagem de cores
- Histórico salvo em CSV local `blaze_history.csv`
