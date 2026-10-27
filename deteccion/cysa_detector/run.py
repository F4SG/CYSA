import argparse,csv,json,time
from pathlib import Path
from datetime import datetime,timezone
from uuid import uuid4
from cysa.contracts import Conteo
from cysa.interfaces import FuenteDeteccion
from cysa.mqtt import Publisher
from .counter import Lane,LineCounter

class CameraSource(FuenteDeteccion):
    def __init__(self,config):self.config=config
    def eventos(self):
        import cv2
        from ultralytics import YOLO
        c=self.config
        if not c.get('interseccion') or not c.get('lanes'):raise ValueError('Completar intersección y líneas en YAML')
        if not isinstance(c.get('prueba'),bool):raise ValueError('prueba debe ser booleano')
        seconds=c.get('intervalo_s',30)
        if not isinstance(seconds,(int,float)) or not 1<=seconds<=30:raise ValueError('intervalo_s entre 1 y 30')
        source=c.get('source',0)
        # stream/video externo se lee sin copiarlo; únicamente fuente secuencial, jamás paquetes de imágenes.
        cap=cv2.VideoCapture(source)
        if not cap.isOpened():raise RuntimeError('No se pudo abrir la fuente configurada')
        lanes=[Lane(x['acceso'],x['carril'],tuple(x['a']),tuple(x['b']),x['direction']) for x in c['lanes']]
        counter=LineCounter(lanes)
        model=YOLO(c.get('model','yolo26n.pt'))
        mapping={int(k):v for k,v in c['class_map'].items()}
        try:
            yield from self._loop(cap,model,counter,mapping,seconds,cv2)
        finally:cap.release()
    def _loop(self,cap,model,counter,mapping,seconds,cv2):
        c=self.config;start=datetime.now(timezone.utc);tick=time.monotonic()
        def flush(end):
            counts=counter.snapshot()
            for lane in counter.lanes:
                for clase in ['auto','micro','moto']:
                    yield Conteo(mensaje_id=uuid4(),interseccion=c['interseccion'],acceso=lane.acceso,carril=lane.carril,
                      clase=clase,cantidad=counts.get((lane.acceso,lane.carril,clase),0),inicio=start,fin=end,prueba=c['prueba'])
        while True:
            ok,frame=cap.read()
            if not ok:break
            h,w=frame.shape[:2]
            results=model.track(frame,persist=True,tracker='bytetrack.yaml',classes=list(mapping),
              conf=float(c.get('confidence',0.3)),device=c.get('device','cpu'),
              save=False,save_txt=False,save_crop=False,save_frames=False,show=False,verbose=False)
            now_tick=time.monotonic()
            # Emitir intervalos válidos; si la inferencia tardó >30.5 s, detener antes de publicar datos fuera del contrato.
            if now_tick-tick>30.5:raise RuntimeError('Procesamiento demasiado lento: reducir resolución/modelo o usar GPU')
            boxes=results[0].boxes
            if boxes is not None and boxes.id is not None:
                for xyxy,tid,cls in zip(boxes.xyxy.cpu().tolist(),boxes.id.int().cpu().tolist(),boxes.cls.int().cpu().tolist()):
                    x1,y1,x2,y2=xyxy
                    counter.observe(tid,mapping.get(cls),((x1+x2)/(2*w),y2/h),now_tick)
            counter.prune(now_tick)
            del results,boxes,frame
            if now_tick-tick>=seconds:
                end=datetime.now(timezone.utc)
                yield from flush(end)
                counter.reset_interval();start=end;tick=now_tick
        # Al detener o al EOF no fabricar ceros para un intervalo completo. Publicar solo el tramo efectivamente observado.
        end=datetime.now(timezone.utc)
        if 0<(end-start).total_seconds()<=30.5:
            yield from flush(end)

def main():
    import yaml
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True)
    p.add_argument('--salida-conteos',type=Path,required=True,help='CSV agregado; nunca imágenes')
    a=p.parse_args();config=yaml.safe_load(a.config.read_text(encoding='utf-8'))
    if not config.get('configuracion_verificada',False):p.error('Adaptar y verificar líneas/fuente y marcar configuracion_verificada=true')
    source=CameraSource(config)
    a.salida_conteos.parent.mkdir(parents=True,exist_ok=True)
    exists=a.salida_conteos.exists() and a.salida_conteos.stat().st_size>0
    with a.salida_conteos.open('a',encoding='utf-8',newline='') as out,Publisher('cysa-deteccion') as pub:
        writer=None
        try:
            for event in source.eventos():
                row=event.model_dump(mode='json')
                if writer is None:
                    writer=csv.DictWriter(out,fieldnames=list(row))
                    if not exists:writer.writeheader()
                # El CSV permite reintentar un evento con el mismo UUID si el broker no confirma.
                writer.writerow(row);out.flush();pub.publish(event)
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
