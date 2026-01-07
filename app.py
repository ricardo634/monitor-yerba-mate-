import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

# Configuración visual
st.set_page_config(page_title="Yerba Mate FEDECOOP", layout="wide")
st.title("🌿 Monitor Satelital de Yerba Mate")

# Conexión segura con tu Google Sheets
def cargar_datos():
    # El archivo JSON debe llamarse exactamente así en GitHub
    JSON_FILE = 'tu-credencial.json' 
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(JSON_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    
    # Abrir la planilla y convertir a tabla de datos
    sheet = client.open("yerbatero").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Limpiar el NDVI para que sea número (por si tiene comas)
    df.columns = ['fecha', 'coop', 'lote', 'ndvi', 'estado', 'informe']
    df['ndvi'] = df['ndvi'].astype(str).str.replace(',', '.').astype(float)
    return df

try:
    df = cargar_datos()
    
    # Selector de lote en la barra lateral
    lote_opciones = df['lote'].unique()
    lote_elegido = st.sidebar.selectbox("Seleccione el Lote:", lote_opciones)
    
    # Filtrar datos del lote elegido
    datos_lote = df[df['lote'] == lote_elegido].iloc[-1]
    
    # Mostrar indicadores principales
    c1, c2, c3 = st.columns(3)
    c1.metric("Salud (NDVI)", datos_lote['ndvi'])
    c2.subheader(f"Estado: {datos_lote['estado']}")
    c3.write(f"📅 Actualizado: {datos_lote['fecha']}")
    
    st.info(f"🤖 **Diagnóstico de la IA:** \n\n {datos_lote['informe']}")
    
    # Gráfico de evolución
    st.subheader("📈 Tendencia de Salud")
    historial = df[df['lote'] == lote_elegido]
    fig, ax = plt.subplots()
    ax.plot(historial['fecha'], historial['ndvi'], marker='o', color='green')
    plt.xticks(rotation=45)
    st.pyplot(fig)

except Exception as e:
    st.error("Error conectando con los datos. Verifique sus credenciales.")
