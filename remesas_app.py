import streamlit as st
import json
from datetime import datetime
import os

# Ruta al archivo de datos
DATA_FILE = "remesas_data.json"

# ================== UTILIDADES ==================

def cargar_datos():
    if "remesas" not in st.session_state:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                st.session_state.remesas = json.load(f)
        else:
            st.session_state.remesas = []

def guardar_datos(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================== FORMULARIO USUARIO ==================

def mostrar_formulario_remesa():
    st.subheader("📤 Enviar Remesa")
    nombre = st.text_input("Tu nombre")
    email = st.text_input("Tu correo")
    cantidad = st.number_input("Cantidad a enviar", min_value=1.0, step=1.0)

    moneda_origen = st.selectbox("Moneda con la que vas a pagar", ["USD", "EUR", "AUD", "NZD", "CAD"])
    destino = st.selectbox("Destino", ["Nequi", "Bancolombia", "Davivienda"])
    numero_destino = st.text_input("Número de cuenta o celular")

    if st.button("Enviar remesa"):
        nueva_remesa = {
            "nombre": nombre,
            "email": email,
            "cantidad": cantidad,
            "moneda_origen": moneda_origen,
            "destino": destino,
            "numero_destino": numero_destino,
            "estado": "pendiente_pago",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.session_state.remesas.append(nueva_remesa)
        guardar_datos(st.session_state.remesas)

        st.session_state.ultima_remesa = nueva_remesa
        st.session_state.estado = "instrucciones_pago"
        st.experimental_rerun()

# ================== INSTRUCCIONES PAGO ==================

def mostrar_instrucciones_pago():
    remesa = st.session_state.ultima_remesa
    moneda = remesa["moneda_origen"]
    num_remesa = len(st.session_state.remesas)

    st.success("✅ Tu remesa fue registrada correctamente.")
    st.markdown("### 🧾 Instrucciones para realizar el pago")

    if moneda == "USD":
        st.markdown(f"""
**Método:** Wise (USD – ACH o Wire)  
**Beneficiario:** TuEmpresa Inc.  
**Cuenta:** 123456789  
**Banco:** Wise US  
**Referencia:** REMESA#{num_remesa}
        """)
    elif moneda == "EUR":
        st.markdown(f"""
**Método:** Wise (Transferencia SEPA)  
**IBAN:** DE12345678901234567890  
**Beneficiario:** TuEmpresa GmbH  
**Referencia:** REMESA#{num_remesa}
        """)
    elif moneda == "AUD":
        st.markdown(f"""
**Método:** Wise (Australia)  
**Cuenta BSB:** 123-456  
**Número de cuenta:** 987654321  
**Beneficiario:** TuEmpresa AU Pty  
**Referencia:** REMESA#{num_remesa}
        """)
    elif moneda == "NZD":
        st.markdown(f"""
**Método:** Wise (Nueva Zelanda)  
**Código del banco:** 12-3456  
**Cuenta:** 0009876  
**Beneficiario:** TuEmpresa NZ Ltd  
**Referencia:** REMESA#{num_remesa}
        """)
    elif moneda == "CAD":
        st.markdown(f"""
**Método:** Wise (Canadá)  
**Institución:** 001  
**Transit:** 12345  
**Cuenta:** 1234567  
**Beneficiario:** TuEmpresa CA Inc  
**Referencia:** REMESA#{num_remesa}
        """)

    st.info("Una vez realices el pago, te enviaremos la confirmación por correo.")

    if st.button("Volver al inicio"):
        st.session_state.estado = "formulario"
        st.experimental_rerun()

# ================== PANEL ADMIN ==================

def mostrar_panel_admin():
    st.subheader("🛠️ Panel de Administración")

    for i, remesa in enumerate(st.session_state.remesas):
        with st.expander(f"Remesa #{i+1} – {remesa['nombre']} – Estado: {remesa['estado']}"):
            st.write(remesa)

            nuevo_estado = st.selectbox(
                "Cambiar estado", 
                ["pendiente_pago", "recibido_pago", "enviado", "entregado"], 
                index=["pendiente_pago", "recibido_pago", "enviado", "entregado"].index(remesa["estado"]),
                key=f"estado_{i}"
            )

            if st.button(f"Actualizar estado (Remesa #{i+1})", key=f"btn_{i}"):
                st.session_state.remesas[i]["estado"] = nuevo_estado
                guardar_datos(st.session_state.remesas)
                st.success(f"Estado actualizado a: {nuevo_estado}")
                st.experimental_rerun()

# ================== LOGIN ADMIN ==================

def login_admin():
    st.subheader("🔐 Ingreso administrador")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if password == "admin123":  # puedes mejorar esto luego
            st.session_state.estado = "admin"
            st.experimental_rerun()
        else:
            st.error("Contraseña incorrecta")

# ================== MAIN ==================

def main():
    st.set_page_config(page_title="Remesas App", page_icon="💸")

    cargar_datos()

    if "estado" not in st.session_state:
        st.session_state.estado = "formulario"

    if st.session_state.estado == "formulario":
        mostrar_formulario_remesa()
    elif st.session_state.estado == "instrucciones_pago":
        mostrar_instrucciones_pago()
    elif st.session_state.estado == "admin":
        mostrar_panel_admin()
    elif st.session_state.estado == "login":
        login_admin()

    st.divider()
    if st.button("👮 Ingresar como administrador"):
        st.session_state.estado = "login"
        st.experimental_rerun()

# ================== EJECUTAR ==================

if __name__ == "__main__":
    main()



