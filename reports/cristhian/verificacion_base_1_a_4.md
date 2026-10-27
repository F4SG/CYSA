# Verificación realizada y límites

Alcance preparado: iteraciones 1–4 del Sprint 1, 26/10–02/11/2026. La fecha de preparación no acredita ejecución de reuniones futuras ni cumplimiento de hitos.

## Ejecutado con datos sintéticos
- 30 pruebas automatizadas PASSED: rechazo de mensajes inválidos y campos extras, tópico/cuerpo coincidente, deduplicación en repositorio de prueba, consulta por API y estados no regresivos.
- Firma RSA de JWT, issuer/audience/expiración, falta de login, rol incorrecto y escritura de inventario solo administrador; alta/edición y errores de inventario.
- Cruce de línea una sola vez por track/carril, continuidad entre intervalos, sentido/segmento finito y umbrales de calibración (incluido manual cero).
- Lectura/resumen de tripinfo y rechazo de demanda duplicada.
- API probada con FastAPI TestClient y repositorio en memoria. La resolución JWKS se sustituyó por clave RSA de prueba: NO es una conexión con Keycloak real.
- SUMO oficial 1.27.0 ejecutó red DEMO, plan fijo sintético y 13 vehículos: todos completados; CSV de timeLoss por acceso. La red usa linkIndex finales para asignar accesos opuestos.
- Se ensamblan los tres paquetes en una carpeta de prueba sin colisión de archivos; esto comprueba compatibilidad de interfaces, no la integración formal a S0.

Aviso no bloqueante observado en la suite: Starlette depreca el uso de httpx en TestClient y sugiere httpx2. Los 30 casos pasan con la versión de httpx fijada. Revisar al actualizar dependencias.

## No validado con recursos reales
- Docker/Compose no disponible: no se arrancaron Mosquitto, TimescaleDB, Nginx ni Keycloak; sus imágenes, migraciones, red/ACL/TLS y generación de usuarios requieren prueba en la PC del equipo.
- No hubo acceso a webcam, GPU ni escenas vehiculares: detector/Ultralytics y rendimiento no ejecutados, calibración real pendiente.
- No se ejecutó login de navegador ni revisión visual del panel. Sintaxis de módulos y estructura estática se verifican por separado.
- Inventario, geometría y plan fijo reales no proporcionados. Red, activos y demanda DEMO se identifican como sintéticos.
- No existen aprobaciones del equipo/docente ni mediciones de precisión, búsqueda <1 min o actualización ≤30 s en el piloto.
- No se ejecutaron actividades formales de iteraciones 5–8 ni se aprueba ningún requisito del sprint por estas pruebas.

## Implementación preparada, sin afirmar pruebas en vivo
API/repo SQL, consumidor MQTT, TLS/ACL/Compose, plantillas/CA, detector, inventario, login/panel, escenario SUMO, exportación y reglas borrador.
El generador de certificados y realm se ejecutó en un directorio temporal con llamadas Docker sustituidas: se verificó la firma de CA y los SAN del certificado, separación de CA privada y credenciales aleatorias. El hash de Mosquitto y el contenedor real permanecen sin probar.
Mosquitto sin persistencia y reconexión de laboratorio no garantizan entrega ante caída abrupta de procesos; ensayar pérdida/reenvío del CSV y endurecer antes de producción.
