"""Un cuadro en RAM para comprobar disponibilidad; no muestra ni guarda imagen."""
import argparse

def main():
    import cv2
    p=argparse.ArgumentParser();p.add_argument('--source',default='0');a=p.parse_args()
    source=int(a.source) if a.source.isdigit() else a.source
    cap=cv2.VideoCapture(source)
    try:
        ok,frame=cap.read()
        if not ok:raise SystemExit('No hay cuadro disponible. Revisar conexión/permisos/índice de cámara.')
        height,width=frame.shape[:2];del frame
        print(f'Fuente disponible: {width} x {height}. Cuadro descartado; no acredita escena de tráfico ni precisión.')
    finally:cap.release()
if __name__=='__main__':main()
