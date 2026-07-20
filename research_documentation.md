# Documentación Académica: AgroPosture

## 1. Justificación Ergonomica y Matemática

La plataforma AgroPosture está diseñada para evaluar riesgos biomecánicos en tareas agrícolas, en particular la recolección de frutas. Los trabajadores agrícolas a menudo mantienen posturas forzadas durante períodos prolongados, lo que contribuye a trastornos musculoesqueléticos (TME).

### Regla 1: Espalda Encorvada
- **Métrica**: Ángulo del tronco con respecto a la horizontal.
- **Matemática**: Se calcula el ángulo entre el vector formado por la cadera y el hombro, y un vector horizontal que pasa por la cadera.
  - Ecuación: $\theta_{espalda} = \arctan2(y_{horizontal} - y_{cadera}, x_{horizontal} - x_{cadera}) - \arctan2(y_{hombro} - y_{cadera}, x_{hombro} - x_{cadera})$
- **Justificación Ergonómica**: 
  - $> 65^\circ$: Postura erguida, aceptable.
  - $45^\circ - 65^\circ$: Flexión de tronco moderada. Incrementa la presión intradiscal.
  - $< 45^\circ$: Flexión severa. Los músculos erectores espinales están sometidos a máxima tensión.

### Regla 2: Flexión de Cuello
- **Métrica**: Ángulo interno entre Cabeza, Hombro y Cadera.
- **Justificación**: Un ángulo $< 140^\circ$ indica una alta flexión cervical, comúnmente asociada a dolor de cuello crónico por el "síndrome de cuello adelantado".

### Regla 3: Uso de Rodillas
- **Métrica**: Ángulo Cadera-Rodilla-Tobillo.
- **Justificación**: Si un trabajador inclina su tronco (Regla 1 $< 65^\circ$) manteniendo las rodillas extendidas (ángulo $> 160^\circ$), el peso de la parte superior del cuerpo recae enteramente en la columna lumbar (L5-S1), en lugar de distribuirse en los grandes músculos de las piernas (cuádriceps/glúteos).

### Regla 4: Tiempo Sostenido
- Las posturas estáticas son más perjudiciales que las dinámicas. Se ha establecido un umbral de $> 5$ segundos continuos en posturas riesgosas (Moderado o Alto) para disparar una alerta máxima, indicando una potencial acumulación de fatiga localizada.

---

## 2. Limitaciones del Método basado en Visión 2D

El uso de un modelo como YOLOv8-pose en imágenes 2D (monoculares) presenta ciertas limitaciones inherentes:
1. **Oclusión**: En actividades agrícolas, la vegetación, herramientas y los propios brazos del trabajador pueden ocultar articulaciones críticas (como las rodillas o caderas).
2. **Ambigüedad de Profundidad**: En un plano 2D, una extremidad que se acerca a la cámara parece más corta. Esto puede alterar severamente los cálculos de los ángulos, ya que la estimación 2D asume que el sujeto está paralelo al plano de la cámara (perfil perfecto).
3. **Falta de Rotación Axial**: No se puede medir fácilmente la torsión de la columna, lo cual es un factor de riesgo crítico en la manipulación de cargas.

---

## 3. Recomendaciones para Mejorar la Precisión

Para escalar este prototipo a un sistema robusto, se recomiendan las siguientes mejoras:
1. **MediaPipe Pose 3D**: Sustituir YOLOv8-pose por MediaPipe Pose, que infiere coordenadas $(x, y, z)$. El eje $z$ permite corregir parcialmente la ambigüedad de profundidad.
2. **Redes Estereoscópicas o Cámaras RGB-D (RealSense, Kinect)**: Utilizar hardware específico para capturar profundidad real y calcular ángulos 3D verdaderos.
3. **OpenPose con Multi-Cámara**: Triangulación de coordenadas de 2 o más cámaras ubicadas en el campo para lograr una reconstrucción esquelética en 3D robusta ante oclusiones.

---

## 4. Métricas de Evaluación Sugeridas

Para validar académicamente el sistema en un estudio posterior, se sugiere comparar las salidas de AgroPosture contra un sistema "Gold Standard" (como sensores inerciales IMU Xsens o Vicon):
- **Accuracy**: Porcentaje total de cuadros correctamente clasificados en Riesgo Alto, Moderado, Correcta.
- **Precision**: Capacidad del sistema para no marcar como "Riesgo" una postura correcta.
- **Recall (Sensibilidad)**: Capacidad para detectar todas las posturas de verdadero Riesgo Alto.
- **F1-Score**: Media armónica entre Precision y Recall (crítico dado que las posturas pueden estar desbalanceadas temporalmente).
- **MAE de Ángulos (Mean Absolute Error)**: Diferencia en grados entre el ángulo medido por YOLO 2D y el medido por sensores IMU 3D.
