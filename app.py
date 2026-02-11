import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. ESTO TIENE QUE IR PRIMERO QUE NADA ---
st.set_page_config(page_title="Sistema Control Logístico", layout="wide")

# --- 2. SEGURIDAD ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Restringido")
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if user == "admin" and pw == "Socio2024*":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
        return False
    return True

# --- 3. PROGRAMA ---
if check_password():
    st.title("🚀 Panel de Control SocioLogística")
    
    # Carga de archivos
    if os.path.exists("inventario.csv") and os.path.exists("inventario_insumos.csv"):
        df_san = pd.read_csv("inventario.csv")
        df_ins = pd.read_csv("inventario_insumos.csv")
        
        menu = st.sidebar.radio("Navegación", ["Mapa", "Almacén", "Reportes"])
        
        if menu == "Mapa":
            st.subheader("📍 Ubicación de Activos")
            m = folium.Map(location=[df_san['Latitud'].mean(), df_san['Longitud'].mean()], zoom_start=10)
            for _, r in df_san.iterrows():
                folium.Marker([r['Latitud'], r['Longitud']], popup=r['ID_Activo']).add_to(m)
            st_folium(m, width=700, height=450)
            
        elif menu == "Almacén":
            st.subheader("📦 Inventario de Insumos")
            st.table(df_ins)
            
        elif menu == "Reportes":
            st.subheader("📊 Gráficas de Operación")
            st.bar_chart(df_ins.set_index('Producto')['Cantidad'])
    else:
        st.warning("⚠️ No se encontraron los archivos .csv en el repositorio.")
