import streamlit as st
import sqlite3
import os
import pandas as pd
import smtplib
from email.message import EmailMessage

# Configuración del email
EMAIL_ORIGEN = "urrutiab67@gmail.com"
EMAIL_APP_PASSWORD = "mgpr bgwa jrwg njnr"

DB_PATH = "remesas.db"

# Inicializar DB si no existe
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS remesas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            correo TEXT NOT NULL,
                            monto REAL NOT NULL,
                            estado TEXT DEFAULT 'Pendiente')''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL)''')
        conn.commit()

# Autenticación
def autenticar_usuario(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone() is not None

# Insertar nueva remesa
def insertar_remesa(nombre, correo, monto):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO remesas (nombre, correo, monto) VALUES (?, ?, ?)", (nombre, correo, monto))
        conn.commit()

# Obtener todas las remesas
def obtener_remesas():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM remesas", conn)

# Actualizar estado de remesa
def actualizar_estado_remesa(id_remesa, nuevo_estado):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE remesas SET estado = ? WHERE id = ?", (nuevo_estado, id_remesa))
        conn.commit()

# Enviar correo de notificación
def enviar_correo_estado(email_destino, nombre, nuevo_estado, id_remesa):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Actualización de tu remesa #{id_remesa}"
        msg["From"] = EMAIL_ORIGEN
        msg["To"] = email_destino
        msg.set_content(f"""
Hola {nombre},

Tu remesa #{id_remesa} ha sido actualizada.

Nuevo estado: {nuevo_estado}

Gracias por usar nuestra plataforma.

Saludos,
Equipo de Remesas
        """)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ORIGEN, EMAIL_APP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# UI - Panel Admin
def mostrar_panel_admin():
    st.title("Panel de Administración")
    df = obtener_remesas()
    for _, row in df.iterrows():
        id, nombre, email, monto, estado = row
        st.write(f"### Remesa #{id}")
        st.write(f"**Nombre:** {nombre}  |  **Email:** {email}  |  **Monto:** ${monto}  |  **Estado actual:** {estado}")
        nuevo_estado = st.selectbox(
            f"Actualizar estado (Remesa #{id})",
            ["Pendiente", "Aprobado", "Rechazado"],
            index=["Pendiente", "Aprobado", "Rechazado"].index(estado),
            key=f"estado_{id}"
        )
        if st.button(f"Actualizar estado #{id}"):
            actualizar_estado_remesa(id, nuevo_estado)
            enviar_correo_estado(email, nombre, nuevo_estado, id)
            st.success("Estado actualizado y correo enviado correctamente.")
            st.rerun()

    if st.button("Descargar base de datos en CSV"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV", csv, "remesas.csv", "text/csv")

# UI - App principal
def main():
    st.set_page_config(page_title="App de Remesas")
    st.sidebar.title("Menú")
    menu = st.sidebar.selectbox("Selecciona una opción", ["Enviar Remesa", "Administrador"])

    if menu == "Enviar Remesa":
        st.title("Enviar Remesa")
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        monto = st.number_input("Monto a enviar", min_value=1.0)
        if st.button("Enviar"):
            insertar_remesa(nombre, correo, monto)
            st.success("Remesa enviada exitosamente.")

    elif menu == "Administrador":
        st.title("Inicio de Sesión Administrador")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if autenticar_usuario(usuario, clave):
                st.session_state["admin_autenticado"] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

        if st.session_state.get("admin_autenticado"):
            mostrar_panel_admin()

if __name__ == "__main__":
    init_db()
    main()


