# Red y seguridad de la base preparada
- `operacional` es una red Docker interna: db, broker, consumidor y API. El panel no se conecta a ella.
- `panel`: panel Nginx, Keycloak y API. La API es el enlace explícito entre ambas redes.
- PostgreSQL no publica puertos. FastAPI no publica puertos al host: se accede por `/api` en Nginx.
- Broker publica únicamente 127.0.0.1:8883, con TLS, usuarios separados y ACL; sin 1883.
- Keycloak 127.0.0.1:8080 y panel 127.0.0.1:8088 son para pruebas locales. Keycloak usa start-dev y H2 persistente:
  esta base sirve al laboratorio S1, no es un despliegue productivo de identidad.
- Puertos en loopback permiten el ensayo desde una sola PC. Para la webcam en otra PC, editar deliberadamente
  el binding del broker al IP de la LAN de laboratorio, limitar firewall por IP de Cristhian y regenerar certificado
  con `--broker-dns`/`--broker-ip` antes del primer arranque. No abrir un listener sin TLS.
- `internal: true` no es una VLAN física. Propuesta de campo: una VLAN operacional por gabinete, enrutamiento
  permitido solo desde detección/controlador a broker TLS y administración autorizada; panel en red separada.
  Números VLAN, subredes, gateway y reglas reales siguen pendientes del corredor y responsable técnico.
- Broker ACL: deteccion escribe conteos; plataforma lee conteos/estados; prueba escribe solo DEMO_INT_01;
  emulador escribe estados (credencial reservada, sin adaptador S1).
- CA propia, certificado con SAN (mosquitto, localhost e IP configurada), verificación de nombre activada.
  `preparar_local.py` usa cryptography para generar X.509 de forma portátil; no necesita OpenSSL instalado.
  El resultado equivale a CA/certificados PEM que OpenSSL puede inspeccionar; no implementa una PKI de producción.
- CA privada fuera del montaje del broker. Contraseñas, claves y usuarios de prueba se generan en runtime y .env,
  nunca en los ZIP. El script no sobrescribe configuración existente. Revisar ACL de archivos en Windows.
- Mosquitto passwords se convierte con `mosquitto_passwd -U` dentro de su imagen. No se pasan secretos en argumentos.
- El panel usa Authorization Code + PKCE S256. Tokens solo en memoria, comprobación de firma y permisos en API.
  Roles: lectura para operador/administrador, carga/edición de inventario solo administrador.
- HTTP del panel/Keycloak solo en loopback para laboratorio; si se publica fuera del host, definir HTTPS, ajustar
  issuer, redirectUri, webOrigins, post.logout.redirect.uris y CSP. Los valores de LAN no se adivinan.
- La autorización de planes está ausente. MFA y trazabilidad crítica corresponden a S2/S3.

## Prueba pendiente con servicios reales
1. Generar configuración, arrancar Compose y comprobar logs sin mensajes de error.
2. Usar credencial prueba y ejecutar `verificar_tls.py`: plano rechazado y TLS autenticado con PUBACK.
3. Confirmar por API que el estado DEMO llegó al almacenamiento. PUBACK solo prueba aceptación del broker.
4. Capturar red y revisar puertos/listeners para confirmar 100 % MQTT cifrado.
5. Confirmar aislamiento desde el contenedor del panel y acceso autorizado de la webcam al listener TLS.
No se afirma haber realizado estas pruebas de Docker/Mosquitto en el entorno autor.
