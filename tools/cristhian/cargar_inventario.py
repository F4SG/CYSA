import argparse,csv,json,os,urllib.request
from pathlib import Path
from cysa.contracts import Activo

def leer_csv(path):
    items=[]
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for line,row in enumerate(csv.DictReader(f),2):
            try:
                if row['prueba'].lower() not in ['true','false']:raise ValueError('prueba debe ser true/false')
                row['prueba']=row['prueba'].lower()=='true';row['acceso']=row['acceso'] or None
                items.append(Activo.model_validate(row))
            except (ValueError,KeyError) as ex:raise ValueError(f'Fila {line}: CSV inválido') from ex
    if not items:raise ValueError('CSV sin activos; completar plantilla antes de cargar')
    if len(items)>2000:raise ValueError('Máximo 2000 activos por carga')
    if len({a.activo_id for a in items})!=len(items):raise ValueError('IDs duplicados')
    return items

def main():
    p=argparse.ArgumentParser();p.add_argument('csv',type=Path);p.add_argument('--api',default='http://localhost:8088/api')
    p.add_argument('--validar',action='store_true');a=p.parse_args();items=leer_csv(a.csv)
    if a.validar:print(f'OK: {len(items)} activos válidos');return
    data=json.dumps({'items':[x.model_dump() for x in items]}).encode()
    req=urllib.request.Request(a.api+'/inventario/carga',data=data,method='POST',headers={
      'Content-Type':'application/json','Authorization':'Bearer '+os.environ['CYSA_TOKEN']})
    with urllib.request.urlopen(req,timeout=15) as r:print(r.read().decode())
if __name__=='__main__':main()
