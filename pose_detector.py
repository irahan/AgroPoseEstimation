from ultralytics import YOLO
import numpy as np

class PoseDetector:
    def __init__(self, model_path="models/yolov8n-pose.pt"):
        """
        Inicializa el modelo YOLO para estimación de pose.
        Si el modelo no existe localmente, ultralytics lo descargará automáticamente.
        """
        self.model = YOLO(model_path)
        
        # Mapeo de keypoints (formato COCO para YOLO pose)
        self.KP_MAPPING = {
            'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
            'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
            'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
            'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16
        }

    def predict(self, frame):
        """
        Realiza la inferencia sobre un frame y devuelve los resultados.
        """
        # verbose=False para no saturar la consola en tiempo real
        results = self.model(frame, verbose=False)
        return results

    def extract_keypoints(self, result):
        """
        Extrae los keypoints principales requeridos para el análisis de una persona (la primera detectada).
        Si hay múltiples personas, toma la de mayor confianza o la primera de la lista.
        """
        if not result.keypoints or not result.keypoints.has_visible:
            return None

        # Tomamos la primera persona detectada
        # result.keypoints.data tiene shape (num_personas, 17, 3) -> [x, y, confianza]
        kpts = result.keypoints.data[0].cpu().numpy()

        def get_pt(name1, name2=None):
            """
            Obtiene la coordenada del punto. Si se proveen dos (izquierdo y derecho),
            se devuelve el que tenga mayor confianza.
            """
            idx1 = self.KP_MAPPING[name1]
            pt1 = kpts[idx1]
            
            if name2:
                idx2 = self.KP_MAPPING[name2]
                pt2 = kpts[idx2]
                # Comparamos confianza (índice 2)
                if pt1[2] > pt2[2] and pt1[2] > 0.3:
                    return (int(pt1[0]), int(pt1[1]))
                elif pt2[2] > 0.3:
                    return (int(pt2[0]), int(pt2[1]))
                return None
            else:
                if pt1[2] > 0.3:
                    return (int(pt1[0]), int(pt1[1]))
                return None

        # Para el análisis ergonómico de perfil, usualmente un lado tiene más confianza.
        # Cabeza: podemos usar la oreja que tenga mejor vista
        head = get_pt('left_ear', 'right_ear')
        if head is None: # Fallback a nariz
            head = get_pt('nose')
            
        shoulder = get_pt('left_shoulder', 'right_shoulder')
        hip = get_pt('left_hip', 'right_hip')
        knee = get_pt('left_knee', 'right_knee')
        ankle = get_pt('left_ankle', 'right_ankle')

        return {
            'head': head,
            'shoulder': shoulder,
            'hip': hip,
            'knee': knee,
            'ankle': ankle
        }
