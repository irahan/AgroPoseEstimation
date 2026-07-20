import streamlit as st
import cv2
import tempfile
import time
import pandas as pd
import plotly.express as px
import os
from video_processor import VideoProcessor

st.set_page_config(page_title="AgroPosture - Análisis Ergonomico", layout="wide")

st.title("AgroPosture: Evaluación Ergonómica Agrícola")
st.markdown("Detección de posturas y clasificación de riesgos biomecánicos en tiempo real usando YOLOv8.")

# --- BARRA LATERAL ---
st.sidebar.header("Configuración")
source_type = st.sidebar.selectbox("Fuente de entrada", ["Cámara Web", "Video", "Imagen"])

model_size = st.sidebar.radio("Tamaño del modelo YOLO", ["n (rápido)", "s (preciso)"])
model_choice = 'n' if 'n' in model_size else 's'

# Botón para descargar resultados
if os.path.exists("outputs/results.csv"):
    with open("outputs/results.csv", "rb") as f:
        file_content = f.read()
    st.sidebar.download_button("Descargar CSV de Resultados", file_content, file_name="resultados_postura.csv", mime="text/csv")

# --- PROCESAMIENTO ---
processor = VideoProcessor(model_size=model_choice)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Visualización")
    frame_placeholder = st.empty()

with col2:
    st.subheader("Métricas en Tiempo Real")
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()

def process_stream(cap):
    frame_count = 0
    history = {'frame': [], 'back_angle': [], 'neck_angle': [], 'knee_angle': []}
    
    stop_button = st.button("Detener Análisis")
    
    while cap.isOpened() and not stop_button:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Procesar
        annotated_frame, metrics = processor.process_frame(frame, frame_count)
        
        # Mostrar imagen
        if annotated_frame is not None:
            # OpenCV usa BGR, Streamlit espera RGB
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
        if metrics:
            # Actualizar historial
            history['frame'].append(frame_count)
            history['back_angle'].append(metrics['back_angle'])
            history['neck_angle'].append(metrics['neck_angle'])
            history['knee_angle'].append(metrics['knee_angle'])
            
            # Limitar historial a los últimos 50 frames para visualización
            if len(history['frame']) > 50:
                for k in history.keys():
                    history[k] = history[k][-50:]
            
            df = pd.DataFrame(history)
            
            # Gráfico con Plotly
            fig = px.line(df, x='frame', y=['back_angle', 'neck_angle', 'knee_angle'], 
                          title="Ángulos Articulares",
                          labels={'value': 'Ángulo (°)', 'variable': 'Articulación'})
            
            with metrics_placeholder.container():
                st.metric("Score de Riesgo", f"{metrics['risk_score']}/100")
                st.metric("Tiempo Sostenido (Riesgo)", f"{metrics['time_in_bad_posture']} s")
                
            chart_placeholder.plotly_chart(fig, use_container_width=True)

        frame_count += 1
        time.sleep(1/15) # Limitar a aprox 15 FPS para Streamlit

    cap.release()

if source_type == "Cámara Web":
    if st.button("Iniciar Cámara"):
        processor.initialize_csv()
        cap = cv2.VideoCapture(0)
        process_stream(cap)

elif source_type == "Video":
    uploaded_video = st.file_uploader("Sube un video", type=['mp4', 'avi', 'mov'])
    if uploaded_video is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
        tfile.write(uploaded_video.read())
        tfile.close()
        
        if st.button("Procesar Video"):
            processor.initialize_csv()
            cap = cv2.VideoCapture(tfile.name)
            process_stream(cap)

elif source_type == "Imagen":
    uploaded_image = st.file_uploader("Sube una imagen", type=['jpg', 'png', 'jpeg'])
    if uploaded_image is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tfile.write(uploaded_image.read())
        tfile.close()
        
        frame = cv2.imread(tfile.name)
        if frame is not None:
            processor.initialize_csv()
            annotated_frame, metrics = processor.process_frame(frame, 0)
        else:
            st.error("No se pudo leer la imagen.")
            annotated_frame = None
            metrics = None
        
        if annotated_frame is not None:
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
        if metrics:
            with metrics_placeholder.container():
                st.metric("Score de Riesgo", f"{metrics['risk_score']}/100")
                st.write(f"Ángulo Espalda: {metrics['back_angle']}°")
                st.write(f"Ángulo Cuello: {metrics['neck_angle']}°")
                st.write(f"Ángulo Rodilla: {metrics['knee_angle']}°")

# --- FOOTER / DERECHOS DE AUTOR ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p><strong>Derechos de autor &copy;</strong></p>
</div>
<div style='display: flex; justify-content: center; color: gray;'>
    <ul>
        <li>Dr. Irahan Otoniel José Guzmán</li>
        <li>Ing. Francisco Javier Parra Sanchez</li>
        <li>Dr. Luis Enrique Garcia Santamaria</li>
        <li>Dr. Gregorio Fernandez Lambert</li>   
    </ul>
</div>
""", unsafe_allow_html=True)
