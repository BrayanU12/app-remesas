import streamlit as st
import pandas as pd
from datetime import datetime

# Inicialización de estado
if "remesas" not in st.session_state:
    st.session_state.remesas = pd.DataFrame(columns=["nombre", "correo", "monto", "moneda", "pais_origen", "fecha", "estado"])
if "modo" not in st.session_state:
    st.session_state.modo = "cliente"
if "mostrar_login" not in st.session_state:
    st.session_state.mostrar_login = False
if "mostrar_datos_pago" not in st.session_state:
    st.session_state.mostrar_datos_pago = False

# Datos bancarios por moneda
DATOS_BANCARIOS = {
    "USD": {
        "banco": "Wise US",
        "nombre": "RemesasApp LLC",
        "cuenta": "1234567890",
        "routing": "021000021",
        "swift": "CHASUS33"
    },
    "EUR": {
        "banco": "Wise Europe",
        "nombre": "RemesasApp B.V.",
        "cuenta": "DE89370400440532013000",
        "swift": "DEUTDEFF"
    },
    "AUD": {
        "banco": "Wise Australia",
        "nombre": "RemesasApp Pty Ltd",
        "cuenta": "12345678",
        "bsb": "802-123"
    },
    "NZD": {
        "banco": "Wise New Zealand",
        "nombre": "RemesasApp NZ Ltd",
        "cuenta": "12-1234-1234567-00"
    },
    "CAD": {
        "banco": "Wise Canada",
        "nombre": "RemesasApp Inc.",
        "cuenta": "1234567",
        "institution": "003",
        "transit": "12345"
    }
}

def registrar_remesa():
    st.title("📤 Enviar Remesa")

    with st.form("form_remesa"):
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        monto = st.number_input("Monto a enviar", min_value=1.0, format="%.2f")
        moneda = st.selectbox("Moneda de origen", ["USD", "EUR", "AUD", "NZD", "CAD"])
        pais_origen = st.text_input("País desde donde envías")
        enviado = st.form_submit_button("Enviar remesa")

        if enviado:
            nueva_remesa = {
                "nombre": nombre,
                "correo": correo,
                "monto": monto,
                "moneda": moneda,
                "pais_origen": pais_origen,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "Pendiente"
            }
            st.session_state.remesas = pd.concat([st.session_state.remesas, pd.DataFrame([nueva_remesa])], ignore_index=True)
            st.session_state.mostrar_datos_pago = True
            st.success("✅ Remesa registrada exitosamente. A continuación encontrarás los datos para hacer el pago.")
            st.rerun()

    if st.session_state.mostrar_datos_pago:
        mostrar_datos_pago(st.session_state.remesas.iloc[-1]["moneda"])

def mostrar_datos_pago(moneda):
    st.subheader("🏦 Datos para realizar la transferencia")
    datos = DATOS_BANCARIOS.get(moneda, {})
    if datos:
        for clave, valor in datos.items():
            st.write(f"**{clave.capitalize()}:** {valor}")
        st.markdown("---")
        st.info("Una vez hayas hecho la transferencia, tu remesa será procesada y enviada en USDT a Colombia.")
    else:
        st.warning("No se encontraron datos bancarios para esta moneda.")

def login_admin():
    st.subheader("🔐 Iniciar sesión como administrador")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if password == "admin123":
            st.session_state.modo = "admin"
            st.session_state.mostrar_login = False
            st.success("✅ Ingreso exitoso.")
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta.")

def mostrar_panel_admin():
    st.title("📊 Panel de Administración")

    if st.session_state.remesas.empty:
        st.info("No hay remesas registradas.")
        return

    for i, remesa in st.session_state.remesas.iterrows():
        st.write(f"**Remesa #{i + 1}**")
        st.write(remesa.to_frame().T)

        nuevo_estado = st.selectbox(
            f"Actualizar estado (Remesa #{i + 1})",
            ["Pendiente", "Procesada", "Cancelada"],
            index=["Pendiente", "Procesada", "Cancelada"].index(remesa["estado"]),
            key=f"estado_{i}"
        )

        if st.button(f"Actualizar estado Remesa #{i + 1}", key=f"btn_estado_{i}"):
            st.session_state.remesas.at[i, "estado"] = nuevo_estado
            st.success(f"Estado actualizado a {nuevo_estado} para la Remesa #{i + 1}")
            st.rerun()

def main():
    st.set_page_config(page_title="RemesasApp", layout="centered")

    st.title("🌎 RemesasApp")

    # Botón de administrador
    if st.button("👮 Ingresar como administrador"):
        st.session_state.mostrar_login = True

    if st.session_state.mostrar_login and st.session_state.modo != "admin":
        login_admin()
    elif st.session_state.modo == "admin":
        mostrar_panel_admin()
    else:
        registrar_remesa()

if __name__ == "__main__":
    main()

