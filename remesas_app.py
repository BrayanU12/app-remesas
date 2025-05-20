import streamlit as st
import sqlite3
import pandas as pd
import time

# Elimina remesas.db si ya existe, para evitar conflictos de esquema
if os.path.exists("remesas.db"):
    os.remove("remesas.db")

DB_PATH = "remesas.db"

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

def guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO remesas (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, email, pais, monto_usdt, monto_cop, metodo_pago, estado))

def actualizar_estado_remesa(remesa_id, nuevo_estado):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            UPDATE remesas SET estado = ? WHERE id = ?
        ''', (nuevo_estado, remesa_id))

st.title("📤 Sendify - Envío de Remesas Simulado")

crear_tabla()

with st.form("formulario_remesa"):
    nombre = st.text_input("👤 Nombre completo")
    email = st.text_input("📧 Correo electrónico")
    pais = st.selectbox("🌍 País destino", ["Colombia", "México", "Argentina", "Perú"])
    monto_usdt = st.number_input("💸 Monto a enviar (USDT)", min_value=0.0, step=0.5)
    metodo_pago = st.selectbox("💳 Método de pago", ["Binance Pay", "MetaMask", "PayPal", "Otro"])

    submitted = st.form_submit_button("Iniciar pago")

if submitted:
    if not nombre or not email or monto_usdt <= 0:
        st.warning("⚠️ Por favor completa todos los campos.")
    else:
        with st.spinner("🔄 Procesando pago..."):
            time.sleep(2)
        tasa = 4000  # Simula tasa de cambio
        monto_cop = monto_usdt * tasa

        # Guardar con estado "Pago confirmado"
        guardar_en_db(nombre, email, pais, monto_usdt, monto_cop, metodo_pago, "Pago confirmado")
        st.success(f"✅ Pago confirmado. Listo para aprobar la remesa.")
        
        # Mostrar botón de aprobación solo si se acaba de confirmar
        aprobar = st.button("✅ Aprobar y enviar remesa")
        if aprobar:
            # Buscar el último registro (más reciente)
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM remesas ORDER BY id DESC LIMIT 1")
                remesa_id = cursor.fetchone()[0]
            actualizar_estado_remesa(remesa_id, "Remesa aprobada")
            st.success("💰 Remesa aprobada y enviada con éxito.")

# Historial con estado
if st.checkbox("📄 Ver historial de remesas"):
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM remesas ORDER BY id DESC", conn)
        if not df.empty:
            df['monto_cop'] = df['monto_cop'].map(lambda x: f"${x:,.0f}")
            st.dataframe(df)
        else:
            st.info("Aún no hay remesas registradas.")

