import cv2 as cv
import numpy as np
import math
from PIL import Image

REAL_MARKER_DIMENTION_mm= 40
FOCAL_LENGHT_mm = 2.6
PIXEL_DIMENTION_mm = 0.0008

# Funzione che calcola la quantità di padding da aggiungere a due numeri
def padding_to_add(a, b):
    # Calcola il valore assoluto della differenza tra i due numeri e divide per 2
    # per ottenere la metà della differenza, che è la quantità di padding da aggiungere
    return abs(a - b) / 2

'''
    Funzione che scrive informazioni testuali su un'immagine.

    Parametri di utilizzo:
        - img_canvas: L'immagine di base su cui verranno sovrapposte le informazioni testuali.
        - video_width: La larghezza del video, utilizzata per posizionare il testo sull'immagine.
        - distance: La distanza dell'oggetto in millimetri, che verrà convertita in metri e visualizzata sull'immagine.
        - rom: L'intervallo di movimento (Range of Motion) in millimetri, anch'esso convertito in metri e mostrato sull'immagine.
        - rom_speed: La velocità dell'intervallo di movimento in millimetri al secondo, convertita in metri al secondo e visualizzata sull'immagine.

    Return:
        - img_canvas: L'immagine originale con le informazioni testuali sovrapposte.
'''
def write_canvasData(img_canvas, video_width, distance, rom, rom_speed):
    # Scrivi tutte le info nell'immagine path_execution.png
    img_canvas = cv.putText(img_canvas, f"obj_distance: {(distance/1000):.2f} m", (video_width -400, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    img_canvas = cv.putText(img_canvas, f"ROM: {(rom/1000):.2f} m", (video_width -400, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    img_canvas = cv.putText(img_canvas, f"ROM speed: {(rom_speed/1000):.2f} m", (video_width -400, 150), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return img_canvas

'''
    Questa funzione visualizza un'immagine in una finestra OpenCV ridimensionabile con larghezza e altezza specificate.

    Parametri:
        - name: nome della finestra
        - desired_width: larghezza della finestra
        - desired_height: altezza della finestra
        - frame: immagine da visualizzare
'''
def img_show(name, desired_width, desired_height, frame):
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    cv.resizeWindow(name, desired_width, desired_height)
    cv.imshow(name, frame)

'''
Funzione per ottenere il range di valori HSV (Hue, Saturation, Value) per un dato colore in formato BGR

Parametri:
- color: colore da cui ricavare i range

Ritorna:
Limite inferiore e limite maggiore dei colori da ricercare
'''
def get_value_range(color):
    # Converti il colore BGR in HSV
    c = np.uint8([[color]])  # Converti il colore in un array numpy di tipo uint8
    hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)  # Converti il colore da BGR a HSV

    # Estrai i valori di Hue (tonalità), Saturation (saturazione) e Value (luminosità) dal colore HSV
    hue, saturation, value = hsvC[0][0]
    #print("HSV: {} {} {}".format(hue, saturation, value))  # Stampa i valori di Hue, Saturation e Value

    # Definisci i limiti inferiori e superiori per il range di valori HSV
    # La tonalità (Hue) viene regolata con un margine di +/- 10 per catturare variazioni nel colore
    lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)  # Limite inferiore per Hue, Saturation e Value
    upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)  # Limite superiore per Hue, Saturation e Value

    return lowerLimit, upperLimit  # Restituisce i limiti inferiori e superiori del range di valori HSV


def get_limits(color):
    c = np.uint8([[color]])  # BGR values
    hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)

    hue = hsvC[0][0][0]  # Get the hue value

    # Handle red hue wrap-around
    if hue >= 165:  # Upper limit for divided red hue
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([180, 255, 255], dtype=np.uint8)
    elif hue <= 15:  # Lower limit for divided red hue
        lowerLimit = np.array([0, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)
    else:
        lowerLimit = np.array([hue - 10, 100, 100], dtype=np.uint8)
        upperLimit = np.array([hue + 10, 255, 255], dtype=np.uint8)

    return lowerLimit, upperLimit

"""
Ridimensiona un'immagine in modo che contenga la figura rappresentata all'interno.

Parametri:
- image: l'immagine da ridimensionare

Ritorna:
Un'immagine ridimensionata contenente la figura.
"""
def resize_to_fit_containing_figure(image, w, h, cx, cy):

    #Ritaglio le immagini alla minima dimensione contenente il path
    xoff = w//2
    yoff = h//2
    crop = image[cy-yoff:cy+yoff, cx-xoff:cx+xoff]
    
    return crop

"""
Funzione per ottenere le coordinate del centro di un rettangolo.

Parametri:
- x: La coordinata x dell'angolo in alto a sinistra del rettangolo.
- y: La coordinata y dell'angolo in alto a sinistra del rettangolo.
- w: La larghezza del rettangolo.
- h: L'altezza del rettangolo.

Return:
- x_center: La coordinata x del centro del rettangolo.
- y_center: La coordinata y del centro del rettangolo.

"""
def get_rectangle_center(x, y, w, h):

    # Calcola le coordinate x e y del centro del rettangolo
    x_center = x + (w // 2)
    y_center = y + (h // 2)
    
    # Restituisce le coordinate del centro del rettangolo
    return x_center, y_center

"""
Questa funzione prende in input le coordinate di due punti che definiscono un rettangolo e calcola
le coordinate del centro del cerchio circoscritto al rettangolo. 

"""
def get_circle_center_coordinates(x1, x2, y1, y2):
    
    # Calcola le coordinate x e y del centro del cerchio
    x_center = (x2 + x1) // 2
    y_center = (y2 + y1) // 2
    
    # Restituisce le coordinate del centro del cerchio
    return x_center, y_center
    
"""
Calcola l'altezza e la larghezza del bounding box (bbox).

Args:
    bbox (tuple): Una tupla contenente i quattro punti del bounding box (x1, y1, x2, y2).

Returns:
    tuple: Una tupla contenente l'altezza e la larghezza del bounding box (height, width).
"""
def get_bbox_dimensions(x1, y1, x2, y2):
    width = x2 - x1
    height = y2 - y1
    return height, width

"""
Calcola le coordinate del rettangolo.

Args:
    t_width (int): Larghezza totale dell'immagine o della finestra.
    t_pos (int): Posizione verticale del rettangolo, indicata come numero di posizioni dall'alto verso il basso.

Returns:
    tuple: Una tupla contenente le coordinate x e y del rettangolo.
"""
def compute_rectangle_coordinate(t_width, t_pos):
    # Calcola la coordinata x del rettangolo
    x = t_width - 100
    # Calcola la coordinata y del rettangolo basata sulla posizione desiderata
    y = (t_pos -1) * 100
    return x, y

"""
Calcola l'altezza proporzionale di un'immagine in base alla larghezza desiderata.

Parameters:
    img: numpy.ndarray - L'immagine di cui si vuole calcolare l'altezza proporzionale.
    width: int - La larghezza desiderata dell'immagine ridimensionata.

Returns:
    int: - L'altezza proporzionale calcolata.
"""
def get_proportional_height(target,t_width, t_height, desired_width):

    # Calcola l'altezza proporzionale
    aspect_ratio = t_width / t_height
    desired_height = int(desired_width / aspect_ratio)

    return desired_height


"""
    Esegue la sottrazione dello sfondo dall'immagine di input utilizzando un sottrattore specificato.
    
    Argomenti:
    - frame: l'immagine di input su cui applicare la sottrazione dello sfondo.
    - subtractor: il modello di sottrattore di sfondo da utilizzare.

    Restituisce:
    - masked_frame: l'immagine risultante con lo sfondo sottratto.
"""
def background_subtraction(frame, subtractor):
    # Applica la sottrazione dello sfondo
    fg_mask = subtractor.apply(frame)
    # Trova i contorni
    contours, hierarchy = cv.findContours(fg_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # Applica una sogliatura globale per rimuovere le ombre
    retval, mask_thresh = cv.threshold(fg_mask, 180, 255, cv.THRESH_BINARY)
    # Imposta il kernel
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
    # Applica l'erosione
    mask_eroded = cv.morphologyEx(mask_thresh, cv.MORPH_OPEN, kernel)
    # Applica l'operazione AND bit a bit tra il frame originale e la maschera erosa
    masked_frame = cv.bitwise_and(frame, frame, mask=mask_eroded)
    return masked_frame

"""
    Trova la bounding box dell'oggetto di interesse nell'immagine utilizzando una maschera di colore.

    Argomenti:
    - frame: l'immagine di input su cui applicare la ricerca della bounding box.
    - lowerLimit: il limite inferiore dell'intervallo di colore nell'immagine HSV per il rilevamento.
    - upperLimit: il limite superiore dell'intervallo di colore nell'immagine HSV per il rilevamento.

    Restituisce:
    - bbox: la bounding box dell'oggetto di interesse nell'immagine, o None se l'oggetto non è stato trovato.
"""
def get_marker_boundingbox(frame, lowerLimit, upperLimit):
    # Converti l'immagine BGR in HSV
    hsvImage = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # Crea una maschera utilizzando l'intervallo di colore specificato
    mask = cv.inRange(hsvImage, lowerLimit, upperLimit)
    # Converte la maschera in un oggetto immagine
    mask_ = Image.fromarray(mask)
    # Trova la bounding box dell'oggetto nell'immagine
    bbox = mask_.getbbox()
    # Restituisce la bounding box dell'oggetto
    return bbox

"""
    Calcola la velocità di un oggetto in un video.

    Argomenti:
    - start_x: La coordinata x di partenza dell'oggetto.
    - start_y: La coordinata y di partenza dell'oggetto.
    - end_x: La coordinata x di arrivo dell'oggetto.
    - end_y: La coordinata y di arrivo dell'oggetto.
    - video_fps: Il frame rate del video.

    Restituisce:
    - speed: La velocità dell'oggetto in millimetri al secondo.
"""
def compute_speed(x0, y0, x, y, video_fps):
    # Calcola l'intervallo di tempo tra due frame consecutivi in secondi
    time_sec = 1 / video_fps
    print("Tempo tra due frame consecutivi: {}".format(time_sec))

     # Calcola la variazione delle coordinate x e y tra i due frame
    dx = (x - x0)
    dy = (y - y0)

    # Calcola la distanza Euclidea tra i due punti nel piano 2D
    distance_px = math.sqrt(pow(dx, 2) + pow(dy, 2))

    # Converte la distanza in pixel in millimetri
    distance_mm = distance_px * PIXEL_DIMENTION_mm

    # Calcola la velocità dividendo la distanza percorsa per l'intervallo di tempo tra i frame
    speed = distance_mm / time_sec
    print("dx= {} dy= {} distance_px= {} distance_mm= {} speed= {}".format(dx, dy, distance_px, distance_mm, speed))
    
    return speed

"""
    Calcola la distanza tra la telecamera e un oggetto utilizzando le dimensioni dell'oggetto rilevato.

    Argomenti:
    - sensor_obj_dim: le dimensioni dell'oggetto rilevato sul sensore della telecamera.

    Restituisce:
    - La distanza stimata tra la telecamera e l'oggetto in millimetri.
"""
def compute_distance(sensor_obj_dim):
    # Calcola dimensione oggetto sul sensore in mm
    sensor_obj_dim_mm = sensor_obj_dim * PIXEL_DIMENTION_mm

    # Calcola la distanza stimata [dim_reale : distance = dim_sensore : lunghezza_focale]
    distance = REAL_MARKER_DIMENTION_mm / sensor_obj_dim_mm * FOCAL_LENGHT_mm
    return distance

"""
    Calcola (ROM - Range of Movement) utilizzando la didtanza dell'oggetto dalla camera e le coordinate Y massime e minime
    raggiunte dall'utente.

    Argomenti:
    - obj_distance: Distanza dell'oggetto dalla camera in mm
    - y_max: la coordinata Y massima dell'oggetto rilevato.
    - y_min: la coordinata Y minima dell'oggetto rilevato.

    Restituisce:
    - L'ampiezza del campo visivo (ROM) in millimetri.
    """
def compute_rom(obj_distance , y_min, y_max):
    # Calcola ROM sul sensore in mm
    sensor_rom_mm = (y_max - y_min) * PIXEL_DIMENTION_mm

    # Calcola ROM reale [dim_reale : distance = dim_sensore : lunghezza_focale]
    real_rom_mm = ((sensor_rom_mm) / FOCAL_LENGHT_mm) * obj_distance 
    return real_rom_mm

"""
    Calcola la velocità di un oggetto in un video.

    Argomenti:
    - rom: Moviemento effettuato nel mondo reale in mm
    - n_frame: Numero di frame trascorsi fino al momento del calcolo
    - fps: Frame rate del video

    Restituisce:
    - speed: La velocità di esecuzione in millimetri al secondo.
"""
def compute_rom_speed(rom, n_frame, fps):
    # Calcola il tempo trascorso
    t= n_frame / fps

    # Calcola la velocità dividendo la distanza percorsa per l'intervallo di tempo tra i frame
    speed = rom / t
    return speed


