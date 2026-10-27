import argparse,time
from datetime import datetime,timedelta,timezone
from uuid import uuid4
from cysa.contracts import Conteo,Estado
from cysa.mqtt import Publisher

def main():
    p=argparse.ArgumentParser(description='Publicador sintético, siempre prueba=true')
    p.add_argument('--ciclos',type=int,default=1);a=p.parse_args()
    if a.ciclos<1:p.error('ciclos debe ser positivo')
    with Publisher('cysa-prueba') as pub:
        for n in range(a.ciclos):
            now=datetime.now(timezone.utc)
            for clase,qty in [('auto',3),('micro',1),('moto',2)]:
                pub.publish(Conteo(mensaje_id=uuid4(),interseccion='DEMO_INT_01',acceso='N',carril='N_0',
                  clase=clase,cantidad=qty,inicio=now-timedelta(seconds=30),fin=now,prueba=True))
            pub.publish(Estado(mensaje_id=uuid4(),interseccion='DEMO_INT_01',fase_actual='NS',plan_activo='DEMO_FIJO',
              estado_controlador='conectado',timestamp=now,prueba=True))
            if n<a.ciclos-1:time.sleep(30)
if __name__=='__main__':main()
