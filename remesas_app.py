import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ---------- FUNCIONES DE BASE DE DATOS ----------

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
            monto_cop REAL,
            estado TEXT DEFAULT 'Pendiente'
        )
    ''')
    conn.commit()
    conn.close()

def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop):
    conn = sqlite3.connect("remesas.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacciones (fecha, nombre, email, pais, monto_usdt, monto_cop, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nombre, email, pais, monto_usdt, monto_cop, "Pendiente"))
    conn.commit()
    conn.close()

def obtener_transacciones():
    conn = sqlite3.connect("remesas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacciones ORDER BY fecha DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def actualizar_estado(id_transaccion, nuevo_estado):
    conn = sqlite3.connect("remesas.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE transacciones SET estado = ? WHERE id = ?", (nuevo_estado, id_transaccion))
    conn.commit()
    conn.close()

# ---------- INTERFAZ ----------

st.set_page_config(page_title="Sendify - Envío de Remesas", layout="centered")
st.title("💸 Sendify - Envío de Remesas Internacionales")

crear_tabla()

menu = st.sidebar.selectbox("Selecciona una opción", ["Nueva Transacción", "Historial de Transacciones"])

if menu == "Nueva Transacción":
    st.header("📤 Nueva Transacción")
    
    nombre = st.text_input("Nombre del destinatario")
    email = st.text_input("Email del destinatario")
    pais = st.selectbox("País destino", ["Colombia", "México", "Argentina", "Perú", "Chile"])
    monto_usdt = st.number_input("Monto en USDT a enviar", min_value=1.0)
    
    tasa_cambio = 3900  # puedes reemplazarlo por una tasa en tiempo real
    monto_cop = monto_usdt * tasa_cambio

    st.write(f"💰 Monto aproximado en moneda local (COP): {monto_cop:,.2f}")

    if st.button("Enviar Remesa"):
        if nombre and email:
            guardar_en_db(nombre, email, pais, monto_usdt, monto_cop)
            st.success("✅ Transacción registrada correctamente. Estado: Pendiente.")
        else:
            st.error("❗Por favor, completa todos los campos.")

elif menu == "Historial de Transacciones":
    st.header("📑 Historial de Transacciones")

    data = obtener_transacciones()
    if data:
        df = pd.DataFrame(data, columns=["ID", "Fecha", "Nombre", "Email", "País", "USDT", "COP", "Estado"])

        for i, row in df.iterrows():
            with st.expander(f"📦 Transacción #{row['ID']} - {row['Nombre']} ({row['Estado']})"):
                st.write(f"📅 Fecha: {row['Fecha']}")
                st.write(f"✉️ Email: {row['Email']}")
                st.write(f"🌍 País: {row['País']}")
                st.write(f"💸 Monto USDT: {row['USDT']}")
                st.write(f"💵 Monto Local (COP): {row['COP']:,.2f}")
                nuevo_estado = st.selectbox(
                    f"Cambiar estado",
                    options=["Pendiente", "Aprobado", "Rechazado"],
                    index=["Pendiente", "Aprobado", "Rechazado"].index(row["Estado"]),
                    key=f"estado_{row['ID']}"
                )
                if nuevo_estado != row["Estado"]:
                    if st.button(f"Actualizar estado de #{row['ID']}", key=f"btn_{row['ID']}"):
                        actualizar_estado(row["ID"], nuevo_estado)
                        st.success(f"✅ Estado actualizado a {nuevo_estado}. Recarga para ver el cambio.")
    else:
        st.info("Aún no hay transacciones registradas.")


