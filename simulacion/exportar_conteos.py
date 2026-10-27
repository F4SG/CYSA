"""Exporta conteos de la API para demanda SUMO; no requiere descargar video."""
import argparse,csv,json,os,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime

def main():
    p=argparse.ArgumentParser();p.add_argument('--api',default='http://localhost:8088/api')
    for arg in ['desde','hasta','interseccion']:p.add_argument('--'+arg,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    start,end=[datetime.fromisoformat(x.replace('Z','+00:00')) for x in [a.desde,a.hasta]]
    if start.tzinfo is None or end.tzinfo is None or start>=end:p.error('Fechas con zona y rango válido requeridas')
    fields=['interseccion','acceso','carril','clase','cantidad','inicio','fin','prueba']
    rows=[];offset=0
    while True:
        q=urllib.parse.urlencode({'desde':a.desde,'hasta':a.hasta,'interseccion':a.interseccion,'limit':1000,'offset':offset})
        req=urllib.request.Request(a.api+'/conteos?'+q,headers={'Authorization':'Bearer '+os.environ['CYSA_TOKEN']})
        with urllib.request.urlopen(req,timeout=15) as r:items=json.load(r)['items']
        rows.extend(items)
        if len(items)<1000:break
        offset+=len(items)
    if not rows:raise SystemExit('No hay conteos para exportar; no se genera demanda cero ficticia')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in rows:w.writerow({k:str(row[k]).lower() if k=='prueba' else row[k] for k in fields})
    print(f'Exportados {len(rows)} intervalos. Revisar origen, duplicados y correspondencia de accesos antes de simular.')
if __name__=='__main__':main()
