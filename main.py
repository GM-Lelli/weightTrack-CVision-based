import cv2 as cv
import sys
import draw_weightPath

def main():
    # Verifica che l'utente abbia fornito i due argomenti richiesti
    if len(sys.argv) != 3:
        print("Uso corretto: python main.py 'path_di_lettura' 'path_di_scrittura'")
        sys.exit(1)

    # Ottieni i percorsi dal terminale
    read_path = sys.argv[1]
    write_path = sys.argv[2]

    # Stampa i percorsi per conferma
    print(f"Percorso di lettura: {read_path}")
    print(f"Percorso di scrittura: {write_path}")

    try:
        # Qui puoi aggiungere il codice per leggere e scrivere i file utilizzando i percorsi specificati
        img_canvas = draw_weightPath.draw_path(read_path)
        cv.imwrite(write_path,img_canvas)

    except ValueError as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()