import streamlit as st
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuración de la base de datos ---
def crear_tabla():
    conn = sqlite3.connect("remesas.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nombre TEXT,
            email TEXT,
            pais TEXT,
            monto_usdt REAL,
            monto_cop REAL
        )
    ''')
    conn.commit()
    conn.close()

def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop):
    conn = sqlite3.connect("remesas.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacciones (fecha, nombre, email, pais, monto_usdt, monto_cop)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nombre, email, pais, monto_usdt, monto_cop))
    conn.commit()
    conn.close()

def obtener_transacciones():
    conn = sqlite3.connect("remesas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacciones ORDER BY fecha DESC")
    filas = cursor.fetchall()
    conn.close()
    return filas

# --- Enviar correo ---
def enviar_correo(destinatario_email, nombre, monto_usdt, monto_cop):
    remitente = "urrutiab67@gmail.com"
    password = "zuew psyg izxd hpdk"

    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = "Confirmación de Remesa"
    mensaje["From"] = remitente
    mensaje["To"] = destinatario_email

    texto = f"""Hola {nombre},

Has recibido una remesa por {monto_usdt} USDT.
Equivalente a: {monto_cop:,.0f} COP.

Gracias por usar nuestra plataforma.
"""
    mensaje.attach(MIMEText(texto, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario_email, mensaje.as_string())
        servidor.quit()
        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False

# --- Inicio de la App ---
st.set_page_config(page_title="Plataforma de Remesas Cripto", page_icon="💸")
st.title("💸 Plataforma de Remesas con Criptomonedas")
st.markdown("Simula el envío de dinero usando USDT de forma rápida y económica.")

# Crear tabla en DB si no existe
crear_tabla()

# Función para tasa de cambio simulada
def obtener_tasa_cop():
    return 4323

# Formulario
with st.form("formulario_remesas"):
    st.subheader("📨 Datos del destinatario")

    nombre = st.text_input("Nombre del destinatario")
    email = st.text_input("Email del destinatario")
    pais = st.selectbox("País de destino", ["Colombia", "México", "Perú", "Venezuela", "Otro"])
    monto = st.number_input("Monto a enviar en USDT", min_value=1.0, step=1.0)

    enviar = st.form_submit_button("Simular envío")

    if enviar:
        tasa = obtener_tasa_cop()

        # 1. Calcular comisión
        if monto < 50:
            comision = 1.0  # Comisión fija
            tipo_comision = "Fija (1 USDT)"
        else:
            comision = monto * 0.02  # 2%
            tipo_comision = "2% del monto"

        monto_neto = monto - comision
        monto_en_cop = monto_neto * tasa

        # 2. Mostrar resultados al usuario
        st.success("✅ Transacción simulada")
        st.write(f"**Destinatario:** {nombre} ({email} - {pais})")
        st.write(f"**Enviado:** {monto:.2f} USDT")
        st.write(f"**Tipo de comisión:** {tipo_comision}")
        st.write(f"**Comisión aplicada:** {comision:.2f} USDT")
        st.write(f"**Monto neto a recibir:** {monto_neto:.2f} USDT")
        st.write(f"**Tasa de cambio:** 1 USDT = {tasa:,} COP")
        st.write(f"**Total en COP:** {monto_en_cop:,.0f} COP")

        # 3. Registrar y enviar correo
        guardar_en_db(nombre, email, pais, monto, monto_en_cop)
        st.success("✔️ Transacción registrada")

        enviado = enviar_correo(email, nombre, monto, monto_en_cop)
        if enviado:
            st.success("📨 Correo enviado correctamente")
        else:
            st.warning("⚠️ No se pudo enviar el correo")

# Mostrar historial con filtros
st.subheader("📊 Historial de Envíos")

# Obtener todos los datos
transacciones = obtener_transacciones()

if transacciones:
    import pandas as pd

    df = pd.DataFrame(transacciones, columns=["ID", "Fecha", "Nombre", "Email", "País", "USDT", "COP"])

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_nombre = st.text_input("Filtrar por nombre")
    with col2:
        filtro_email = st.text_input("Filtrar por email")
    with col3:
        filtro_pais = st.selectbox("Filtrar por país", options=["Todos"] + sorted(df["País"].unique().tolist()))

    # Aplicar filtros
    if filtro_nombre:
        df = df[df["Nombre"].str.contains(filtro_nombre, case=False)]
    if filtro_email:
        df = df[df["Email"].str.contains(filtro_email, case=False)]
    if filtro_pais != "Todos":
        df = df[df["País"] == filtro_pais]

    st.dataframe(df, use_container_width=True)
else:
    st.info("Aún no hay transacciones registradas.")


conn = sqlite3.connect("remesas.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE transacciones ADD COLUMN estado TEXT DEFAULT 'Pendiente'")
conn.commit()
conn.close()

