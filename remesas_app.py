import streamlit as st
import sqlite3
import os

DB_PATH = "remesas.db"

# --------------------- BASE DE DATOS ---------------------

def crear_base_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
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
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # Crear usuario admin por defecto
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ('admin', 'admin123'))

    conn.commit()
    conn.close()

def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado))
    conn.commit()
    conn.close()

def obtener_remesas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM remesas")
    datos = cursor.fetchall()
    conn.close()
    return datos

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

# --------------------- PÁGINAS ---------------------

def mostrar_formulario_remesas():
    st.subheader("Enviar remesa")

    nombre = st.text_input("Nombre completo")
    email = st.text_input("Email")
    pais = st.selectbox("País de destino", ["Colombia", "México", "Argentina", "Otro"])
    monto_usdt = st.number_input("Monto a enviar (USDT)", min_value=1.0, step=1.0)
    metodo_pago = st.selectbox("Método de pago", ["Billetera USDT", "Binance Pay", "Otro"])

    tasa = 3900  # Simulación
    monto_cop = monto_usdt * tasa
    st.write(f"El destinatario recibirá aproximadamente: **${monto_cop:,.2f} COP**")

    if st.button("Enviar remesa"):
        guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, "Pendiente")
        st.success("Remesa registrada exitosamente")

def mostrar_panel_admin():
    st.subheader("Panel de administración")
    remesas = obtener_remesas()

    if not remesas:
        st.info("No hay remesas registradas.")
        return

    for remesa in remesas:
        id, nombre, email, pais, usdt, cop, metodo, estado = remesa
        st.write(f"### Remesa #{id}")
        st.write(f"- **Nombre:** {nombre}")
        st.write(f"- **Email:** {email}")
        st.write(f"- **País:** {pais}")
        st.write(f"- **Monto USDT:** {usdt}")
        st.write(f"- **Monto COP:** {cop}")
        st.write(f"- **Método de pago:** {metodo}")
        st.write(f"- **Estado actual:** {estado}")

        estados = ["Pendiente", "Aprobado", "Rechazado"]
        if estado in estados:
            index_estado = estados.index(estado)
        else:
            index_estado = 0

        nuevo_estado = st.selectbox(
            f"Actualizar estado (Remesa #{id})",
            estados,
            index=index_estado,
            key=f"estado_{id}"
        )

        if st.button(f"Actualizar estado #{id}"):
            actualizar_estado_remesa(id, nuevo_estado)
            st.success("Estado actualizado")
            st.experimental_rerun()

# --------------------- APP PRINCIPAL ---------------------

def main():
    st.title("Sendify – Plataforma de Envío de Remesas")

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

