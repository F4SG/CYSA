"""Geometría y conteo sin dependencias de cámara; no conserva imágenes."""
from dataclasses import dataclass
from collections import Counter
@dataclass(frozen=True)
class Lane:
    acceso:str
    carril:str
    a:tuple[float,float]
    b:tuple[float,float]
    direction:str='negative_to_positive'
    def __post_init__(self):
        if self.a==self.b:raise ValueError('La línea debe tener longitud')
        if self.direction not in ['negative_to_positive','positive_to_negative','both']:raise ValueError('Dirección inválida')
        if not all(0<=v<=1 for p in [self.a,self.b] for v in p):raise ValueError('Coordenadas normalizadas 0..1')
def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def on_segment(a,b,p,q):
    """El recorrido debe intersectar el segmento finito, no su prolongación."""
    return cross(p,q,a)*cross(p,q,b)<=0
class LineCounter:
    def __init__(self,lanes,ttl_s=120):
        self.lanes=lanes;self.ttl=ttl_s;self.tracks={};self.counts=Counter()
        if len({(l.acceso,l.carril) for l in lanes})!=len(lanes):raise ValueError('Carril repetido')
    def observe(self,track_id,clase,point,timestamp):
        if clase not in ['auto','micro','moto']:return
        record=self.tracks.get(track_id,{'last':{},'counted':set(),'seen':timestamp})
        record['seen']=timestamp
        for i,l in enumerate(self.lanes):
            side=cross(l.a,l.b,point)
            if abs(side)<1e-7:continue
            prev=record['last'].get(i)
            if prev and i not in record['counted']:
                old,p=prev
                direction='negative_to_positive' if old<0<side else 'positive_to_negative'
                if old*side<0 and (l.direction in ['both',direction]) and on_segment(l.a,l.b,p,point):
                    self.counts[(l.acceso,l.carril,clase)]+=1;record['counted'].add(i)
            record['last'][i]=(side,point)
        self.tracks[track_id]=record
    def prune(self,timestamp):
        self.tracks={k:v for k,v in self.tracks.items() if timestamp-v['seen']<=self.ttl}
    def snapshot(self):return dict(self.counts)
    def reset_interval(self):self.counts.clear() # Conservar IDs para no duplicar al cambiar de intervalo.
