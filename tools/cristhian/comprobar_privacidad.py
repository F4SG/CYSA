"""Revisión local de carpetas de ejecución; no inspecciona la PC entera ni muestra archivos sensibles."""
import argparse,json
from pathlib import Path
EXT={'.mp4','.avi','.mov','.mkv','.jpg','.jpeg','.png','.bmp','.webp'}
def scan(paths):
    found=[]
    for root in paths:
        if not root.exists():continue
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in EXT:found.append(str(p.relative_to(root)))
    return found

def main():
    p=argparse.ArgumentParser();p.add_argument('--carpeta',action='append',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    existentes=[x for x in a.carpeta if x.is_dir()]
    found=scan(existentes);a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps({'archivos_multimedia_encontrados':found,'carpetas_inspeccionadas':len(existentes),'carpetas_omitidas':len(a.carpeta)-len(existentes),'estado':('INCONCLUSO' if not existentes else ('REVISAR' if found else 'SIN_ARCHIVOS_EN_CARPETAS_INSPECCIONADAS')),
      'limite':'No cubre logs, BD, carpetas no indicadas ni borrados anteriores. No elimina archivos.'},indent=2),encoding='utf-8')
    if found or not existentes:raise SystemExit(1)
    print('No se encontraron imágenes/videos en las carpetas indicadas; completar revisión SQL y MQTT.')
if __name__=='__main__':main()
