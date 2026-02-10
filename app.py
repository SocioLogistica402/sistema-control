import streamlit as st

# --- CONFIGURACIÓN DE SEGURIDAD ---
def check_password():
    """Devuelve True si el usuario ingresó la contraseña correcta."""

    def password_entered():
        """Revisa si la contraseña coincide."""
        if st.session_state["username"] == "admin" and st.session_state["password"] == "Socio2024*":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Borramos la contraseña de memoria por seguridad
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Pantalla de Login
        st.title("🔐 Acceso Restringido")
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Credenciales incorrectas
        st.title("🔐 Acceso Restringido")
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        st.error("😕 Usuario o contraseña incorrectos")
        return False
    else:
        # Contraseña correcta
        return True

# --- SI LA CONTRASEÑA ES CORRECTA, CORRE EL RESTO DE LA APP ---
if check_password():
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Control Logístico Total", layout="wide")

# --- CARGA DE DATOS ---
def cargar_datos():
    # Sanitarios
    if os.path.exists("inventario.csv"):
        df_san = pd.read_csv("inventario.csv")
    else:
        df_san = pd.DataFrame(columns=['ID_Activo', 'Estado', 'Responsable', 'Latitud', 'Longitud'])
    
    # Insumos
    if os.path.exists("inventario_insumos.csv"):
        df_ins = pd.read_csv("inventario_insumos.csv")
    else:
        df_ins = pd.DataFrame(columns=['Producto', 'Cantidad', 'Unidad', 'Minimo'])
        
    return df_san, df_ins

df_san, df_ins = cargar_datos()

# --- BARRA LATERAL (Menú) ---
st.sidebar.title("🚀 PANEL DE NAVEGACIÓN")
seccion = st.sidebar.radio("Ir a:", ["📍 Mapa y Activos", "📦 Almacén de Insumos", "📊 Reportes y Gráficas"])

# --- SECCIÓN 1: SANITARIOS ---
if seccion == "📍 Mapa y Activos":
    st.title("📡 Control de Unidades Sanitarias")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Mapa en Tiempo Real")
        if not df_san.empty:
            m = folium.Map(location=[df_san['Latitud'].mean(), df_san['Longitud'].mean()], zoom_start=10)
            for _, r in df_san.iterrows():
                color = 'green' if r['Estado'] == 'En Bodega' else 'blue'
                if r['Estado'] == 'Reparación': color = 'red'
                folium.Marker([r['Latitud'], r['Longitud']], 
                              popup=f"ID: {r['ID_Activo']} - {r['Responsable']}",
                              icon=folium.Icon(color=color)).add_to(m)
            st_folium(m, width=800, height=500)
    
    with col2:
        st.subheader("Estado de Unidades")
        st.dataframe(df_san[['ID_Activo', 'Estado', 'Responsable']], use_container_width=True)
        
        # Mini resumen
        en_ruta = len(df_san[df_san['Estado'] == 'En Ruta'])
        st.metric("Unidades en Calle", f"{en_ruta} de {len(df_san)}")

# --- SECCIÓN 2: ALMACÉN ---
elif seccion == "📦 Almacén de Insumos":
    st.title("📦 Inventario de Materiales e Insumos")
    
    # Alertas Críticas arriba
    criticos = df_ins[df_ins['Cantidad'] <= df_ins['Minimo']]
    if not criticos.empty:
        for _, r in criticos.iterrows():
            st.error(f"⚠️ **COMPRA URGENTE:** {r['Producto']} (Quedan {r['Cantidad']} {r['Unidad']})")

    # Tabla de Inventario
    st.subheader("Existencias Actuales")
    st.table(df_ins)

    # Formulario rápido de Salida
    with st.expander("➕ Registrar Salida de Material"):
        with st.form("salida_insumos"):
            prod = st.selectbox("Selecciona Producto", df_ins['Producto'].unique())
            cant = st.number_input("Cantidad", min_value=0.1)
            quien = st.selectbox("Entrega a:", ["Yamil", "José", "Cruz", "Noel"])
            boton = st.form_submit_button("Registrar Entrega")
            if boton:
                st.success(f"Salida de {cant} de {prod} registrada para {quien}")

# --- SECCIÓN 3: REPORTES ---
elif seccion == "📊 Reportes y Gráficas":
    st.title("📊 Análisis de Operación")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Carga por Chofer")
        if not df_san.empty:
            resumen_chofer = df_san[df_san['Estado'] == 'En Ruta']['Responsable'].value_counts()
            st.bar_chart(resumen_chofer)
            
    with c2:
        st.subheader("Insumos en Stock")
        st.bar_chart(df_ins.set_index('Producto')['Cantidad'])

    st.success("¡Bienvenido, Socio!")
