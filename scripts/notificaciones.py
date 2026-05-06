import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============================================
# CONFIGURACIÓN — completar cuando tengas acceso
# =============================================
CORREO_ORIGEN  = "tucorreo@gmail.com"       # tu Gmail
CORREO_DESTINO = "cliente@empresa.com"      # correo del cliente
PASSWORD_APP   = "xxxx xxxx xxxx xxxx"      # contraseña de app Gmail

TELEGRAM_TOKEN   = "aqui_va_tu_token"       # token del bot de Telegram
TELEGRAM_CHAT_ID = "aqui_va_el_chat_id"     # ID del cliente en Telegram

# =============================================
# CANAL ACTIVO — cambia aquí según el cliente
# =============================================
CANAL = "email"  # opciones: "email" o "telegram"

# =============================================
# FUNCIÓN PRINCIPAL — no tocar
# =============================================
def enviar_alerta(mineral, precio, tipo, umbral):
    mensaje = f"""
    ⚠️ ALERTA DE PRECIO — MineralesBot
    
    Mineral  : {mineral}
    Precio   : ${precio}
    Tipo     : {"🔴 PRECIO ALTO" if tipo == "max" else "🟢 PRECIO BAJO"}
    Umbral   : ${umbral}
    
    Revise su estrategia de venta/compra.
    — MineralesBot
    """

    if CANAL == "email":
        _enviar_email(mineral, mensaje)
    elif CANAL == "telegram":
        _enviar_telegram(mensaje)
    else:
        print(f"⚠️ Canal '{CANAL}' no reconocido")

def _enviar_email(mineral, mensaje):
    try:
        msg = MIMEMultipart()
        msg["From"]    = CORREO_ORIGEN
        msg["To"]      = CORREO_DESTINO
        msg["Subject"] = f"⚠️ Alerta MineralesBot — {mineral}"
        msg.attach(MIMEText(mensaje, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(CORREO_ORIGEN, PASSWORD_APP)
            server.sendmail(CORREO_ORIGEN, CORREO_DESTINO, msg.as_string())

        print(f"✅ Correo enviado para {mineral}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

def _enviar_telegram(mensaje):
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje
        })
        print("✅ Telegram enviado")
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")