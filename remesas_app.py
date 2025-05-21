import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_PATH = "remesas.db"

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
            estado TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def crear_usuario_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ("admin", "admin"))
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

def autenticar_usuario(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def obtener_remesas():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM remesas", conn)
    conn.close()
    return df

def actualizar_estado_remesa(remesa_id, nuevo_estado):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE remesas SET estado = ? WHERE id = ?", (nuevo_estado, remesa_id))
    conn.commit()
    conn.close()

def enviar_correo(destinatario, asunto, mensaje):
    remitente = "urrutiab67@gmail.com"
    contrasena = "mgpr bgwa jrwg njnr"  # Contraseña de aplicación de Gmail

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, contrasena)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        return True
    except Exception as e:
        st.warning(f"No se pudo enviar el correo: {e}")
        return False

def mostrar_panel_admin():
    st.header("Panel de Administración")

    df = obtener_remesas()
    st.dataframe(df)

    for index, row in df.iterrows():
        id = row['id']
        estado = row['estado']
        email = row['email']
        nombre = row['nombre']

        nuevo_estado = st.selectbox(
            f"Actualizar estado (Remesa #{id})",
            ["Pendiente", "Aprobado", "Rechazado"],
            index=["Pendiente", "Aprobado", "Rechazado"].index(estado),
            key=f"estado_{id}"
        )

        if st.button(f"Actualizar estado", key=f"btn_{id}"):
            actualizar_estado_remesa(id, nuevo_estado)
            enviado = enviar_correo(
                email,
                "Estado de tu remesa actualizado",
                f"Hola {nombre}, tu remesa ha sido actualizada al estado: {nuevo_estado}"
            )
            if enviado:
                st.success(f"Estado actualizado y correo enviado a {email}")
            else:
                st.warning(f"Estado actualizado pero el correo no se envió")
            st.experimental_rerun()  # Refresca la página para mostrar cambio

    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar base de datos (CSV)", csv, "remesas.csv", "text/csv")

def main():
    st.title("App de Remesas")

    init_db()
    crear_usuario_admin()

    # Inicializar session_state
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False

    menu = ["Usuario", "Administrador"]
    eleccion = st.sidebar.selectbox("Selecciona vista", menu)

    if eleccion == "Usuario":
        st.subheader("Formulario de Envío de Remesas")
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        pais = st.selectbox("País de destino", ["Colombia", "Venezuela", "Perú", "Otro"])
        monto_usdt = st.number_input("Monto en USDT", min_value=1.0)
        tasa_cambio = 4000
        monto_cop = monto_usdt * tasa_cambio
        st.write(f"Monto aproximado en COP: ${monto_cop:,.2f}")
        metodo_pago = st.selectbox("Método de pago", ["Nequi", "Daviplata", "Bancolombia", "Efectivo"])

        if st.button("Enviar remesa"):
            guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, "Pendiente")
            st.success("Remesa registrada correctamente")

    elif eleccion == "Administrador":
        if not st.session_state.admin_autenticado:
            st.subheader("Ingreso administrador")
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if autenticar_usuario(usuario, clave):
                    st.session_state.admin_autenticado = True
                    st.experimental_rerun()
                else:
                    st.error("Credenciales incorrectas")
        else:
            mostrar_panel_admin()
            if st.button("Cerrar sesión"):
                st.session_state.admin_autenticado = False
                st.experimental_rerun()

if __name__ == "__main__":
    main()



