import streamlit as st
import sqlite3
import os

DB_PATH = "remesas.db"

# ---------- Inicialización de la base de datos ----------
def init_db():
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
    conn.commit()
    conn.close()

# ---------- Función para guardar una remesa ----------
def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, 'Pendiente')
    ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago))
    conn.commit()
    conn.close()

# ---------- Función para obtener remesas ----------
def obtener_remesas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM remesas')
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------- Función para actualizar el estado ----------
def actualizar_estado(remesa_id, nuevo_estado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE remesas SET estado = ? WHERE id = ?', (nuevo_estado, remesa_id))
    conn.commit()
    conn.close()

# ---------- Autenticación básica ----------
def autenticar(usuario, contraseña):
    return usuario == "admin" and contraseña == "admin123"

# ---------- Interfaz principal ----------
def main():
    st.set_page_config(page_title="Sendify", layout="centered")
    st.title("Sendify - App de Remesas")

    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.subheader("Iniciar sesión")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if autenticar(usuario, contraseña):
                st.session_state.autenticado = True
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return

    st.sidebar.title("Menú")
    opcion = st.sidebar.radio("Seleccione una opción", ["Registrar Remesa", "Panel de Administración"])

    if opcion == "Registrar Remesa":
        st.subheader("Formulario de Remesa")

        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        pais = st.selectbox("País de destino", ["Colombia", "México", "Perú", "Argentina"])
        monto_usdt = st.number_input("Monto en USDT", min_value=1.0)
        tasa_cambio = 4000  # tasa fija por ahora
        monto_cop = monto_usdt * tasa_cambio
        st.write(f"Monto en COP (aprox): {monto_cop:,.0f}")
        metodo_pago = st.selectbox("Método de pago", ["Binance", "PayPal", "Western Union"])

        if st.button("Enviar Remesa"):
            guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago)
            st.success("Remesa registrada exitosamente.")

    elif opcion == "Panel de Administración":
        st.subheader("Panel de Administración - Estado de Remesas")

        remesas = obtener_remesas()
        for remesa in remesas:
            id, nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado = remesa
            st.write(f"📨 {nombre} | {email} | {pais} | {monto_usdt} USDT | {monto_cop:,.0f} COP | Método: {metodo_pago}")

            nuevo_estado = st.selectbox(f"Actualizar estado (Remesa #{id})", ["Pendiente", "Aprobado", "Rechazado"], index=["Pendiente", "Aprobado", "Rechazado"].index(estado), key=f"estado_{id}")
            if st.button(f"Guardar estado #{id}", key=f"guardar_{id}"):
                actualizar_estado(id, nuevo_estado)
                st.success(f"Estado actualizado a: {nuevo_estado}")
                st.experimental_rerun()

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    main()
