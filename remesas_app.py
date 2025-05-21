import streamlit as st
import sqlite3
import os

DB_PATH = "remesas.db"

# Crear base de datos y tablas si no existen
def inicializar_db():
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
            estado TEXT DEFAULT 'Pendiente'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    # Crear un usuario admin si no existe
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ('admin', 'admin123'))

    conn.commit()
    conn.close()

def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado))
    conn.commit()
    conn.close()

def obtener_remesas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM remesas")
    data = cursor.fetchall()
    conn.close()
    return data

def actualizar_estado_remesa(remesa_id, nuevo_estado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE remesas SET estado = ? WHERE id = ?", (nuevo_estado, remesa_id))
    conn.commit()
    conn.close()

def autenticar_usuario(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def mostrar_panel_admin():
    st.subheader("Panel de Administración")
    remesas = obtener_remesas()

    for remesa in remesas:
        id, nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado = remesa
        with st.expander(f"Remesa #{id} - {nombre} ({estado})"):
            st.write(f"Correo: {email}")
            st.write(f"País: {pais}")
            st.write(f"Monto USDT: {monto_usdt}")
            st.write(f"Monto en COP: {monto_cop}")
            st.write(f"Método de pago: {metodo_pago}")

            nuevo_estado = st.selectbox(
                f"Actualizar estado (Remesa #{id})",
                ["Pendiente", "Aprobado", "Rechazado"],
                index=["Pendiente", "Aprobado", "Rechazado"].index(estado),
                key=f"estado_{id}"
            )

            if st.button(f"Actualizar estado #{id}"):
                actualizar_estado_remesa(id, nuevo_estado)
                st.success("Estado actualizado")
                # Marcar actualización para forzar rerun en main()
                st.session_state["actualizado"] = True


def main():
    st.set_page_config(page_title="App de Remesas", layout="centered")
    inicializar_db()

    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    st.title("Remesas USDT a Colombia")
    menu = ["Enviar Remesa", "Administrador"]
    opcion = st.sidebar.radio("Menú", menu)

    if opcion == "Enviar Remesa":
        # Formulario normal...
        pass

    elif opcion == "Administrador":
        st.subheader("Login de Administrador")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            if autenticar_usuario(usuario, clave):
                st.session_state.autenticado = True
                st.success("Inicio de sesión exitoso")
                st.session_state.mostrar_admin = True
            else:
                st.error("Credenciales incorrectas")

        if st.session_state.get("autenticado", False) and st.session_state.get("mostrar_admin", False):
            mostrar_panel_admin()

    # 🔁 Lanzar rerun de forma segura luego de terminar la ejecución de main
    if st.session_state.get("actualizado", False):
        st.session_state["actualizado"] = False
        st.experimental_rerun()


if __name__ == "__main__":
    main()



