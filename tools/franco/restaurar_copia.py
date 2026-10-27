"""Restaura únicamente en una BD nueva cysa_restore_*; nunca sobrescribe cysa."""
import argparse,re,subprocess
from pathlib import Path
from respaldo import compose

def main():
    p=argparse.ArgumentParser();p.add_argument('--file',type=Path,required=True);p.add_argument('--database',required=True);a=p.parse_args()
    if not re.fullmatch(r'cysa_restore_[a-z0-9_]{1,32}',a.database):p.error('Nombre permitido: cysa_restore_<identificador>; cysa está prohibida')
    if not a.file.is_file():p.error('No se encontró respaldo')
    root=Path(__file__).resolve().parents[2];base=compose(root)+['exec','-T','db']
    # createdb falla si ya existe. No se borra ni se vacía ninguna BD.
    subprocess.run(base+['createdb','-U','cysa',a.database],check=True)
    subprocess.run(base+['psql','-v','ON_ERROR_STOP=1','-U','cysa','-d',a.database,'-c','CREATE EXTENSION IF NOT EXISTS timescaledb; SELECT timescaledb_pre_restore();'],check=True)
    with a.file.open('rb') as f:subprocess.run(base+['pg_restore','-U','cysa','--no-owner','--exit-on-error','-d',a.database],stdin=f,check=True)
    subprocess.run(base+['psql','-v','ON_ERROR_STOP=1','-U','cysa','-d',a.database,'-c','SELECT timescaledb_post_restore(); SELECT count(*) FROM conteos;'],check=True)
    print('Restaurada en BD nueva de verificación. La aplicación sigue usando cysa. Revisar conteos/inventario antes de darla por validada.')
if __name__=='__main__':main()
