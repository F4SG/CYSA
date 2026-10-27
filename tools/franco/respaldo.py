"""Respaldo binario de conteos/inventario/estados. No empaqueta claves ni passwords."""
import argparse,subprocess,json,hashlib
from pathlib import Path

def compose(root):return ['docker','compose','--env-file',str(root/'infra/.env'),'-f',str(root/'infra/compose.yaml')]
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[2]
    if a.out.exists():p.error('La salida ya existe; elegir un nombre nuevo')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    try:
        with a.out.open('xb') as f:subprocess.run(compose(root)+['exec','-T','db','pg_dump','-U','cysa','-d','cysa','-Fc'],stdout=f,check=True)
    except Exception:raise SystemExit('Falló pg_dump. El archivo parcial NO es un respaldo válido; conservarlo separado para diagnóstico.')
    digest=hashlib.sha256(a.out.read_bytes()).hexdigest()
    a.out.with_suffix(a.out.suffix+'.json').write_text(json.dumps({'formato':'pg_dump custom','sha256':digest,'incluye':'BD de monitoreo, no Keycloak ni runtime TLS','validacion_restauracion':'PENDIENTE'},indent=2),encoding='utf-8')
    print('Respaldo terminado. Falta verificar restauración; archivo local, no anexarlo a un ZIP público si contiene datos reales.')
if __name__=='__main__':main()
