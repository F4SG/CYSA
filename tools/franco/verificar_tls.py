"""Prueba activa: socket plano debe cerrarse/rechazarse; TLS autenticado debe publicar."""
import os,socket
from cysa.mqtt import Publisher
from cysa.contracts import Estado
from datetime import datetime,timezone
from uuid import uuid4

def main():
    host=os.environ.get('MQTT_HOST','localhost');port=int(os.environ.get('MQTT_PORT','8883'))
    # MQTT CONNECT 3.1.1 mínimo sin credenciales; no hay datos sensibles en la prueba plana.
    packet=bytes.fromhex('10 10 00 04 4d 51 54 54 04 02 00 3c 00 04 74 65 73 74')
    with socket.create_connection((host,port),timeout=5) as s:
        s.settimeout(5)
        try:s.sendall(packet);reply=s.recv(4)
        except (ConnectionResetError,ConnectionAbortedError):reply=b''
        except socket.timeout:raise SystemExit('INCONCLUSO: conexión plana no recibió respuesta; revisar broker')
        if reply.startswith(b'\x20'):raise SystemExit('FALLO: el listener aceptó MQTT sin TLS')
    with Publisher('cysa-verificacion-tls') as pub:
        pub.publish(Estado(mensaje_id=uuid4(),interseccion='DEMO_INT_01',fase_actual='NS',plan_activo='DEMO_FIJO',
            estado_controlador='conectado',timestamp=datetime.now(timezone.utc),prueba=True))
    print('OK: MQTT plano rechazado y publicación TLS autenticada confirmada por PUBACK.')
if __name__=='__main__':main()
