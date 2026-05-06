import yfinance as yf
import pandas as pd
import psycopg2
from datetime import datetime
from notificaciones import enviar_alerta

# =============================================
# CONFIGURACIÓN DE UMBRALES POR CLIENTE
# =============================================
UMBRALES = {
    "Cobre": {"min": 5.50, "max": 6.50},
    "Oro":   {"min": 4000, "max": 5000},
    "Plata": {"min": 60,   "max": 80},
    "Zinc":  {"min": 2000, "max": 2800},
    "WTI":   {"min": 80,   "max": 110},
    "Brent": {"min": 85,   "max": 115}
}

# =============================================
# TICKERS
# =============================================
TICKERS = {
    "Cobre": "HG=F",
    "Oro":   "GC=F",
    "Plata": "SI=F",
    "Zinc":  "ZNC=F",
    "WTI":   "CL=F",
    "Brent": "BZ=F"
}

# =============================================
# PASO 1 — Extraer precios
# =============================================
print("📡 Extrayendo precios...")
datos = []

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
            print(f"  ✅ {nombre}: ${ultimo:.2f} ({variacion:+.2f}%)")
    except Exception as e:
        print(f"  ❌ Error con {nombre}: {e}")

df = pd.DataFrame(datos)

# =============================================
# PASO 2 — Guardar en PostgreSQL
# =============================================
print("\n💾 Guardando en base de datos...")
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
    print("  ✅ Datos guardados correctamente")
except Exception as e:
    print(f"  ❌ Error en base de datos: {e}")

# =============================================
# PASO 3 — Verificar umbrales y enviar alertas
# =============================================
print("\n🔔 Verificando alertas...")
alertas_enviadas = 0

for _, fila in df.iterrows():
    mineral = fila["mineral"]
    precio  = fila["precio"]

    if mineral in UMBRALES:
        if precio >= UMBRALES[mineral]["max"]:
            print(f"  🔴 {mineral} superó umbral máximo (${UMBRALES[mineral]['max']})")
            enviar_alerta(mineral, precio, "max", UMBRALES[mineral]["max"])
            alertas_enviadas += 1
        elif precio <= UMBRALES[mineral]["min"]:
            print(f"  🟢 {mineral} bajó del umbral mínimo (${UMBRALES[mineral]['min']})")
            enviar_alerta(mineral, precio, "min", UMBRALES[mineral]["min"])
            alertas_enviadas += 1

if alertas_enviadas == 0:
    print("  ✅ Sin alertas — precios dentro de rangos normales")

print(f"\n🏁 Pipeline completado — {datetime.now().strftime('%Y-%m-%d %H:%M')}")