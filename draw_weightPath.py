import cv2 as cv
import numpy as np
import util

def draw_path(read_path):
    # Tolleranza del bbox in px
    BBOX_TOLLERANCE = 20
    # Tolleranza per oscillazioni del dispositivo
    CAP_TOLLERANCE = 30

    # Apre il video specificato nel percorso
    cap = cv.VideoCapture(read_path)

    # Controlla se il video è stato aperto correttamente
    if not cap.isOpened():
        print("Errore nell'apertura del video")
        raise OSError("Impossibile aprire il video: il file potrebbe non esistere o il percorso potrebbe essere errato.")
    else:
        
        # Ottiene l'altezza e la larghezza del video
        video_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("Original Dimension {} x {}".format(video_width, video_height))
        
        # Definisci la larghezza desiderata e ottieni l'altezza per la visualizzazione
        desired_width = 500
        desired_height = util.get_proportional_height(cap, video_width,video_height, desired_width)
        print("New Dimension {} x {}".format(desired_width, desired_height))

        # Definisci il colore da riconoscere e calcola i limiti inf e sup da includere
        target_color = [0,255,130]
        lowerLimit, upperLimit = util.get_value_range(color = target_color)
        print("LowerLimit: {} MiddleValue: {} UpperLimit: {}".format(lowerLimit, target_color, upperLimit))
        
        # Leggi il frame rate del video
        fps = cap.get(cv.CAP_PROP_FPS)

        # Inizializzazione delle variabili di controllo
        frame_counter, xp, yp, y_min, y_max = np.zeros(5)
        # Per tenere traccia delle coordinate e dimensione del bbox
        old_x1, old_y1, old_x2, old_y2, old_bbox_height, old_bbox_width = np.zeros(6)
        # Per chiudere il percorso
        first_coordinate = last_coordinete = (0,0)
        # Crea un canvas vuoto delle stesse dimensioni del frame
        img_canvas = np.zeros((video_height, video_width, 3), np.uint8)
        # Crea il sottrattore dello sfondo
        backSub = cv.createBackgroundSubtractorMOG2()
        # Parametri da calcolare
        distance = rom = rom_speed = None
        
    while cap.isOpened():

        # Lettura della cattura
        ret, frame = cap.read()

        # Controlla se il frame è stato letto correttamente
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break  # Esci dal loop

        # Tieni traccia dei frame trascorsi
        if rom_speed is None:
            frame_counter = frame_counter + 1

        # Sottrazione dello sfondo dal frame
        masked_frame = util.background_subtraction(frame, backSub)

        # Ottieni il Bounding Box del marker
        bbox = util.get_marker_boundingbox(masked_frame, lowerLimit, upperLimit)

        if bbox is not None:
            # Assegna coordinate bbox
            new_x1, new_y1, new_x2, new_y2 = bbox
            new_bbox_height, new_bbox_width = util.get_bbox_dimensions(new_x1, new_y1, new_x2, new_y2)
            sensor_marker_dimention = new_bbox_height

            # Se non è stato ancora assegnato un bbox
            if old_bbox_height == 0 and old_bbox_width == 0:
                old_x1, old_y1, old_x2, old_y2 = new_x1, new_y1, new_x2, new_y2
                old_bbox_height, old_bbox_width = new_bbox_height, new_bbox_width

            # Se new_bbox_dimentions > old_bbox_dimentions + tollerance mantengo il bbox precedente
            if abs(new_bbox_height - old_bbox_height) > BBOX_TOLLERANCE or abs(new_bbox_width - old_bbox_width) > BBOX_TOLLERANCE:
                new_x1, new_y1, new_x2, new_y2 = old_x1, old_y1, old_x2, old_y2
                new_bbox_height, new_bbox_width = old_bbox_height, old_bbox_width

            # Altrimenti aggiorno il bbox
            else:
                old_x1, old_y1, old_x2, old_y2 = new_x1, new_y1, new_x2, new_y2
                old_bbox_height, old_bbox_width = new_bbox_height, new_bbox_width
                        
            # Disegna il Bounding Box
            frame = cv.rectangle(frame, (new_x1, new_y1), (new_x2, new_y2), (0, 255, 0), 5)
            # Ottiene le coordinate del centro del cerchio
            x_center, y_center = util.get_circle_center_coordinates(new_x1, new_x2, new_y1, new_y2)

            # Prima cattura
            if xp == 0 and yp == 0:
                # Imposta le coordinate del punto precedente
                xp, yp = x_center, y_center
                y_min = y_max = y_center
                first_coordinate = (x_center, y_center)
            
            if distance is None:
                # Calcolo e stampa la distanza del marker dalla camera
                distance = util.compute_distance(sensor_marker_dimention)
            else:
                frame = cv.putText(frame, f"Distance: {(distance/1000):.1f} m",(x_center + 50 , y_center + 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Se il centro è maggiore del valore massimo allora sto scendendo
            if y_center > y_max:
                y_max = y_center
            # altrimenti sto salendo
            elif y_center + CAP_TOLLERANCE < y_max and rom is None:
                # Calcolo del rom di movimento e la velocità di esecuzione
                rom = util.compute_rom(distance, y_min, y_max)
                rom_speed = util.compute_rom_speed(rom, frame_counter, fps)

            # Se parametri sono staticalcolati allora stampali
            if rom is not None and rom_speed is not None:
                frame = cv.putText(frame, f"ROM: {(rom/1000):.2f} m",(video_width -400 , 50 ), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                frame = cv.putText(frame, f"ROM speed: {(rom_speed/1000):.2f} m/s",(video_width -400 , 100), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


            # Disegna il path del bilancere
            img_canvas = cv.line(img_canvas, (xp, yp), (x_center, y_center), (0, 0, 255), 10)
            # Aggiorna le coordinate del punto precedente
            xp, yp = x_center, y_center
            last_coordinete = (x_center, y_center)

        # Effettua l'unione del frame con il canva
        canvas_gray = cv.cvtColor(img_canvas, cv.COLOR_BGR2GRAY)
        _, imgInv = cv.threshold(canvas_gray, 50, 255, cv.THRESH_BINARY_INV)
        imgInv = cv.cvtColor(imgInv, cv.COLOR_GRAY2BGR)
        frame_edit = cv.bitwise_and(frame, imgInv)
        frame_edit = cv.bitwise_or(frame, img_canvas)

        # Crea una finestra, imposta dim e mostra
        util.img_show('frame', desired_width, desired_height, frame)
        # Visualizza il canvas con il path del percorso
        util.img_show('canvas', desired_width, desired_height, frame_edit)
        
        # Attendi 30 millisecondi per un tasto premuto (25 millisecondi di ritardo tra i frame)
        if cv.waitKey(30) == ord('q'):
            break  # Se viene premuto 'q', esci dal loop

    # Disegna la linea per chiudere il path del bilancere
    img_canvas = cv.line(img_canvas, (last_coordinete[0], last_coordinete[1]), (first_coordinate[0], first_coordinate[1]), (0, 0, 255), 10)
    # Scrivi tutte le info nell'immagine path_execution.png
    img_canvas = util.write_canvasData(img_canvas, video_width, distance, rom, rom_speed)

    # Rilascia il video e chiudi tutte le finestre
    cap.release()
    cv.destroyAllWindows()
    return img_canvas