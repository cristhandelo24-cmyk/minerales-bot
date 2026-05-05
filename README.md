# ⛏️ MineralesBot

Pipeline ETL + Dashboard + Chatbot IA para monitoreo de precios de minerales e hidrocarburos en Perú.

## 🚀 ¿Qué hace?

- Extrae precios en tiempo real de Cobre, Oro, Plata, Zinc, WTI y Brent
- Almacena historial en PostgreSQL
- Dashboard web interactivo con gráficos
- Chatbot en español con IA (Groq + LLaMA 3.3)
- Alertas automáticas por correo o Telegram
- Pipeline automatizado con n8n cada día a las 8am

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Extracción | Python + yfinance |
| Transformación | Pandas |
| Almacenamiento | PostgreSQL (Docker) |
| API | FastAPI |
| Dashboard | Streamlit + Plotly |
| Chatbot IA | Groq + LLaMA 3.3 70B |
| Automatización | n8n |
| Seguridad | python-dotenv |

## 📁 Estructura del proyecto
minerales_bot/
├── notebooks/
│   └── 01_extraccion_precios.ipynb
├── scripts/
│   ├── api.py
│   ├── chatbot.py
│   ├── dashboard.py
│   ├── notificaciones.py
│   └── pipeline_completo.py
├── .env.example
├── .gitignore
└── README.md
## ⚙️ Instalación

1. Clona el repositorio
```bash
git clone https://github.com/cristhandelo24-cmyk/minerales-bot.git
cd minerales-bot
```

2. Instala las dependencias
```bash
python -m pip install yfinance pandas psycopg2-binary python-dotenv streamlit plotly fastapi uvicorn groq
```

3. Copia el archivo de variables de entorno
```bash
cp .env.example .env
```

4. Completa el archivo `.env` con tus credenciales

5. Levanta PostgreSQL con Docker
```bash
docker-compose up -d
```

6. Ejecuta el dashboard
```bash
python -m streamlit run scripts/dashboard.py
```

## 🎯 Casos de uso

- Gerentes de empresas mineras medianas en Perú
- Traders de concentrados de minerales
- Consultoras del sector energético
- Empresas proveedoras de hidrocarburos

## 👨‍💻 Autor

Desarrollado por **craqman11** — Data Engineering student at Tecsup, Peru.