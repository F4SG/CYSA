"""Reenvío explícito de CSV agregado. Conserva mensaje_id: idempotencia en TimescaleDB."""
import argparse,csv
from pathlib import Path
from cysa.contracts import Conteo
from cysa.mqtt import Publisher

def main():
    p=argparse.ArgumentParser();p.add_argument('csv',type=Path);a=p.parse_args()
    count=0
    with a.csv.open(encoding='utf-8-sig',newline='') as f,Publisher('cysa-reenvio') as pub:
        for row in csv.DictReader(f):
            if row['prueba'].lower() not in ['true','false']:raise ValueError('Marca prueba inválida')
            row['prueba']=row['prueba'].lower()=='true';row['cantidad']=int(row['cantidad'])
            pub.publish(Conteo.model_validate(row));count+=1
    print(f'{count} eventos reenviados con sus UUID originales. Confirmar persistencia por API.')
if __name__=='__main__':main()
