"""Proceso separado de FastAPI: un suscriptor, confirmación después de persistir."""
import logging,os,time
from cysa.mqtt import client
from cysa.contracts import decode_message
from app.repository import Repository
log=logging.getLogger('cysa.consumer')
def main():
    logging.basicConfig(level=logging.INFO)
    repo=Repository();repo.ready()
    c=client('cysa-plataforma',manual_ack=True)
    def connected(client,userdata,flags,reason,properties):
        if reason.is_failure:log.error('MQTT rechazó autenticación');return
        client.subscribe([('corredor/+/+/conteos',1),('corredor/+/estado',1)])
    def message(client,userdata,msg):
        try:event=decode_message(msg.topic,msg.payload)
        except ValueError:
            log.warning('Mensaje descartado: contrato o tópico inválido')
            if msg.qos:client.ack(msg.mid,msg.qos)
            return
        # No confirmar hasta escribir. El reintento mantiene el mismo evento, sin perderlo en reconexión.
        delay=1
        while True:
            try:repo.save(event);break
            except Exception:
                log.error('Persistencia no disponible; se reintenta sin registrar el payload')
                time.sleep(delay);delay=min(30,delay*2)
        if msg.qos:client.ack(msg.mid,msg.qos)
    c.on_connect=connected;c.on_message=message
    c.connect(os.environ.get('MQTT_HOST','mosquitto'),int(os.environ.get('MQTT_PORT','8883')),60)
    try:c.loop_forever(retry_first_connection=True)
    finally:c.disconnect()
if __name__=='__main__':main()
