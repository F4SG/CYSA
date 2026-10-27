import argparse,json,zipfile
from pathlib import Path,PurePosixPath

def assemble(zips,destination):
    destination=Path(destination).resolve()
    if destination.exists() and any(destination.iterdir()):raise ValueError('La salida debe ser nueva o vacía; no se sobrescribe S0')
    files={};owners=set()
    for zip_path in zips:
        with zipfile.ZipFile(zip_path) as z:
            manifests=[n for n in z.namelist() if n.count('/')==1 and n.endswith('/manifiesto.json')]
            if len(manifests)!=1:raise ValueError('ZIP sin manifiesto único')
            prefix=manifests[0].split('/')[0]+'/'
            manifest=json.loads(z.read(manifests[0]));owner=manifest['integrante']
            if manifest.get('release')!='s1-it1a8-v1' or manifest.get('iteraciones')!=list(range(1,9)):
                raise ValueError('Se requieren tres paquetes acumulativos 1 a 8 de la misma release')
            if owner in owners:raise ValueError('Paquete duplicado')
            owners.add(owner)
            for source,target in manifest['mapa'].items():
                # Las rutas se tratan como POSIX y se verifican de nuevo bajo el destino absoluto.
                for entry in z.infolist():
                    rel=entry.filename.removeprefix(prefix)
                    if entry.is_dir() or not entry.filename.startswith(prefix):continue
                    if rel==source:suffix=''
                    elif rel.startswith(source.rstrip('/')+'/'):suffix=rel[len(source.rstrip('/'))+1:]
                    else:continue
                    dest=PurePosixPath(target)/suffix if suffix else PurePosixPath(target)
                    if dest.is_absolute() or '..' in dest.parts or '\\' in str(dest) or ':' in str(dest):raise ValueError('Ruta insegura')
                    resolved=(destination/str(dest)).resolve()
                    if not resolved.is_relative_to(destination):raise ValueError('Ruta fuera del destino')
                    if str(dest) in files:raise ValueError('Colisión de archivos: '+str(dest))
                    files[str(dest)]=z.read(entry)
    if owners!={'Franco','Cristhian','Leonardo'}:raise ValueError('Se requieren los tres ZIP')
    destination.mkdir(parents=True,exist_ok=True)
    for rel,content in files.items():
        p=destination/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
    print(f'Ensamblados {len(files)} archivos en {destination}. No se ejecutaron servicios ni se integró S0.')
    return len(files)
def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);p.add_argument('zips',nargs=3,type=Path);a=p.parse_args()
    assemble(a.zips,a.salida)
if __name__=='__main__':main()
