"""Prueba S1 sintética en servicios reales. Requiere login_local y Compose activo."""
import argparse,json,os,socket,time,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
from cysa.contracts import Conteo,Estado
from cysa.mqtt import Publisher

def validate_updates(samples):
    if not samples:return {'cumple':False,'motivo':'Sin muestras'}
    stamps=sorted({datetime.fromisoformat(s['timestamp'].replace('Z','+00:00')) for s in samples})
    gaps=[(b-a).total_seconds() for a,b in zip(stamps,stamps[1:])]
    ages=[s['edad_s'] for s in samples]
    return {'cumple':len(stamps)>=3 and max(gaps,default=999)<=30 and max(ages)<=30,
      'actualizaciones_distintas':len(stamps),'max_gap_s':max(gaps,default=None),'max_edad_s':max(ages)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--api',default='http://localhost:8088/api');p.add_argument('--out',type=Path,required=True)
    p.add_argument('--solo-roles',choices=['operador','administrador']);p.add_argument('--duracion-estados',type=int,default=65)
    a=p.parse_args();root=Path(__file__).resolve().parents[2]
    if a.out.exists():p.error('Elegir una salida nueva; no sobrescribir evidencia')
    if not os.environ.get('CYSA_TOKEN'):p.error('Ejecutar mediante login_local.py; no colocar token en argumentos')
    if not a.solo_roles and not 65<=a.duracion_estados<=180:p.error('Prueba de estados entre 65 y 180 s')
    a.out.mkdir(parents=True);results=[]
    def api(path,method='GET',body=None,authorized=True):
        headers={'Content-Type':'application/json'}
        if authorized:headers['Authorization']='Bearer '+os.environ['CYSA_TOKEN']
        req=urllib.request.Request(a.api+path,headers=headers,method=method,data=None if body is None else json.dumps(body).encode())
        try:
            with urllib.request.urlopen(req,timeout=10) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as e:
            try:body=json.loads(e.read())
            except ValueError:body={}
            return e.code,body
    def run(name,fn):
        try:
            detail=fn();results.append({'prueba':name,'estado':'PASS_SINTETICO','detalle':detail or 'OK'})
        except Exception as e:results.append({'prueba':name,'estado':'FAIL','detalle':type(e).__name__+': '+str(e)[:240]})
    def expect(path,status,**kwargs):
        code,body=api(path,**kwargs)
        if code!=status:raise AssertionError(f'{path.split("?")[0]}: esperado {status}, recibido {code}')
        return body
    run('Sin token se rechazan consultas',lambda:expect('/conteos',401,authorized=False))
    run('Consulta con rol autenticado',lambda:expect('/estados',200))
    run('Activación de planes ausente',lambda:expect('/planes',404,method='POST',body={}))
    if a.solo_roles:
        expected=403 if a.solo_roles=='operador' else 422
        # Carga vacía: el administrador pasa autorización pero falla validación; no modifica inventario.
        run('Permiso de escritura '+a.solo_roles,lambda:expect('/inventario/carga',expected,method='POST',body={'items':[]}))
    else:
        for line in (root/'infra/runtime/clientes/prueba.env').read_text(encoding='utf-8-sig').splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                k,v=line.split('=',1);os.environ[k]=v
        def inventory():
            import csv
            rows=list(csv.DictReader((root/'data/cristhian/ejemplos/inventario_DEMO.csv').open(encoding='utf-8')))
            for r in rows:r['prueba']=True;r['acceso']=r['acceso'] or None
            expect('/inventario/carga',200,method='POST',body={'items':rows})
            camera=next(x for x in rows if x['tipo']=='camara')
            expect('/inventario/'+camera['activo_id'],200,method='PUT',body=camera)
            items=expect('/inventario',200)['items']
            if not {x['activo_id'] for x in rows}<={x['activo_id'] for x in items}:raise AssertionError('Inventario no recuperado')
            return 'Activos DEMO cargados, consultados y editados con administrador'
        run('Inventario sintético',inventory)
        now=datetime.now(timezone.utc);uid=uuid4();lane='QA_'+uid.hex[:12]
        count=Conteo(mensaje_id=uid,interseccion='DEMO_INT_01',acceso='N',carril=lane,clase='auto',cantidad=3,
          inicio=now-timedelta(seconds=30),fin=now,prueba=True)
        query=urllib.parse.urlencode({'desde':(now-timedelta(minutes=1)).isoformat(),'hasta':(now+timedelta(minutes=2)).isoformat(),
          'interseccion':'DEMO_INT_01','carril':lane,'limit':1000})
        def rows():return expect('/conteos?'+query,200)['items']
        def tls_plain():
            packet=bytes.fromhex('10 10 00 04 4d 51 54 54 04 02 00 3c 00 04 74 65 73 74')
            with socket.create_connection((os.environ['MQTT_HOST'],int(os.environ['MQTT_PORT'])),timeout=5) as s:
                s.settimeout(5)
                try:s.sendall(packet);reply=s.recv(4)
                except (ConnectionResetError,ConnectionAbortedError):reply=b''
                if reply.startswith(b'\x20'):raise AssertionError('MQTT plano recibió CONNACK')
            with socket.socket() as s:
                s.settimeout(2)
                if s.connect_ex(('127.0.0.1',1883))==0:raise AssertionError('Hay servicio accesible en 1883; revisar listener')
            return 'Listener TLS cerró MQTT plano; localhost:1883 no está abierto'
        run('Sin listener plano accesible',tls_plain)
        try:
            with Publisher('cysa-aceptacion') as pub:
                def persistence():
                    pub.publish(count);pub.publish(count)
                    deadline=time.monotonic()+30
                    while time.monotonic()<deadline:
                        found=[r for r in rows() if r['mensaje_id']==str(uid)]
                        if found:
                            if len(found)!=1 or found[0]['cantidad']!=3 or found[0]['prueba'] is not True:raise AssertionError('Dato incorrecto o duplicado')
                            return {'mensaje_id':str(uid),'cantidad':3,'filas_persistidas':1,'prueba':True}
                        time.sleep(1)
                    raise TimeoutError('Broker confirmó pero el conteo no llegó a API en 30 s')
                run('TLS, MQTT, BD y API con duplicado QoS1',persistence)
                def invalid():
                    invalid_id=uuid4();bad=count.model_dump(mode='json');bad.update({'mensaje_id':str(invalid_id),'imagen':'PROHIBIDO'})
                    info=pub.client.publish('corredor/DEMO_INT_01/N/conteos',json.dumps(bad),qos=1);info.wait_for_publish(timeout=10)
                    # Barrera: publicar un evento válido posterior y esperar su persistencia.
                    barrier=count.model_copy(update={'mensaje_id':uuid4(),'cantidad':0})
                    pub.publish(barrier);deadline=time.monotonic()+30
                    while time.monotonic()<deadline:
                        got=rows()
                        if any(r['mensaje_id']==str(invalid_id) for r in got):raise AssertionError('Se persistió mensaje con campo imagen')
                        if any(r['mensaje_id']==str(barrier.mensaje_id) for r in got):return 'Mensaje inválido descartado; barrera válida posterior persistida'
                        time.sleep(1)
                    raise TimeoutError('No se pudo confirmar procesamiento de la barrera')
                run('Mensaje fuera de contrato rechazado',invalid)
                def states():
                    samples=[];begin=time.monotonic();next_pub=begin;last=None
                    while time.monotonic()-begin<a.duracion_estados:
                        tick=time.monotonic()
                        if tick>=next_pub:
                            pub.publish(Estado(mensaje_id=uuid4(),interseccion='DEMO_INT_01',fase_actual='NS',plan_activo='DEMO_FIJO',
                              estado_controlador='conectado',timestamp=datetime.now(timezone.utc),prueba=True));next_pub+=25
                        data=expect('/estados',200)['items'];item=next((x for x in data if x['interseccion']=='DEMO_INT_01'),None)
                        if item:
                            stamp=datetime.fromisoformat(item['timestamp'].replace('Z','+00:00'))
                            age=max(0,(datetime.now(timezone.utc)-stamp).total_seconds())
                            # Esperar primer estado de esta ejecución, no juzgar uno antiguo de otra corrida.
                            if stamp>=now:
                                if item['prueba'] is not True:raise AssertionError('Se perdió la marca prueba')
                                samples.append({'timestamp':item['timestamp'],'edad_s':round(age,3)})
                        time.sleep(1)
                    result=validate_updates(samples)
                    (a.out/'muestras_estados.json').write_text(json.dumps(samples,indent=2),encoding='utf-8')
                    if not result['cumple']:raise AssertionError(json.dumps(result))
                    return result
                run('Estados sintéticos cada <=30 s durante ensayo breve',states)
        except Exception as e:results.append({'prueba':'Conexión MQTT','estado':'FAIL','detalle':type(e).__name__})
    report={'origen':'PRUEBA SINTETICA EN SERVICIOS LOCALES','ejecutado_utc':datetime.now(timezone.utc).isoformat(),'casos':results,
      'validacion_trafico_real':False,'panel_visual':'PENDIENTE DE PRUEBA HUMANA','calibracion_real':'PENDIENTE',
      'nota':'El PASS sintético no acepta el sprint completo ni reemplaza la aprobación docente.'}
    (a.out/'resultado.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    for r in results:print(r['estado']+': '+r['prueba'])
    if any(r['estado']=='FAIL' for r in results):raise SystemExit(1)
if __name__=='__main__':main()
