"""Ejecutar dentro del contenedor api: comprueba schema, no descarga imágenes ni datos personales."""
import json
from app.repository import Repository

def inspect(repo):
    with repo.connection() as c:
        columns=c.execute("SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('conteos','estados','inventario') ORDER BY table_name,ordinal_position").fetchall()
        hypertables=c.execute("SELECT hypertable_name FROM timescaledb_information.hypertables WHERE hypertable_name='conteos'").fetchall()
        duplicates=c.execute('SELECT count(*) AS n FROM (SELECT mensaje_id,inicio FROM conteos GROUP BY mensaje_id,inicio HAVING count(*)>1) d').fetchone()['n']
        forbidden=[r for r in columns if any(x in r['column_name'].lower() for x in ['imagen','video','placa','image','frame'])]
        return {'columnas':columns,'hypertable_conteos':bool(hypertables),'grupos_duplicados':duplicates,'columnas_prohibidas':forbidden,
          'nota':'Solo inspección de esquema y duplicados; no demuestra ausencia de archivos fuera de la base.'}
if __name__=='__main__':
    result=inspect(Repository());print(json.dumps(result,indent=2,ensure_ascii=False))
    if not result['hypertable_conteos'] or result['grupos_duplicados'] or result['columnas_prohibidas']:raise SystemExit(1)
