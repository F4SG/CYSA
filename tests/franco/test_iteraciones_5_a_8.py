from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
import json,zipfile
import pytest,jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from aceptacion_local import validate_updates
from login_local import validate_tokens
from ensamblar import assemble

def test_estados_limite_30s_y_muestras_minimas():
    start=datetime(2026,10,26,12,tzinfo=timezone.utc)
    samples=[{'timestamp':(start+timedelta(seconds=i)).isoformat(),'edad_s':1} for i in [0,25,50]]
    assert validate_updates(samples)['cumple']
    assert not validate_updates(samples[:2])['cumple']
    samples[-1]['edad_s']=30.01;assert not validate_updates(samples)['cumple']
    samples[-1].update(edad_s=1,timestamp=(start+timedelta(seconds=56)).isoformat());assert not validate_updates(samples)['cumple']

def test_login_cli_firma_y_nonce():
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048);now=datetime.now(timezone.utc)
    base={'iss':'https://id.example.invalid/realms/cysa','sub':'sintetico','iat':now,'exp':now+timedelta(minutes=5)}
    class Keys:
        def get_signing_key_from_jwt(self,token):return SimpleNamespace(key=key.public_key())
    tokens={'access_token':jwt.encode({**base,'aud':'cysa-api'},key,algorithm='RS256'),
      'id_token':jwt.encode({**base,'aud':'cysa-cli','nonce':'correcto'},key,algorithm='RS256')}
    assert validate_tokens(tokens,base['iss'],'correcto',Keys())['sub']=='sintetico'
    with pytest.raises(ValueError):validate_tokens(tokens,base['iss'],'incorrecto',Keys())

def test_no_mezclar_zip_antiguo(tmp_path):
    old=tmp_path/'old.zip'
    with zipfile.ZipFile(old,'w') as z:z.writestr('Franco/manifiesto.json',json.dumps({'integrante':'Franco','iteraciones':[1,2,3,4],'mapa':{}}))
    with pytest.raises(ValueError,match='acumulativos'):assemble([old],tmp_path/'repo')
    assert not (tmp_path/'repo').exists()
