import cv2

cap = cv2.VideoCapture(0) # 0 est l'index de ta caméra par défaut

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur : Impossible d'accéder à la caméra.")
        break
        
    cv2.imshow("Test Camera Rita", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()