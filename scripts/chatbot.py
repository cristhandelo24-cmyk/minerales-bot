from groq import Groq
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# =============================================
# CARGAR VARIABLES DE ENTORNO
# =============================================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_HOST      = os.getenv("DB_HOST")
DB_PORT      = os.getenv("DB_PORT")
DB_NAME      = os.getenv("DB_NAME")
DB_USER      = os.getenv("DB_USER")
DB_PASSWORD  = os.getenv("DB_PASSWORD")

client = Groq(api_key=GROQ_API_KEY)

# =============================================
# OBTENER PRECIOS DESDE POSTGRESQL
# =============================================
def obtener_precios():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    df = pd.read_sql("""
        SELECT DISTINCT ON (mineral) mineral, precio, variacion_pct, fecha
        FROM precios_minerales
        ORDER BY mineral, fecha DESC
    """, conn)
    conn.close()
    return df

# =============================================
# CONSTRUIR CONTEXTO CON DATOS REALES
# =============================================
def construir_contexto():
    df = obtener_precios()
    contexto = "Estos son los precios actuales de minerales e hidrocarburos:\n\n"
    for _, fila in df.iterrows():
        signo = "+" if fila["variacion_pct"] > 0 else ""
        contexto += f"- {fila['mineral']}: ${fila['precio']} ({signo}{fila['variacion_pct']}% variación)\n"
    contexto += f"\nFecha de datos: {df['fecha'].max()}"
    return contexto

# =============================================
# CHATBOT
# =============================================
def chatbot(pregunta_usuario):
    contexto = construir_contexto()

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""Eres MineralesBot, un asistente experto en precios de minerales 
                e hidrocarburos para empresas peruanas. Respondes en español de forma clara 
                y concisa. Usas los siguientes datos reales para responder:
                
                {contexto}
                
                Si te preguntan algo que no está en los datos, dilo honestamente.
                Cuando menciones precios usa el símbolo $ y cuando menciones variaciones 
                usa % con flecha ↑ o ↓."""
            },
            {
                "role": "user",
                "content": pregunta_usuario
            }
        ],
        temperature=0.3,
        max_tokens=500
    )

    return respuesta.choices[0].message.content

# =============================================
# PRUEBA EN TERMINAL
# =============================================
if __name__ == "__main__":
    print("🤖 MineralesBot — Escribe tu pregunta (o 'salir' para terminar)\n")
    while True:
        pregunta = input("Tú: ")
        if pregunta.lower() == "salir":
            break
        respuesta = chatbot(pregunta)
        print(f"\nMineralesBot: {respuesta}\n")