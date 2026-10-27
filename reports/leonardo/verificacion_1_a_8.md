# Verificación de la release s1-it1a8-v1

## Ejecutado al preparar los paquetes
34 pruebas automatizadas correctas. Se reutiliza la base 1 a 4 y se agregan verificación de nonce/firma del login CLI, límites de estado, rechazo de ZIP de otra release y escáner de archivos multimedia. API con TestClient y repositorio en memoria, JWKS/claves sintéticas y Docker sustituido en preparación de certificados: estas pruebas NO prueban los servicios reales.

Se ejecutó SUMO oficial 1.27.0 por CLI, semilla 42, red DEMO, 13 vehículos esperados y completados. La corrida se repite con scripts de esta release y conserva salidas sintéticas.

## Herramientas nuevas preparadas
Login de navegador PKCE para CLI sin tokens guardados, diagnóstico, ejecutor de aceptación en servicios locales, inspección SQL, escáner de privacidad, respaldo binario y recuperación a BD nueva. El ejecutor de aceptación NO fue corrido contra servicios reales en el entorno autor por ausencia de Docker. Están listos para que Franco lo ejecute siguiendo la guía.

## Pendientes
Docker/Compose, Mosquitto/TLS/ACL/red, TimescaleDB/migraciones, Nginx, Keycloak/login/refresh/logout, panel visual y búsqueda <1 min. Cámara/GPU/escenas, precisión ≤10 %, inventario/geometría/plan reales y aprobación docente. No se inventa ningún resultado real ni aprobación.

## Alcance de las iteraciones
Las ocho iteraciones tienen materiales e instrucciones preparados. La integración formal a S0, ensayo real, aceptación y entrega del 3–6/11 son actividades planificadas, no hechos acreditados. Las pruebas sintéticas locales de compatibilidad de archivos no equivalen a la aceptación del sprint.

La suite muestra un aviso de deprecación no bloqueante por httpx en TestClient; no hubo fallos. Ver el informe histórico de base para detalles de los módulos originales. Los ZIP no incluyen secretos, pesos, videos ni dependencias binarias.
