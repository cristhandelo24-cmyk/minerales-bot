from fastapi import FastAPI
from datetime import datetime
import yfinance as yf
import pandas as pd
import psycopg2

app = FastAPI()

TICKERS = {
    "Cobre": "HG=F",
    "Oro":   "GC=F",
    "Plata": "SI=F",
    "Zinc":  "ZNC=F",
    "WTI":   "CL=F",
    "Brent": "BZ=F"
}

UMBRALES = {
    "Cobre": {"min": 5.50, "max": 6.50},
    "Oro":   {"min": 4000, "max": 5000},
    "Plata": {"min": 60,   "max": 80},
    "Zinc":  {"min": 2000, "max": 2800},
    "WTI":   {"min": 80,   "max": 110},
    "Brent": {"min": 85,   "max": 115}
}

@app.get("/")
def home():
    return {"status": "MineralesBot API corriendo ✅"}

@app.get("/ejecutar-pipeline")
def ejecutar_pipeline():
    datos = []
    alertas = []

    # Extraer precios
    for nombre, ticker in TICKERS.items():
        try:
            activo = yf.Ticker(ticker)
            hist = activo.history(period="7d")
            if not hist.empty:
                ultimo = hist["Close"].iloc[-1]
                anterior = hist["Close"].iloc[-2] if len(hist) > 1 else ultimo
                variacion = ((ultimo - anterior) / anterior) * 100
                datos.append({
                    "mineral":       nombre,
                    "precio":        round(ultimo, 2),
                    "variacion_pct": round(variacion, 2),
                    "fecha":         datetime.now()
                })
        except Exception as e:
            print(f"Error con {nombre}: {e}")

    df = pd.DataFrame(datos)

    # Guardar en PostgreSQL
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            database="minerales_bot",
            user="admin",
            password="admin123"
        )
        cursor = conn.cursor()
        for _, fila in df.iterrows():
            cursor.execute("""
                INSERT INTO precios_minerales (mineral, precio, variacion_pct, fecha)
                VALUES (%s, %s, %s, %s)
            """, (fila["mineral"], fila["precio"], fila["variacion_pct"], fila["fecha"]))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

    # Verificar alertas
    for _, fila in df.iterrows():
        mineral = fila["mineral"]
        precio  = fila["precio"]
        if mineral in UMBRALES:
            if precio >= UMBRALES[mineral]["max"]:
                alertas.append(f"🔴 {mineral} en ${precio} — superó máximo ${UMBRALES[mineral]['max']}")
            elif precio <= UMBRALES[mineral]["min"]:
                alertas.append(f"🟢 {mineral} en ${precio} — bajó mínimo ${UMBRALES[mineral]['min']}")

    return {
        "status":   "ok",
        "fecha":    datetime.now().strftime("%Y-%m-%d %H:%M"),
        "precios":  datos,
        "alertas":  alertas if alertas else ["Sin alertas — precios dentro de rangos normales"]
    }