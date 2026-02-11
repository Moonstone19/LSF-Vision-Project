import cv2

# --- ÉTAPE 1 DU PIPELINE : ACQUISITION DES IMAGES --- 
# Justification : Utilisation d'OpenCV pour capturer le flux brut de la caméra.
# Cette étape est critique car elle conditionne la qualité de l'image d'entrée

cap = cv2.VideoCapture(0) # 0 est l'index de ta caméra par défaut

while True:
    ret, frame = cap.read()
    
    # Gestion d'erreur d'acquisition 
    if not ret:
        print("Erreur : Impossible d'accéder à la caméra.")
        break
        
    # Visualisation du flux brut avant tout traitement 
    cv2.imshow("Test Camera Rita - Acquisition Brute", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Nettoyage des ressources (Nettoyage du pipeline)
cap.release()
cv2.destroyAllWindows()