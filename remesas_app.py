import streamlit as st
import pandas as pd
import sqlite3
import os

# Crear conexión a la base de datos
DB_PATH = "remesas.db"

def crear_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS remesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                email TEXT,
                pais TEXT,
                monto_usdt REAL,
                monto_cop REAL
            )
        ''')
        conn.commit()

def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, email, pais, monto_usdt, monto_cop))
        conn.commit()

# Crear base de datos si no existe
crear_db()

# Interfaz Streamlit
st.title("📤 Plataforma de Envío de Remesas - Sendify")

st.subheader("🧾 Ingresa los datos de la remesa")

with st.form("remesa_form"):
    nombre = st.text_input("Nombre del remitente")
    email = st.text_input("Email del remitente")
    pais = st.selectbox("País receptor", ["Colombia", "México", "Perú", "Argentina"])
    monto_usdt = st.number_input("Monto a enviar (USDT)", min_value=0.0, format="%.2f")

    tasa_cop = 3800
    monto_cop = monto_usdt * tasa_cop

    st.markdown(f"💱 Tasa estimada: 1 USDT = {tasa_cop} COP")
    st.markdown(f"💰 Recibirás aproximadamente: **{monto_cop:,.2f} COP**")

    enviar = st.form_submit_button("Enviar remesa")

    if enviar:
        if nombre and email and monto_usdt > 0:
            guardar_en_db(nombre, email, pais, monto_usdt, monto_cop)
            st.success("✅ Remesa enviada correctamente.")
        else:
            st.error("❌ Por favor completa todos los campos.")

# Mostrar datos
if st.checkbox("📄 Ver historial de remesas"):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM remesas", conn)
        st.dataframe(df)
