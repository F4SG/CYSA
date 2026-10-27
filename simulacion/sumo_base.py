"""Genera red DEMO o reutiliza una red real con su plan fijo. Solo CLI."""
import argparse,csv,json,os,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element,SubElement,ElementTree

def binary(name):
    found=shutil.which(name)
    if found:return found
    import sumolib
    return sumolib.checkBinary(name)
def write_xml(path,root):ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def load_counts(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    if not rows:raise ValueError('No hay flujos: completar la plantilla')
    seen=set();ints=set()
    for r in rows:
        if r['clase'] not in ['auto','micro','moto'] or r['prueba'].lower() not in ['true','false']:raise ValueError('Clase o marca prueba inválida')
        r['cantidad']=int(r['cantidad']);r['inicio_dt']=datetime.fromisoformat(r['inicio'].replace('Z','+00:00'));r['fin_dt']=datetime.fromisoformat(r['fin'].replace('Z','+00:00'))
        if r['cantidad']<0 or r['inicio_dt'].tzinfo is None or r['fin_dt'].tzinfo is None or r['fin_dt']<=r['inicio_dt']:raise ValueError('Cantidad, zona o intervalo inválido')
        key=tuple(r[k] for k in ['interseccion','acceso','carril','clase','inicio','fin'])
        if key in seen:raise ValueError('Intervalo/carril/clase duplicado')
        seen.add(key);ints.add(r['interseccion'])
    if len(ints)!=1:raise ValueError('Ejecutar una intersección por escenario')
    if sum(r['cantidad'] for r in rows)==0:raise ValueError('Sin vehículos no existe una demora base medible')
    if sum(r['cantidad'] for r in rows)==0:raise ValueError('Sin vehículos no existe una demora base medible')
    if sum(r['cantidad'] for r in rows)==0:raise ValueError('Sin vehículos no existe una demora base medible')
    # Rechazar intervalos que se superpongan para el mismo carril y clase.
    groups={}
    for r in rows:groups.setdefault((r['acceso'],r['carril'],r['clase']),[]).append(r)
    for group in groups.values():
        ordered=sorted(group,key=lambda r:r['inicio_dt'])
        if any(a['fin_dt']>b['inicio_dt'] for a,b in zip(ordered,ordered[1:])):raise ValueError('Intervalos superpuestos')
    return rows

def demo_network(out):
    nodes=Element('nodes')
    for name,x,y,kind in [('C',0,0,'traffic_light'),('N',0,300,'priority'),('S',0,-300,'priority'),('E',300,0,'priority'),('W',-300,0,'priority')]:
        SubElement(nodes,'node',id=name,x=str(x),y=str(y),type=kind)
    edges=Element('edges');connections=Element('connections');mapping={}
    for idx,(acc,target) in enumerate([('N','S'),('S','N'),('E','W'),('W','E')]):
        SubElement(edges,'edge',id=acc+'_in',**{'from':acc,'to':'C','numLanes':'1','speed':'13.89'})
        SubElement(edges,'edge',id=acc+'_out',**{'from':'C','to':acc,'numLanes':'1','speed':'13.89'})
        SubElement(connections,'connection',**{'from':acc+'_in','to':target+'_out','fromLane':'0','toLane':'0','tl':'C','linkIndex':str(idx)})
        mapping[acc]=(acc+'_in',target+'_out')
    tls=Element('additional');logic=SubElement(tls,'tlLogic',id='C',type='static',programID='DEMO_FIJO',offset='0')
    for duration,state in [(30,'GGrr'),(3,'yyrr'),(2,'rrrr'),(30,'rrGG'),(3,'rryy'),(2,'rrrr')]:SubElement(logic,'phase',duration=str(duration),state=state)
    for name,root in [('demo.nod.xml',nodes),('demo.edg.xml',edges),('demo.con.xml',connections),('demo.tll.xml',tls)]:write_xml(out/name,root)
    subprocess.run([binary('netconvert'),'--node-files',str(out/'demo.nod.xml'),'--edge-files',str(out/'demo.edg.xml'),
      '--connection-files',str(out/'demo.con.xml'),'--tllogic-files',str(out/'demo.tll.xml'),'--output-file',str(out/'red.net.xml')],check=True)
    # netconvert puede reordenar linkIndex. Derivar los verdes de las conexiones finales,
    # no de los índices solicitados en PlainXML (evita verdes en conflicto).
    from xml.etree.ElementTree import parse
    tree=parse(out/'red.net.xml');net=tree.getroot()
    connections=[x for x in net.findall('connection') if x.get('tl')=='C']
    size=max(int(x.attrib['linkIndex']) for x in connections)+1
    logic=net.find("tlLogic[@id='C']")
    for child in list(logic):logic.remove(child)
    logic.set('programID','DEMO_FIJO')
    def state_for(accesses,color):
        state=['r']*size
        for x in connections:
            if x.attrib['from'].split('_')[0] in accesses:state[int(x.attrib['linkIndex'])]=color
        return ''.join(state)
    for duration,state in [(30,state_for(['N','S'],'G')),(3,state_for(['N','S'],'y')),(2,'r'*size),
                           (30,state_for(['E','W'],'G')),(3,state_for(['E','W'],'y')),(2,'r'*size)]:
        SubElement(logic,'phase',duration=str(duration),state=state)
    tree.write(out/'red.net.xml',encoding='utf-8',xml_declaration=True)
    actual=Element('additional')
    import copy
    actual.append(copy.deepcopy(logic));write_xml(out/'demo.tll.xml',actual)
    return out/'red.net.xml',mapping

def build_routes(rows,mapping,out):
    routes=Element('routes');base=min(r['inicio_dt'] for r in rows)
    for clase,vclass,length in [('auto','passenger','5'),('micro','bus','10'),('moto','motorcycle','2')]:
        SubElement(routes,'vType',id=clase,vClass=vclass,length=length,accel='2.0',decel='4.5',sigma='0',speedFactor='1')
    for access,(source,target) in mapping.items():SubElement(routes,'route',id='ruta_'+access,edges=source+' '+target)
    for i,r in enumerate(sorted(rows,key=lambda r:r['inicio_dt'])):
        if r['acceso'] not in mapping:raise ValueError('Acceso sin correspondencia en la red: '+r['acceso'])
        if r['cantidad']:
            SubElement(routes,'flow',id=f'{r["acceso"]}__{i}',type=r['clase'],route='ruta_'+r['acceso'],
              begin=str((r['inicio_dt']-base).total_seconds()),end=str((r['fin_dt']-base).total_seconds()),number=str(r['cantidad']),departLane='best')
    write_xml(out/'flujos.rou.xml',routes)
    return max((r['fin_dt']-base).total_seconds() for r in rows)

def summarize(tripinfo,path,prueba):
    from xml.etree.ElementTree import parse
    groups={};unfinished=0
    for t in parse(tripinfo).getroot().findall('tripinfo'):
        if float(t.get('arrival','-1'))<0:unfinished+=1;continue
        access=t.attrib['id'].split('__')[0];delay=float(t.attrib['timeLoss'])
        group=groups.setdefault(access,[]);group.append(delay)
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['acceso','vehiculos_completados','demora_media_timeLoss_s','prueba']);w.writeheader()
        for access,values in sorted(groups.items()):w.writerow({'acceso':access,'vehiculos_completados':len(values),'demora_media_timeLoss_s':f'{sum(values)/len(values):.6f}','prueba':str(prueba).lower()})
    return sum(map(len,groups.values())),unfinished

def main():
    p=argparse.ArgumentParser();p.add_argument('--counts',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--demo',action='store_true');p.add_argument('--network',type=Path);p.add_argument('--access-map',type=Path);p.add_argument('--seed',type=int,default=42)
    a=p.parse_args();rows=load_counts(a.counts);out=a.out.resolve()
    if out.exists() and any(out.iterdir()):p.error('Usar una carpeta de salida nueva/vacía para no mezclar resultados')
    out.mkdir(parents=True,exist_ok=True)
    if a.demo:
        if any(r['prueba'].lower()!='true' for r in rows):p.error('La red DEMO requiere todos los conteos marcados prueba=true')
        network,mapping=demo_network(out);prueba=True
    else:
        if not a.network or not a.access_map:p.error('Para red real proporcionar --network y --access-map; el plan fijo debe estar en la red')
        # Reutilizar la red .net.xml completa; programas adicionales se incorporan con netconvert antes de este comando.
        network=out/'red.net.xml';shutil.copyfile(a.network,network)
        with a.access_map.open(encoding='utf-8-sig',newline='') as f:mapping={r['acceso']:(r['entrada'],r['salida']) for r in csv.DictReader(f)}
        prueba=any(r['prueba'].lower()=='true' for r in rows)
    last=build_routes(rows,mapping,out)
    config=Element('configuration');inputs=SubElement(config,'input');SubElement(inputs,'net-file',value='red.net.xml');SubElement(inputs,'route-files',value='flujos.rou.xml')
    timing=SubElement(config,'time');SubElement(timing,'begin',value='0');SubElement(timing,'end',value=str(last+900))
    processing=SubElement(config,'processing');SubElement(processing,'time-to-teleport',value='-1')
    output=SubElement(config,'output');SubElement(output,'tripinfo-output',value='tripinfo.xml');SubElement(output,'tripinfo-output.write-unfinished',value='true')
    write_xml(out/'base.sumocfg',config)
    command=[binary('sumo'),'-c',str(out/'base.sumocfg'),'--seed',str(a.seed),'--no-step-log','true','--duration-log.disable','true']
    subprocess.run(command,cwd=out,check=True)
    completed,unfinished=summarize(out/'tripinfo.xml',out/'demora_base.csv',prueba)
    expected=sum(r['cantidad'] for r in rows)
    status={'prueba':prueba,'geometria':'SINTETICA' if a.demo else 'SUMINISTRADA_NO_VALIDADA','semilla':a.seed,
      'esperados':expected,'completados':completed,'incompletos':unfinished,'criterio':'timeLoss promedio por acceso, sin incluir departDelay',
      'version_sumo':subprocess.check_output([binary('sumo'),'--version'],text=True).splitlines()[0],
      'fuente_conteos':str(a.counts),'comando':command,'validacion_piloto_real':False}
    (out/'ejecucion.json').write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding='utf-8')
    if unfinished or completed!=expected:raise SystemExit('CORRIDA INCOMPLETA: revisar vehículos no completados antes de interpretar demora')
    print('Corrida terminada. Ver demora_base.csv y ejecucion.json. Esto no valida el piloto real.')
if __name__=='__main__':main()
