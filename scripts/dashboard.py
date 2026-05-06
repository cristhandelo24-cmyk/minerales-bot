import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime
from groq import Groq
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

st.set_page_config(
    page_title="MineralesBot — Dashboard",
    page_icon="⛏️",
    layout="wide"
)

# =============================================
# CONEXIÓN A POSTGRESQL
# =============================================
def get_conexion():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_data():
    conn = get_conexion()
    df = pd.read_sql(
        "SELECT * FROM precios_minerales ORDER BY fecha DESC",
        conn
    )
    conn.close()
    return df

def obtener_ultimos():
    conn = get_conexion()
    df = pd.read_sql("""
        SELECT DISTINCT ON (mineral) mineral, precio, variacion_pct, fecha
        FROM precios_minerales
        ORDER BY mineral, fecha DESC
    """, conn)
    conn.close()
    return df

# =============================================
# CHATBOT
# =============================================
def construir_contexto(df):
    contexto = "Precios actuales de minerales e hidrocarburos:\n\n"
    for _, fila in df.iterrows():
        signo = "+" if fila["variacion_pct"] > 0 else ""
        contexto += f"- {fila['mineral']}: ${fila['precio']} ({signo}{fila['variacion_pct']}%)\n"
    return contexto

def responder(pregunta, contexto):
    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""Eres MineralesBot, asistente experto en precios de minerales 
                e hidrocarburos para empresas peruanas. Respondes en español, 
                de forma clara y concisa. Datos actuales:
                
                {contexto}"""
            },
            {"role": "user", "content": pregunta}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return respuesta.choices[0].message.content

# =============================================
# INTERFAZ
# =============================================
st.title("⛏️ MineralesBot")
st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.divider()

df_completo = get_data()
df_ultimos  = obtener_ultimos()
contexto    = construir_contexto(df_ultimos)

tab1, tab2 = st.tabs(["📊 Dashboard", "🤖 Chat"])

# =============================================
# TAB 1: DASHBOARD
# =============================================
with tab1:
    st.subheader("Precios actuales")
    cols = st.columns(len(df_ultimos))
    for i, (_, fila) in enumerate(df_ultimos.iterrows()):
        cols[i].metric(
            label=fila["mineral"],
            value=f"${fila['precio']}",
            delta=f"{fila['variacion_pct']:+.2f}%"
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Variaciones del día")
        fig = px.bar(
            df_ultimos,
            x="mineral",
            y="variacion_pct",
            color="variacion_pct",
            color_continuous_scale=["red", "gray", "green"],
            labels={"variacion_pct": "Variación %", "mineral": "Mineral"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Historial completo")
        st.dataframe(
            df_completo[["mineral", "precio", "variacion_pct", "fecha"]],
            use_container_width=True
        )

# =============================================
# TAB 2: CHATBOT
# =============================================
with tab2:
    st.subheader("🤖 Pregúntale a MineralesBot")
    st.caption("Escribe en español — responde con datos reales de tu base de datos")

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [
            {
                "role": "assistant",
                "content": "Hola, soy MineralesBot ⛏️ Pregúntame sobre precios de cobre, oro, plata, zinc, WTI o Brent."
            }
        ]

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if pregunta := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.mensajes.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.write(pregunta)

        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                respuesta = responder(pregunta, contexto)
            st.write(respuesta)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta})