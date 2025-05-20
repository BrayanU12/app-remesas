import streamlit as st
import sqlite3
import os

# Ruta de la base de datos
DB_PATH = "remesas.db"

# Crear base de datos y tabla si no existen
def crear_base_datos():
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
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Crear un usuario admin si no existe
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

# Guardar remesa
def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado="Pendiente"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado))
    conn.commit()
    conn.close()

# Autenticación
def autenticar_usuario(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Panel de administrador
def mostrar_panel_admin():
    st.subheader("Panel de Administración")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM remesas")
    remesas = cursor.fetchall()

    estados_posibles = ["Pendiente", "Aprobado", "Rechazado"]

    for remesa in remesas:
        id, nombre, email, pais, usdt, cop, metodo, estado = remesa
        st.write(f"**#{id}** | {nombre} | {email} | {pais} | {usdt} USDT | {cop} COP | Método: {metodo} | Estado: {estado}")

        indice_estado = estados_posibles.index(estado) if estado in estados_posibles else 0

        nuevo_estado = st.selectbox(
            f"Actualizar estado (Remesa #{id})",
            estados_posibles,
            index=indice_estado,
            key=f"estado_{id}"
        )

        if nuevo_estado != estado:
            cursor.execute("UPDATE remesas SET estado = ? WHERE id = ?", (nuevo_estado, id))
            conn.commit()
            st.success(f"Estado actualizado a {nuevo_estado} para la remesa #{id}")

    conn.close()

# Formulario de remesas
def mostrar_formulario_remesas():
    st.subheader("Enviar Remesa")

    nombre = st.text_input("Nombre completo")
    email = st.text_input("Correo electrónico")
    pais = st.selectbox("País destino", ["Colombia", "Venezuela", "México", "Perú"])
    monto_usdt = st.number_input("Monto en USDT", min_value=0.0)
    tasa_cambio = 4000  # Por ejemplo
    monto_cop = monto_usdt * tasa_cambio
    metodo_pago = st.selectbox("Método de pago", ["Nequi", "Daviplata", "Bancolombia", "Efecty"])

    st.write(f"Monto aproximado a recibir: **{monto_cop:,.0f} COP**")

    if st.button("Enviar remesa"):
        if nombre and email and monto_usdt > 0:
            guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago)
            st.success("Remesa registrada exitosamente. Estado: Pendiente.")
        else:
            st.warning("Por favor completa todos los campos.")

# Página principal
def main():
    st.title("Sendify – Plataforma de Envío de Remesas")

    # Crear base de datos al iniciar
    if not os.path.exists(DB_PATH):
        crear_base_datos()

    menu = ["Inicio", "Administrador"]
    opcion = st.sidebar.selectbox("Navegación", menu)

    if opcion == "Inicio":
        mostrar_formulario_remesas()

    elif opcion == "Administrador":
        st.subheader("Iniciar sesión")

        if "autenticado" not in st.session_state:
            st.session_state.autenticado = False

        if not st.session_state.autenticado:
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if autenticar_usuario(usuario, clave):
                    st.session_state.autenticado = True
                    st.experimental_rerun()
                else:
                    st.error("Credenciales incorrectas")
        else:
            mostrar_panel_admin()

if __name__ == "__main__":
    main()

