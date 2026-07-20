import cv2
import csv
import os
from pose_detector import PoseDetector
from posture_rules import PostureAnalyzer

class VideoProcessor:
    def __init__(self, model_size='n', output_dir='outputs'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        model_name = f'yolov8{model_size}-pose.pt'
        self.detector = PoseDetector(model_path=f'models/{model_name}')
        self.analyzer = PostureAnalyzer(fps=15)
        
        self.csv_path = os.path.join(self.output_dir, 'results.csv')
        # Inicializar CSV
        with open(self.csv_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Frame', 'Back_Angle', 'Neck_Angle', 'Knee_Angle', 'Time_Bad_Posture', 'Risk_Score', 'Status'])

    def draw_skeleton(self, frame, keypoints, risk_level):
        """Dibuja el esqueleto y estado sobre el frame."""
        # Colores BGR
        if "Alto" in risk_level:
            color = (0, 0, 255) # Rojo
        elif "Moderado" in risk_level:
            color = (0, 255, 255) # Amarillo
        else:
            color = (0, 255, 0) # Verde

        # Dibujar líneas del esqueleto
        pairs = [
            ('head', 'shoulder'),
            ('shoulder', 'hip'),
            ('hip', 'knee'),
            ('knee', 'ankle')
        ]

        for p1_name, p2_name in pairs:
            pt1 = keypoints.get(p1_name)
            pt2 = keypoints.get(p2_name)
            if pt1 and pt2:
                cv2.line(frame, pt1, pt2, color, 3)

        # Dibujar puntos
        for pt in keypoints.values():
            if pt:
                cv2.circle(frame, pt, 5, (255, 0, 0), -1)

        return frame

    def process_frame(self, frame, frame_count):
        """Procesa un frame individual."""
        results = self.detector.predict(frame)
        kpts = self.detector.extract_keypoints(results[0])
        
        if not kpts:
            return frame, None

        risk_level, risk_score, metrics, recommendation = self.analyzer.evaluate_posture(kpts)
        
        annotated_frame = self.draw_skeleton(frame.copy(), kpts, risk_level)
        
        # Poner textos en la imagen
        cv2.putText(annotated_frame, f"Estado: {risk_level}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"Espalda: {metrics['back_angle']} deg", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, recommendation, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        # Guardar en CSV
        with open(self.csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([frame_count, metrics['back_angle'], metrics['neck_angle'], metrics['knee_angle'], 
                             metrics['time_in_bad_posture'], risk_score, risk_level])
                             
        return annotated_frame, metrics
