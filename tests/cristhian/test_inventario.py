from cysa_inventory.router import Carga
ASSET={'activo_id':'DEMO_CAM_01','interseccion':'DEMO_INT_01','acceso':'N','tipo':'camara','ubicacion':'SINTETICA','protocolo':'USB','prueba':True}
def test_lectura_operador_y_bloqueo_escritura(operator):
    assert operator.get('/api/inventario').status_code==200
    assert operator.post('/api/inventario/carga',json={'items':[ASSET]}).status_code==403
def test_carga_edicion_y_validaciones(admin):
    assert admin.post('/api/inventario/carga',json={'items':[ASSET]}).json()['procesados']==1
    assert len(admin.get('/api/inventario').json()['items'])==1
    assert admin.post('/api/inventario/carga',json={'items':[ASSET,ASSET]}).status_code==422
    assert admin.put('/api/inventario/OTRO',json=ASSET).status_code==422
    assert admin.put('/api/inventario/DEMO_CAM_01',json={**ASSET,'protocolo':'RTSP'}).status_code==200
    assert admin.put('/api/inventario/INEXISTENTE',json={**ASSET,'activo_id':'INEXISTENTE'}).status_code==404
    assert admin.post('/api/inventario/carga',json={'items':[{**ASSET,'imagen':'invalida'}]}).status_code==422
