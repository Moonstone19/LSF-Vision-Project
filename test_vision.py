import cv2
import mediapipe as mp
import pyttsx3
import threading
import numpy as np
from collections import deque

# --- 1. CONFIGURATION DE LA SYNTHÈSE VOCALE ---
def parler_async(texte):
    def task():
        try:
            local_engine = pyttsx3.init()
            local_engine.setProperty('rate', 150)
            local_engine.say(texte)
            local_engine.runAndWait()
        except:
            pass
    threading.Thread(target=task, daemon=True).start()

# --- 2. CONFIGURATION DE LA STABILITÉ ---
compteur_stabilite = 0
signe_en_cours = ""
seuil_validation = 10 
# On garde la trace mais on va la gérer plus proprement
pts = deque(maxlen=10) # Réduit à 10 pour être moins envahissant

# --- 3. INITIALISATION DE L'IA ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
last_vocal_sign = ""

while cap.isOpened():
    success, img = cap.read()
    if not success: break

    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.flip(img, 1) 
    h, w, c = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    display_text = "En attente..."
    current_color = (255, 255, 255)
    temp_res = ""

    if results.multi_hand_landmarks:
        # On ne prend la position pour la trace QUE de la première main pour éviter le gribouillis
        first_hand = results.multi_hand_landmarks[0]
        center = (int(first_hand.landmark[8].x * w), int(first_hand.landmark[8].y * h))
        pts.appendleft(center)

        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = hand_landmarks.landmark
            
            # Logique des doigts
            fingers = []
            for id in [8, 12, 16, 20]:
                if landmarks[id].y < landmarks[id - 2].y: fingers.append(1)
                else: fingers.append(0)

            y_poignet = landmarks[0].y
            inclinaison = abs(landmarks[20].x - landmarks[0].x) > 0.18
            
            # Reconnaissance des signes
            if fingers == [1, 1, 1, 1]:
                if inclinaison: temp_res, current_color = "AU REVOIR", (255, 0, 255)
                elif landmarks[8].y < 0.30: temp_res, current_color = "BONJOUR", (0, 255, 255)
                elif y_poignet > 0.65: temp_res, current_color = "MERCI", (255, 255, 0)
                else: temp_res, current_color = "B", (255, 0, 0)
            elif fingers == [0, 0, 0, 0]: temp_res, current_color = "A", (0, 0, 255)
            elif fingers == [1, 0, 0, 0]: temp_res, current_color = "D", (0, 255, 0)
            elif fingers == [1, 1, 0, 0]: temp_res, current_color = "VIENS", (0, 165, 255)
            elif fingers == [0, 1, 1, 1]: temp_res, current_color = "OK", (128, 0, 128)
            elif landmarks[8].y > landmarks[6].y and landmarks[8].y < landmarks[5].y:
                temp_res, current_color = "C", (42, 42, 165)

            # Dessin du squelette avec la couleur du signe
            style_pts = mp_draw.DrawingSpec(color=current_color, thickness=2, circle_radius=3)
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS, style_pts)

        # Gestion de la stabilité
        if temp_res == signe_en_cours and temp_res != "":
            compteur_stabilite += 1
        else:
            signe_en_cours = temp_res
            compteur_stabilite = 0

        if compteur_stabilite >= seuil_validation:
            display_text = signe_en_cours
            if display_text != last_vocal_sign:
                parler_async(display_text)
                last_vocal_sign = display_text
    else:
        pts.clear()
        compteur_stabilite = 0

    # UI : Barre de stabilité plus fine
    bar_v = int((min(compteur_stabilite, seuil_validation) / seuil_validation) * 200)
    cv2.rectangle(img, (20, h-30), (20 + bar_v, h-20), current_color, cv2.FILLED)

    # Affichage du texte
    cv2.putText(img, display_text, (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    # DESSIN DE LA TRACE (Seulement si une main est là et de façon plus fine)
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None: continue
        # Ligne plus fine (thickness=2) pour ne pas faire brouillon
        cv2.line(img, pts[i - 1], pts[i], current_color, 2)

    cv2.imshow("PROJET LSF - RITA", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()