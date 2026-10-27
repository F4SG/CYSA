"""Ejercita certificados/realm locales con Docker sustituido; no prueba Mosquitto."""
import json,shutil,sys,subprocess
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives.asymmetric import padding
import pytest
import preparar_local

def test_secretos_certificados_y_realm_generados_solo_en_runtime(tmp_path,monkeypatch):
    source=Path(__file__).resolve().parents[2]
    (tmp_path/'identidad').mkdir();(tmp_path/'panel').mkdir();(tmp_path/'infra').mkdir()
    shutil.copyfile(source/'identidad/realm.template.json',tmp_path/'identidad/realm.template.json')
    calls=[]
    def fake_docker(command,**kwargs):
        calls.append(command)
        if 'run' in command:
            # No se comprueba el hash de Mosquitto: el conversor real requiere su contenedor.
            p=tmp_path/'infra/runtime/mqtt/passwords'
            p.write_text('deteccion:HASH_SUSTITUTO_DE_PRUEBA\n')
        return subprocess.CompletedProcess(command,0)
    monkeypatch.setattr(preparar_local.subprocess,'run',fake_docker)
    monkeypatch.setattr(sys,'argv',['preparar_local.py','--repo',str(tmp_path)])
    preparar_local.main()
    runtime=tmp_path/'infra/runtime'
    ca=x509.load_pem_x509_certificate((runtime/'mqtt/ca.crt').read_bytes())
    server=x509.load_pem_x509_certificate((runtime/'mqtt/server.crt').read_bytes())
    ca.public_key().verify(server.signature,server.tbs_certificate_bytes,padding.PKCS1v15(),server.signature_hash_algorithm)
    sans=server.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
    assert 'mosquitto' in sans.get_values_for_type(x509.DNSName)
    assert (runtime/'ca-private/ca.key').exists() and not (runtime/'mqtt/ca.key').exists()
    realm=json.loads((runtime/'keycloak/cysa-realm.json').read_text())
    assert {u['username'] for u in realm['users']}=={'operador','administrador'}
    assert all(len(u['credentials'][0]['value'])>=32 for u in realm['users'])
    assert 'MQTT_PLATAFORMA_PASSWORD=' in (tmp_path/'infra/.env').read_text()
    assert all('HASH_SUSTITUTO' not in str(command) for command in calls)
    with pytest.raises(SystemExit):preparar_local.main()
