import streamlit as st
import sqlite3
import pandas as pd
import time
import os

DB_PATH = "remesas.db"

# Crear tabla si no existe
def crear_tabla():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS remesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                email TEXT,
                pais TEXT,
                monto_usdt REAL,
                monto_cop REAL,
                metodo_pago TEXT,
                estado TEXT
            )
        ''')

# Guardar en base de datos
def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado))

st.title("📤 Sendify - Envío de Remesas Simulado")

crear_tabla()

with st.form("formulario_remesa"):
    nombre = st.text_input("👤 Nombre completo")
    email = st.text_input("📧 Correo electrónico")
    pais = st.selectbox("🌍 País destino", ["Colombia", "México", "Argentina", "Perú"])
    monto_usdt = st.number_input("💸 Monto a enviar (USDT)", min_value=0.0, step=0.5)
    metodo_pago = st.selectbox("💳 Método de pago", ["Binance Pay", "MetaMask", "PayPal", "Otro"])

    submitted = st.form_submit_button("Iniciar pago")

# Simular procesamiento de pago
if submitted:
    if not nombre or not email or monto_usdt <= 0:
        st.warning("⚠️ Por favor completa todos los campos antes de iniciar el pago.")
    else:
        with st.spinner("🔄 Procesando pago..."):
            time.sleep(3)  # Simula tiempo de pago
        st.success(f"✅ Pago por {metodo_pago} recibido.")
        aprobar = st.button("✅ Aprobar y enviar remesa")
        if aprobar:
            tasa = 4000  # Simula TRM
            monto_cop = monto_usdt * tasa
            guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, "Aprobado")
            st.success(f"💰 Remesa de {monto_cop:,.0f} COP enviada exitosamente a {pais}.")

# Mostrar historial
if st.checkbox("📄 Ver historial de remesas"):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM remesas", conn)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("⚠️ Aún no hay remesas registradas.")
