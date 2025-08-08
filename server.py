
from flask import Flask, jsonify
import requests

app = Flask(__name__)

BLAZE_API = "https://blaze.com/api/roulette_games/recent"

@app.route('/ultimo', methods=['GET'])
def ultimo_resultado():
    try:
        response = requests.get(BLAZE_API, timeout=5)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            ultimo = data[0]
            numero = ultimo.get("roll")
            cor_id = ultimo.get("color")
            cor_map = {0: "vermelho", 1: "preto", 2: "branco"}
            cor = cor_map.get(cor_id, "desconhecido")
            return jsonify({"numero": numero, "cor": cor})
        else:
            return jsonify({"erro": "Sem dados"}), 500
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
