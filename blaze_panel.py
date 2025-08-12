/app/
├── backend/
│ ├── server.py
│ ├── requirements.txt
│ └── .env
└── frontend/
├── src/
│ ├── App.js
│ ├── App.css
│ └── index.css
├── package.json
└── .env
```
---
## 🐍 **BACKEND - server.py**
```python
from fastapi import FastAPI, APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import asyncio
import aiohttp
import random
import json
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')
# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
# Create the main app without a prefix
app = FastAPI()
# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")
# WebSocket manager for real-time updates
class ConnectionManager:
def __init__(self):
self.active_connections: List[WebSocket] = []
async def connect(self, websocket: WebSocket):
await websocket.accept()
self.active_connections.append(websocket)
def disconnect(self, websocket: WebSocket):
self.active_connections.remove(websocket)
async def broadcast(self, message: str):
for connection in self.active_connections:
try:
await connection.send_text(message)
except:
pass
manager = ConnectionManager()
# Define Models
class StatusCheck(BaseModel):
id: str = Field(default_factory=lambda: str(uuid.uuid4()))
client_name: str
timestamp: datetime = Field(default_factory=datetime.utcnow)
class StatusCheckCreate(BaseModel):
client_name: str
class BlazeResult(BaseModel):
id: str = Field(default_factory=lambda: str(uuid.uuid4()))
number: int
color: int # 0=branco, 1=vermelho, 2=preto
color_name: str
timestamp: datetime = Field(default_factory=datetime.utcnow)
source: str = "api" # "api" ou "mock"
def dict(self, **kwargs):
d = super().dict(**kwargs)
d['timestamp'] = self.timestamp.isoformat()
return d
class BlazePattern(BaseModel):
id: str = Field(default_factory=lambda: str(uuid.uuid4()))
pattern_type: str # "sequence", "frequency", "gale"
description: str
confidence: float
results_analyzed: int
created_at: datetime = Field(default_factory=datetime.utcnow)
def dict(self, **kwargs):
d = super().dict(**kwargs)
d['created_at'] = self.created_at.isoformat()
return d
class BlazeAlert(BaseModel):
id: str = Field(default_factory=lambda: str(uuid.uuid4()))
alert_type: str # "pattern", "sequence", "gale"
message: str
confidence: float
active: bool = True
created_at: datetime = Field(default_factory=datetime.utcnow)
def dict(self, **kwargs):
d = super().dict(**kwargs)
d['created_at'] = self.created_at.isoformat()
return d
# Blaze API Functions
async def fetch_blaze_data():
"""Obtém dados da API da Blaze com fallback para dados mock"""
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
try:
async with aiohttp.ClientSession() as session:
for url in urls:
try:
async with session.get(url, headers=headers, timeout=5) as response:
if response.status == 200:
data = await response.json()
return process_blaze_data(data, "api")
except:
continue
except Exception as e:
logger.error(f"Erro ao buscar dados da API: {e}")
# Fallback para dados mock
return generate_mock_data()
def process_blaze_data(data, source="api"):
"""Processa dados da API da Blaze"""
results = []
# Extrai dados baseado na estrutura da API
if isinstance(data, dict):
if "records" in data:
data = data["records"]
elif "data" in data:
data = data["data"]
for game in data[:20]: # Últimos 20 resultados
color_id = game.get("color", game.get("colour", 1))
number = game.get("roll", game.get("number", 1))
# Mapeia cores
color_names = {0: "Branco", 1: "Vermelho", 2: "Preto"}
color_name = color_names.get(color_id, "Desconhecido")
result = BlazeResult(
number=number,
color=color_id,
color_name=color_name,
source=source
)
results.append(result)
return results
def generate_mock_data():
"""Gera dados mock quando a API não está disponível"""
results = []
colors = [
(0, "Branco"),
(1, "Vermelho"),
(2, "Preto")
]
for i in range(20):
# Probabilidades realistas: Branco 6%, Vermelho 47%, Preto 47%
color_id, color_name = random.choices(
colors,
weights=[6, 47, 47]
)[0]
number = random.randint(0, 14)
result = BlazeResult(
number=number,
color=color_id,
color_name=color_name,
source="mock"
)
results.append(result)
return results
async def analyze_patterns(results: List[BlazeResult]) -> List[BlazePattern]:
"""Analisa padrões nos resultados"""
patterns = []
if len(results) < 5:
return patterns
# Análise de sequências de cores
color_sequence = [r.color for r in results[:10]]
# Detecta sequências de mesma cor
current_sequence = 1
current_color = color_sequence[0]
max_sequence = 1
sequence_color = current_color
for i in range(1, len(color_sequence)):
if color_sequence[i] == current_color:
current_sequence += 1
if current_sequence > max_sequence:
max_sequence = current_sequence
sequence_color = current_color
else:
current_sequence = 1
current_color = color_sequence[i]
if max_sequence >= 3:
color_names = {0: "Branco", 1: "Vermelho", 2: "Preto"}
pattern = BlazePattern(
pattern_type="sequence",
description=f"Sequência de {max_sequence} {color_names[sequence_color]}s",
confidence=min(0.9, max_sequence * 0.2),
results_analyzed=len(results)
)
patterns.append(pattern)
# Análise de frequência
red_count = sum(1 for r in results[:10] if r.color == 1)
black_count = sum(1 for r in results[:10] if r.color == 2)
white_count = sum(1 for r in results[:10] if r.color == 0)
total = len(results[:10])
if total > 0:
red_freq = red_count / total
black_freq = black_count / total
white_freq = white_count / total
if red_freq > 0.7:
pattern = BlazePattern(
pattern_type="frequency",
description=f"Alta frequência de Vermelho ({red_freq:.1%})",
confidence=red_freq,
results_analyzed=total
)
patterns.append(pattern)
elif black_freq > 0.7:
pattern = BlazePattern(
pattern_type="frequency",
description=f"Alta frequência de Preto ({black_freq:.1%})",
confidence=black_freq,
results_analyzed=total
)
patterns.append(pattern)
elif white_freq > 0.2:
pattern = BlazePattern(
pattern_type="frequency",
description=f"Alta frequência de Branco ({white_freq:.1%})",
confidence=white_freq,
results_analyzed=total
)
patterns.append(pattern)
return patterns
async def generate_alerts(patterns: List[BlazePattern]) -> List[BlazeAlert]:
"""Gera alertas baseado nos padrões detectados"""
alerts = []
for pattern in patterns:
if pattern.confidence > 0.7:
alert = BlazeAlert(
alert_type=pattern.pattern_type,
message=f"🚨 PADRÃO DETECTADO: {pattern.description}",
confidence=pattern.confidence
)
alerts.append(alert)
return alerts
# API Routes
@api_router.get("/")
async def root():
return {"message": "Blaze Monitor API"}
@api_router.get("/blaze/results", response_model=Dict[str, Any])
async def get_blaze_results():
"""Obtém os últimos resultados da Blaze"""
try:
# Busca dados da API
results = await fetch_blaze_data()
# Salva no banco de dados
for result in results:
await db.blaze_results.update_one(
{"number": result.number, "color": result.color, "timestamp": result.timestamp},
{"$set": result.dict()},
upsert=True
)
# Analisa padrões
patterns = await analyze_patterns(results)
# Gera alertas
alerts = await generate_alerts(patterns)
# Salva padrões e alertas
for pattern in patterns:
await db.blaze_patterns.insert_one(pattern.dict())
for alert in alerts:
await db.blaze_alerts.insert_one(alert.dict())
# Calcula estatísticas
total = len(results)
if total > 0:
red_count = sum(1 for r in results if r.color == 1)
black_count = sum(1 for r in results if r.color == 2)
white_count = sum(1 for r in results if r.color == 0)
stats = {
"total": total,
"red": {"count": red_count, "percentage": (red_count/total)*100},
"black": {"count": black_count, "percentage": (black_count/total)*100},
"white": {"count": white_count, "percentage": (white_count/total)*100}
}
else:
stats = {"total": 0, "red": {"count": 0, "percentage": 0}, "black": {"count": 0, "percentage": 0}, "white": {"count": 0, "percentage": 0}}
response_data = {
"results": [r.dict() for r in results],
"patterns": [p.dict() for p in patterns],
"alerts": [a.dict() for a in alerts],
"statistics": stats,
"last_updated": datetime.utcnow().isoformat()
}
# Broadcast para WebSocket connections
await manager.broadcast(json.dumps(response_data))
return response_data
except Exception as e:
logger.error(f"Erro ao obter resultados da Blaze: {e}")
raise HTTPException(status_code=500, detail="Erro interno do servidor")
@api_router.get("/blaze/history", response_model=List[BlazeResult])
async def get_blaze_history(limit: int = 100):
"""Obtém histórico de resultados salvos no banco"""
try:
cursor = db.blaze_results.find().sort("timestamp", -1).limit(limit)
results = await cursor.to_list(length=limit)
return [BlazeResult(**result) for result in results]
except Exception as e:
logger.error(f"Erro ao obter histórico: {e}")
raise HTTPException(status_code=500, detail="Erro interno do servidor")
@api_router.get("/blaze/patterns", response_model=List[BlazePattern])
async def get_patterns(limit: int = 10):
"""Obtém padrões detectados"""
try:
cursor = db.blaze_patterns.find().sort("created_at", -1).limit(limit)
patterns = await cursor.to_list(length=limit)
return [BlazePattern(**pattern) for pattern in patterns]
except Exception as e:
logger.error(f"Erro ao obter padrões: {e}")
raise HTTPException(status_code=500, detail="Erro interno do servidor")
@api_router.get("/blaze/alerts", response_model=List[BlazeAlert])
async def get_alerts(active_only: bool = True):
"""Obtém alertas"""
try:
query = {"active": True} if active_only else {}
cursor = db.blaze_alerts.find(query).sort("created_at", -1).limit(20)
alerts = await cursor.to_list(length=20)
return [BlazeAlert(**alert) for alert in alerts]
except Exception as e:
logger.error(f"Erro ao obter alertas: {e}")
raise HTTPException(status_code=500, detail="Erro interno do servidor")
@api_router.websocket("/blaze/ws")
async def websocket_endpoint(websocket: WebSocket):
"""WebSocket para atualizações em tempo real"""
await manager.connect(websocket)
try:
while True:
# Envia dados atualizados a cada 10 segundos
await asyncio.sleep(10)
results = await fetch_blaze_data()
patterns = await analyze_patterns(results)
alerts = await generate_alerts(patterns)
data = {
"results": [r.dict() for r in results],
"patterns": [p.dict() for p in patterns],
"alerts": [a.dict() for a in alerts],
"timestamp": datetime.utcnow().isoformat()
}
await websocket.send_text(json.dumps(data))
except WebSocketDisconnect:
manager.disconnect(websocket)
# Original status routes
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
status_dict = input.dict()
status_obj = StatusCheck(**status_dict)
_ = await db.status_checks.insert_one(status_obj.dict())
return status_obj
@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
status_checks = await db.status_checks.find().to_list(1000)
return [StatusCheck(**status_check) for status_check in status_checks]
# Include the router in the main app
app.include_router(api_router)
app.add_middleware(
CORSMiddleware,
allow_credentials=True,
allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
allow_methods=["*"],
allow_headers=["*"],
)
# Configure logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
@app.on_event("shutdown")
async def shutdown_db_client():
client.close()
```
---
## 🐍 **BACKEND - requirements.txt**
```txt
fastapi==0.110.1
uvicorn==0.25.0
boto3>=1.34.129
requests-oauthlib>=2.0.0
cryptography>=42.0.8
python-dotenv>=1.0.1
pymongo==4.5.0
pydantic>=2.6.4
email-validator>=2.2.0
pyjwt>=2.10.1
passlib>=1.7.4
tzdata>=2024.2
motor==3.3.1
pytest>=8.0.0
black>=24.1.1
isort>=5.13.2
flake8>=7.0.0
mypy>=1.8.0
python-jose>=3.3.0
requests>=2.31.0
pandas>=2.2.0
numpy>=1.26.0
python-multipart>=0.0.9
jq>=1.6.0
typer>=0.9.0
aiohttp>=3.9.0
websockets>=12.0
```
---
## ⚛️ **FRONTEND - App.js**
```javascript
import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const BlazeMonitor = () => {
const [blazeData, setBlazeData] = useState(null);
const [loading, setLoading] = useState(true);
const [connected, setConnected] = useState(false);
const [alerts, setAlerts] = useState([]);
const [autoRefresh, setAutoRefresh] = useState(true);
const fetchBlazeData = useCallback(async () => {
try {
setLoading(true);
const response = await axios.get(`${API}/blaze/results`);
setBlazeData(response.data);
setAlerts(response.data.alerts || []);
setConnected(true);
} catch (error) {
console.error('Erro ao buscar dados da Blaze:', error);
setConnected(false);
} finally {
setLoading(false);
}
}, []);
useEffect(() => {
fetchBlazeData();
}, [fetchBlazeData]);
useEffect(() => {
if (!autoRefresh) return;
const interval = setInterval(() => {
fetchBlazeData();
}, 10000); // Atualiza a cada 10 segundos
return () => clearInterval(interval);
}, [autoRefresh, fetchBlazeData]);
const getColorStyle = (color) => {
switch (color) {
case 0: // Branco
return {
backgroundColor: '#f3f4f6',
color: '#000000',
border: '3px solid #333333'
};
case 1: // Vermelho
return {
backgroundColor: '#dc2626',
color: '#ffffff',
border: '3px solid #000000'
};
case 2: // Preto
return {
backgroundColor: '#1f2937',
color: '#ffffff',
border: '3px solid #000000'
};
default:
return {
backgroundColor: '#6b7280',
color: '#ffffff',
border: '3px solid #000000'
};
}
};
const formatTime = (timestamp) => {
return new Date(timestamp).toLocaleTimeString('pt-BR');
};
if (loading && !blazeData) {
return (
<div className="min-h-screen bg-gray-900 flex items-center justify-center">
<div className="text-white text-xl animate-pulse">
🎯 Carregando Monitor Blaze...
</div>
</div>
);
}
return (
<div className="min-h-screen bg-gray-900 text-white">
{/* Header */}
<header className="bg-gray-800 border-b border-red-600 p-4">
<div className="max-w-7xl mx-auto flex items-center justify-between">
<div className="flex items-center space-x-4">
<div className="text-2xl font-bold text-red-500">🎯</div>
<h1 className="text-2xl font-bold bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
BLAZE MONITOR
</h1>
</div>
<div className="flex items-center space-x-4">
<div className={`flex items-center space-x-2 ${connected ? 'text-green-400' : 'text-red-400'}`}>
<div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
<span className="text-sm">{connected ? 'Online' : 'Offline'}</span>
</div>
<button
onClick={() => setAutoRefresh(!autoRefresh)}
className={`px-3 py-1 rounded text-sm ${autoRefresh ? 'bg-green-600' : 'bg-gray-600'}`}
>
Auto: {autoRefresh ? 'ON' : 'OFF'}
</button>
<button
onClick={fetchBlazeData}
className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded font-bold transition-colors"
>
🔄 Atualizar
</button>
</div>
</div>
</header>
<div className="max-w-7xl mx-auto p-6">
{/* Alertas */}
{alerts.length > 0 && (
<div className="mb-6">
<h2 className="text-xl font-bold mb-3 text-yellow-400">🚨 ALERTAS ATIVOS</h2>
<div className="space-y-2">
{alerts.map((alert, index) => (
<div key={index} className="bg-yellow-600 bg-opacity-20 border border-yellow-500 rounded-lg p-3">
<div className="flex items-start justify-between">
<span className="text-yellow-300 font-medium">{alert.message}</span>
<span className="text-yellow-400 text-sm ml-2">
{Math.round(alert.confidence * 100)}% confiança
</span>
</div>
</div>
))}
</div>
</div>
)}
{/* Título Principal */}
<div className="text-center mb-8">
<h2 className="text-4xl font-bold mb-2">BLAZE DOUBLE</h2>
<p className="text-gray-300">Últimos resultados em tempo real</p>
{blazeData && (
<p className="text-sm text-gray-400 mt-2">
Última atualização: {formatTime(blazeData.last_updated)}
</p>
)}
</div>
{/* Resultados */}
{blazeData && blazeData.results && (
<div className="mb-8">
<div className="bg-gray-800 rounded-lg p-6">
<h3 className="text-xl font-bold mb-4 text-center">ÚLTIMOS RESULTADOS</h3>
<div className="flex flex-wrap justify-center gap-3 mb-6">
{blazeData.results.slice(0, 15).map((result, index) => (
<div
key={index}
className="flex flex-col items-center"
>
<div
className="w-14 h-14 rounded-full flex items-center justify-center text-lg font-bold transition-transform hover:scale-110 shadow-lg"
style={getColorStyle(result.color)}
title={`${result.color_name} - ${result.number}`}
>
{result.number}
</div>
<span className="text-xs text-gray-400 mt-1">
{result.color_name}
</span>
</div>
))}
</div>
</div>
</div>
)}
{/* Estatísticas */}
{blazeData && blazeData.statistics && (
<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
{/* Vermelho */}
<div className="bg-red-600 bg-opacity-20 border border-red-500 rounded-lg p-6 text-center">
<div className="text-3xl mb-2">🔴</div>
<h3 className="text-xl font-bold mb-2">VERMELHO</h3>
<div className="text-3xl font-bold mb-1">{blazeData.statistics.red.count}</div>
<div className="text-lg">{blazeData.statistics.red.percentage.toFixed(1)}%</div>
<div className="text-sm text-gray-300 mt-2">Multiplicador: x2</div>
</div>
{/* Preto */}
<div className="bg-gray-700 bg-opacity-50 border border-gray-500 rounded-lg p-6 text-center">
<div className="text-3xl mb-2">⚫</div>
<h3 className="text-xl font-bold mb-2">PRETO</h3>
<div className="text-3xl font-bold mb-1">{blazeData.statistics.black.count}</div>
<div className="text-lg">{blazeData.statistics.black.percentage.toFixed(1)}%</div>
<div className="text-sm text-gray-300 mt-2">Multiplicador: x2</div>
</div>
{/* Branco */}
<div className="bg-gray-300 bg-opacity-20 border border-gray-300 rounded-lg p-6 text-center">
<div className="text-3xl mb-2">⚪</div>
<h3 className="text-xl font-bold mb-2">BRANCO</h3>
<div className="text-3xl font-bold mb-1">{blazeData.statistics.white.count}</div>
<div className="text-lg">{blazeData.statistics.white.percentage.toFixed(1)}%</div>
<div className="text-sm text-gray-300 mt-2">Multiplicador: x14</div>
</div>
</div>
)}
{/* Padrões Detectados */}
{blazeData && blazeData.patterns && blazeData.patterns.length > 0 && (
<div className="mb-8">
<h3 className="text-xl font-bold mb-4 text-center text-blue-400">🔍 PADRÕES DETECTADOS</h3>
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
{blazeData.patterns.map((pattern, index) => (
<div key={index} className="bg-blue-600 bg-opacity-20 border border-blue-500 rounded-lg p-4">
<div className="flex items-start justify-between">
<div>
<h4 className="font-bold text-blue-300">{pattern.pattern_type.toUpperCase()}</h4>
<p className="text-sm text-gray-300">{pattern.description}</p>
<p className="text-xs text-gray-400 mt-1">
Analisados: {pattern.results_analyzed} resultados
</p>
</div>
<div className="text-right">
<div className="text-lg font-bold text-blue-400">
{Math.round(pattern.confidence * 100)}%
</div>
<div className="text-xs text-gray-400">confiança</div>
</div>
</div>
</div>
))}
</div>
</div>
)}
{/* Dicas */}
<div className="bg-gray-800 rounded-lg p-6 text-center">
<h3 className="text-lg font-bold mb-3 text-yellow-400">💡 DICAS</h3>
<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
<div>
<strong>🎯 Estratégia Gale:</strong> Aumente a aposta após perder
</div>
<div>
<strong>📊 Análise de Padrões:</strong> Observe sequências e frequências
</div>
<div>
<strong>⚡ Tempo Real:</strong> Dados atualizados automaticamente
</div>
<div>
<strong>🚨 Alertas:</strong> Receba notificações de padrões detectados
</div>
</div>
</div>
</div>
</div>
);
};
const Home = () => {
return <BlazeMonitor />;
};
function App() {
return (
<div className="App">
<BrowserRouter>
<Routes>
<Route path="/" element={<Home />}>
<Route index element={<Home />} />
</Route>
</Routes>
</BrowserRouter>
</div>
);
}
export default App;
```
---
## 🎨 **FRONTEND - App.css**
```css
.App {
text-align: center;
}
/* Animações personalizadas */
@keyframes pulse-glow {
0%, 100% {
opacity: 1;
box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}
50% {
opacity: 0.8;
box-shadow: 0 0 20px rgba(239, 68, 68, 0.8);
}
}
.animate-pulse-glow {
animation: pulse-glow 2s ease-in-out infinite;
}
/* Hover effects para as bolinhas */
.result-ball {
transition: all 0.2s ease-in-out;
cursor: pointer;
}
.result-ball:hover {
transform: scale(1.1);
box-shadow: 0 8px 16px rgba(0,0,0,0.4);
}
/* Gradiente de fundo para cards */
.gradient-bg {
background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(31, 41, 55, 0.8) 100%);
backdrop-filter: blur(10px);
}
/* Animação de aparição para alertas */
@keyframes slideInDown {
from {
transform: translateY(-20px);
opacity: 0;
}
to {
transform: translateY(0);
opacity: 1;
}
}
.alert-slide-in {
animation: slideInDown 0.3s ease-out;
}
/* Loading spinner personalizado */
.loading-spinner {
border: 4px solid rgba(239, 68, 68, 0.1);
border-left: 4px solid #ef4444;
border-radius: 50%;
width: 40px;
height: 40px;
animation: spin 1s linear infinite;
}
@keyframes spin {
0% { transform: rotate(0deg); }
100% { transform: rotate(360deg); }
}
/* Estilo para números das bolinhas */
.result-number {
text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
font-weight: 900;
letter-spacing: -0.5px;
}
/* Cards responsivos */
@media (max-width: 768px) {
.result-ball {
width: 3rem;
height: 3rem;
font-size: 1rem;
}
.stat-card {
padding: 1rem;
}
}
/* Efeito neon para o título */
.neon-text {
text-shadow:
0 0 5px currentColor,
0 0 10px currentColor,
0 0 15px currentColor,
0 0 20px #ef4444;
}
/* Barra de progresso para confiança */
.confidence-bar {
height: 4px;
background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
border-radius: 2px;
overflow: hidden;
}
.confidence-fill {
height: 100%;
background: rgba(255,255,255,0.9);
transition: width 0.5s ease-in-out;
}
/* Hover effect para botões */
.btn-primary {
background: linear-gradient(135deg, #ef4444, #dc2626);
transition: all 0.2s ease-in-out;
}
.btn-primary:hover {
background: linear-gradient(135deg, #dc2626, #b91c1c);
transform: translateY(-1px);
box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}
/* Efeito para status online/offline */
.status-indicator {
position: relative;
}
.status-indicator::after {
content: '';
position: absolute;
top: 0;
left: 0;
right: 0;
bottom: 0;
border-radius: 50%;
animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}
.status-online::after {
background: rgba(34, 197, 94, 0.4);
}
.status-offline::after {
background: rgba(239, 68, 68, 0.4);
}
@keyframes ping {
75%, 100% {
transform: scale(2);
opacity: 0;
}
}
```
---
## 📦 **FRONTEND - package.json**
```json
{
"name": "frontend",
"version": "0.1.0",
"private": true,
"dependencies": {
"axios": "^1.8.4",
"cra-template": "1.2.0",
"react": "^19.0.0",
"react-dom": "^19.0.0",
"react-router-dom": "^7.5.1",
"react-scripts": "5.0.1"
},
"scripts": {
"start": "craco start",
"build": "craco build",
"test": "craco test",
"eject": "react-scripts eject"
},
"browserslist": {
"production": [
">0.2%",
"not dead",
"not op_mini all"
],
"development": [
"last 1 chrome version",
"last 1 firefox version",
"last 1 safari version"
]
},
"devDependencies": {
"@craco/craco": "^7.1.0",
"@eslint/js": "9.23.0",
"autoprefixer": "^10.4.20",
"eslint": "9.23.0",
"eslint-plugin-import": "2.31.0",
"eslint-plugin-jsx-a11y": "6.10.2",
"eslint-plugin-react": "7.37.4",
"globals": "15.15.0",
"postcss": "^8.4.49",
"tailwindcss": "^3.4.17"
}
}
```
---
## ⚙️ **ARQUIVOS DE CONFIGURAÇÃO**
### Backend .env
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="blaze_monitor"
CORS_ORIGINS="*"
```
### Frontend .env
```
REACT_APP_BACKEND_URL=http://localhost:8001
```
---
## 🚀 **COMANDOS PARA RODAR**
### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```
### Frontend
```bash
cd frontend
yarn install
yarn start
```
---
