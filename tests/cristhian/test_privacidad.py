from comprobar_privacidad import scan

def test_scanner_detecta_multimedia_sin_borrar(tmp_path):
    (tmp_path/'conteos.csv').write_text('cantidad\n3\n')
    assert scan([tmp_path])==[]
    (tmp_path/'captura.jpg').write_bytes(b'SINTETICO_NO_ES_IMAGEN_REAL')
    assert scan([tmp_path])==['captura.jpg']
    assert (tmp_path/'captura.jpg').exists()
