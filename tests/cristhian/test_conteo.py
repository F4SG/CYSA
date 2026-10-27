from cysa_detector.counter import Lane,LineCounter
from calibrar import evaluate
import pytest

def lane():return Lane('N','N_0',(0.1,0.5),(0.4,0.5),'negative_to_positive')
def test_cruce_una_vez_y_no_se_repite_entre_intervalos():
    c=LineCounter([lane()]);c.observe(7,'auto',(0.2,0.3),0);c.observe(7,'auto',(0.2,0.7),1)
    assert c.snapshot()=={('N','N_0','auto'):1}
    c.reset_interval();c.observe(7,'auto',(0.2,0.3),2);c.observe(7,'auto',(0.2,0.7),3)
    assert not c.snapshot()
def test_no_cuenta_extension_de_linea_ni_direccion_opuesta():
    c=LineCounter([lane()]);c.observe(1,'moto',(0.8,0.2),0);c.observe(1,'moto',(0.8,0.8),1)
    c.observe(2,'auto',(0.2,0.8),0);c.observe(2,'auto',(0.2,0.2),1)
    assert not c.snapshot()
def test_carriles_clases_y_punto_en_linea():
    c=LineCounter([lane()]);c.observe(1,'micro',(0.2,0.2),0);c.observe(1,'micro',(0.2,0.5),1);c.observe(1,'micro',(0.2,0.8),2)
    assert c.snapshot()[('N','N_0','micro')]==1
    c.prune(200);assert not c.tracks

def row(manual,auto):return {'interseccion':'DEMO_INT_01','acceso':'N','carril':'N_0','clase':'auto','inicio':'2026-10-26T12:00:00Z','fin':'2026-10-26T12:00:30Z','manual':str(manual),'automatico':str(auto),'prueba':'true'}
@pytest.mark.parametrize('manual,auto,result',[(100,110,'CUMPLE'),(100,111,'NO_CUMPLE'),(0,2,'SIN_BASE_PORCENTUAL')])
def test_calibracion_limites(manual,auto,result):assert evaluate([row(manual,auto)])[0]['resultado']==result

def test_muestras_duplicadas_y_vacias():
    with pytest.raises(ValueError):evaluate([row(10,10),row(10,10)])
    with pytest.raises(ValueError):evaluate([])
