import math
import numpy as np

def calculate_angle(p1, p2, p3):
    """
    Calcula el ángulo en grados entre tres puntos (p1, p2, p3).
    El punto p2 es el vértice.
    p1, p2, p3 son tuplas o listas (x, y).
    """
    if p1 is None or p2 is None or p3 is None:
        return 0.0

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # Calcula el ángulo en radianes
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    # Asegurar que el ángulo esté entre 0 y 360
    if angle < 0:
        angle += 360
        
    # Como los ángulos articulares en este contexto normalmente no superan los 180 grados,
    # normalizamos para obtener el ángulo interno:
    if angle > 180.0:
        angle = 360.0 - angle
        
    return angle

def calculate_vertical_angle(shoulder, hip):
    """
    Calcula el ángulo entre la línea (hombro - cadera) y la vertical absoluta.
    Un ángulo de 0° significa que la persona está completamente erguida.
    """
    if shoulder is None or hip is None:
        return 0.0

    # Simulamos un tercer punto que es la vertical hacia arriba (o abajo)
    # Eje Y en imágenes crece hacia abajo. Si la cadera está en (hx, hy), 
    # la vertical superior pasando por la cadera sería (hx, hy - 100).
    vertical_pt = (hip[0], hip[1] - 100)

    # Calculamos el ángulo usando la cadera como vértice: (hombro, cadera, vertical_pt)
    angle = calculate_angle(shoulder, hip, vertical_pt)
    
    return angle
