import time
from utils import calculate_angle

class PostureAnalyzer:
    def __init__(self, fps=15):
        self.fps = fps
        self.risk_start_time = None
        self.consecutive_bad_frames = 0
        self.frames_for_alert = 5 * self.fps # 5 segundos

    def evaluate_posture(self, keypoints):
        """
        Evalúa las reglas ergonómicas en base a los keypoints.
        Retorna el estado, puntaje y métricas.
        """
        if not keypoints or any(v is None for v in keypoints.values()):
            return "Desconocido", 0, {}, "No se detectaron todos los puntos."

        head = keypoints['head']
        shoulder = keypoints['shoulder']
        hip = keypoints['hip']
        knee = keypoints['knee']
        ankle = keypoints['ankle']

        # 1. Regla 1: Espalda encorvada
        # Para que los números del usuario tengan sentido (< 45 encorvado, > 65 aceptable),
        # medimos el ángulo del torso con respecto a la HORIZONTAL (el suelo).
        # Persona erguida = 90 grados (> 65, aceptable).
        # Persona inclinada = 45 grados.
        horizontal_pt = (hip[0] + 100, hip[1])
        back_angle = calculate_angle(shoulder, hip, horizontal_pt)
        # Si la persona está mirando hacia la izquierda, el ángulo puede ser obtuso.
        if back_angle > 90:
            back_angle = 180 - back_angle

        # 2. Regla 2: Flexión de cuello
        neck_angle = calculate_angle(head, shoulder, hip)

        # 3. Regla 3: Uso de rodillas
        knee_angle = calculate_angle(hip, knee, ankle)

        # Evaluación de riesgo
        risk_score = 0
        risk_level = "Correcta"
        recommendation = "Postura adecuada."

        is_trunk_inclined = back_angle < 65

        if back_angle < 45:
            risk_score += 50
        elif 45 <= back_angle <= 65:
            risk_score += 25

        if neck_angle < 140:
            risk_score += 20

        if is_trunk_inclined and knee_angle > 160:
            # Tronco inclinado y rodillas rectas -> espalda soporta la carga
            risk_score += 30

        # Clasificación del frame actual
        if risk_score >= 50:
            current_status = "Alto"
        elif risk_score >= 25:
            current_status = "Moderado"
        else:
            current_status = "Correcta"

        # Regla 4: Tiempo sostenido
        # Si el status es Alto o Moderado, incrementamos contador
        if current_status in ["Alto", "Moderado"]:
            if self.risk_start_time is None:
                self.risk_start_time = time.time()
            self.consecutive_bad_frames += 1
        else:
            self.risk_start_time = None
            self.consecutive_bad_frames = 0

        # Calcular tiempo acumulado en mala postura de esta racha
        time_in_bad_posture = 0
        if self.risk_start_time:
            time_in_bad_posture = time.time() - self.risk_start_time

        # Alerta sostenida
        if time_in_bad_posture > 5.0:
            risk_level = "Riesgo Alto (Sostenido)"
            recommendation = "¡ALERTA! Postura riesgosa por más de 5s. Descansa o usa las rodillas."
        else:
            risk_level = current_status
            if current_status == "Alto":
                recommendation = "Riesgo alto inmediato. Corrige tu espalda."
            elif current_status == "Moderado":
                recommendation = "Riesgo moderado. Presta atención a tu inclinación."

        metrics = {
            'back_angle': round(back_angle, 1),
            'neck_angle': round(neck_angle, 1),
            'knee_angle': round(knee_angle, 1),
            'time_in_bad_posture': round(time_in_bad_posture, 1),
            'risk_score': min(risk_score, 100)
        }

        return risk_level, risk_score, metrics, recommendation
