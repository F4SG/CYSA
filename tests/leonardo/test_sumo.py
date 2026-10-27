from pathlib import Path
from sumo_base import load_counts,summarize
import pytest

def test_tripinfo_separa_accesos_e_incompletos(tmp_path):
    f=tmp_path/'tripinfo.xml';f.write_text('<tripinfos><tripinfo id="N__1.0" timeLoss="10" arrival="50"/><tripinfo id="N__2.0" timeLoss="20" arrival="60"/><tripinfo id="E__3.0" timeLoss="5" arrival="-1"/></tripinfos>')
    count,unfinished=summarize(f,tmp_path/'out.csv',True)
    assert count==2 and unfinished==1
    assert '15.000000' in (tmp_path/'out.csv').read_text()
def test_flujos_duplicados_se_rechazan(tmp_path):
    text='interseccion,acceso,carril,clase,cantidad,inicio,fin,prueba\n'
    row='DEMO_INT_01,N,N_0,auto,3,2026-10-26T12:00:00Z,2026-10-26T12:00:30Z,true\n'
    f=tmp_path/'counts.csv';f.write_text(text+row+row)
    with pytest.raises(ValueError):load_counts(f)
