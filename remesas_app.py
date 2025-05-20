import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = "remesas.db"

# Crear la base de datos si no existe
def crear_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
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
    conn.commit()
    conn.close()

# Guardar datos en la base de datos
def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado))
    conn.commit()
    conn.close()

# Mostrar los registros
def mostrar_registros():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM remesas", conn)
    conn.close()
    return df

# Inicializar base de datos si no existe
if not os.path.exists(DB_PATH):
    crear_db()

# Interfaz Streamlit
st.title("💸 Plataforma de Envío de Remesas - Sendify")

st.header("📨 Enviar Dinero")
with st.form(key="formulario_remesas"):
    nombre = st.text_input("Nombre completo")
    email = st.text_input("Correo electrónico")
    pais = st.selectbox("País de destino", ["Colombia", "México", "Argentina", "Perú"])
    monto_usdt = st.number_input("Monto en USDT", min_value=1.0, format="%.2f")
    metodo_pago = st.selectbox("Método de pago", ["Nequi", "Bancolombia", "Daviplata"])

    tasa_conversion = 3900  # Ejemplo estático, 1 USDT = 3900 COP
    monto_cop = monto_usdt * tasa_conversion

    st.markdown(f"💱 Monto a entregar: **{monto_cop:,.0f} COP**")

    boton_enviar = st.form_submit_button("Enviar")

    if boton_enviar:
        guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, "Pago confirmado")
        st.success("✅ Transacción registrada exitosamente.")
        st.info("🔒 Estado actual: Pago confirmado.")

st.divider()
st.subheader("📊 Historial de Transacciones")
df_registros = mostrar_registros()
st.dataframe(df_registros, use_container_width=True)
