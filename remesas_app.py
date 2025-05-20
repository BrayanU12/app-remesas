import streamlit as st
import sqlite3
import os

DB_PATH = "remesas.db"

# Crear la base de datos si no existe
def crear_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

crear_db()

# Autenticación básica
USUARIOS = {
    "admin": "1234",
    "usuario": "sendify"
}

def autenticar(usuario, contrasena):
    return USUARIOS.get(usuario) == contrasena

# Autenticación de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Iniciar sesión")
    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if autenticar(usuario, contrasena):
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# Si ya está autenticado, mostramos la app
st.title("Sendify - App de Remesas")

nombre = st.text_input("Nombre del remitente")
email = st.text_input("Email del remitente")
pais = st.selectbox("País de destino", ["Colombia", "México", "Argentina"])
monto_usdt = st.number_input("Monto en USDT", min_value=0.0, step=1.0)

tasa_cop = 3900  # puedes luego hacer que esta tasa sea dinámica o por API
monto_cop = monto_usdt * tasa_cop

metodo_pago = st.selectbox("Método de pago", ["Nequi", "Daviplata", "Bancolombia"])

if st.button("Enviar Remesa"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, "Pago confirmado"))
    conn.commit()
    conn.close()
    st.success("Remesa registrada correctamente")

# Mostrar historial
st.subheader("Historial de Remesas")
conn = sqlite3.connect(DB_PATH)
remesas = conn.execute("SELECT nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado FROM remesas").fetchall()
conn.close()

if remesas:
    for r in remesas:
        st.write(f"👤 {r[0]} ({r[1]}) - {r[2]}")
        st.write(f"💸 {r[3]} USDT = {r[4]} COP")
        st.write(f"🏦 Método: {r[5]} | Estado: {r[6]}")
        st.markdown("---")
else:
    st.info("No hay remesas registradas aún.")

