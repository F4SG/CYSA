# Contratos CYSA S1, versión 1.0
Alcance de preparación: iteraciones 1–4 (26/10–02/11/2026). Autor responsable: Franco.

## MQTT
- TLS 1.2 o superior, listener 8883, QoS 1, retain=false. Sin listener 1883.
- Conteo: `corredor/<interseccion>/<acceso>/conteos`.
- Estado: `corredor/<interseccion>/estado`.
- Clases exactas: `auto`, `micro`, `moto`.
- Identificadores ASCII `[A-Za-z0-9_-]{1,64}`, sin espacios ni `/`.
- Todos los mensajes incluyen `version`, `mensaje_id` UUID y `prueba` booleano estricto.
- Conteo: `interseccion`, `acceso`, `carril`, `clase`, `cantidad` entero no negativo, `inicio`, `fin`.
- Ventanas nominales de 30 s, límite de 30.5 s por tolerancia de captura; no son conteos acumulados.
- Estado: `interseccion`, `fase_actual`, `plan_activo`, `estado_controlador` (`conectado`, `desconectado`, `desconocido`), `timestamp`.
- Fechas RFC3339/ISO8601 con zona obligatoria, normalizadas a UTC. Presentación local solo en panel.
- El tópico debe coincidir con intersección/acceso del cuerpo. Campos adicionales se rechazan, incluidos imagen/video/placa.
- Datos sintéticos: `prueba=true`, IDs con prefijo DEMO. No cambiar `prueba` a false para aparentar una medición real.
- `mensaje_id` se conserva al reintentar el mismo evento. La clave `(mensaje_id,inicio)` evita duplicados QoS1 en conteos.
  No protege contra un publicador que cambia el UUID o el intervalo al reintentar; esa conducta viola el contrato.
- El consumidor confirma mensajes QoS1 después de persistir. Mensajes inválidos se descartan con log sin payload.
- El último estado solo se reemplaza por uno con timestamp posterior. El intervalo nominal es 30 s.

## API, base `/api`
Todas las consultas requieren Bearer JWT RS256 firmado por Keycloak, con exp/iat/sub/iss/aud.
`iss=http://localhost:8080/realms/cysa`, `aud=cysa-api` en el entorno local. Operador y administrador pueden leer.

| Método/ruta | Entrada | Respuesta |
|---|---|---|
| GET /conteos | desde/hasta ISO8601; interseccion, carril, prueba opcionales; limit 1..1000; offset >=0 | items, limit, offset, desde, hasta |
| GET /estados | — | items: último estado por intersección |
| GET /inventario | — | items: activos |
| POST /inventario/carga | `{items:[Activo,...]}`, máximo 2000 | procesados |
| PUT /inventario/{activo_id} | Activo completo, mismo ID de ruta | Activo actualizado |

Los dos últimos métodos exigen administrador; el operador recibe 403. Token ausente/inválido: 401.
Keycloak no disponible al obtener clave: 503. `/health` es público y solo informa estado del proceso;
no sustituye una prueba de base de datos, broker ni flujo integrado.
Conteos: por defecto última hora; rango `[desde,hasta)` por **inicio** del intervalo, hasta 31 días.
La API devuelve cada intervalo/carril/clase, no reparte automáticamente un intervalo que cruce una hora.
Para una hora completa consultar sus límites UTC y sumar las cantidades por carril/clase/origen.
El panel pagina de a 200. Datos faltantes se muestran como ausencia, nunca como cero inventado.

Activo: `activo_id`, `interseccion`, `acceso` opcional, `tipo` (interseccion/acceso/camara/controlador),
`ubicacion`, `protocolo`, `prueba`. Carga por upsert de activo_id; IDs duplicados en una carga se rechazan.
La edición reemplaza un activo existente; no crea si el ID no existe. CSV vacío es plantilla, no inventario completo.

## Planes: contrato reservado
`PlanBorrador`: version, plan_id, interseccion, fases [{fase_id,duracion_s}], prueba.
Es un esquema preliminar para coordinar S2: NO es un plan validado, no define autorización ni MFA.
No se habilita tópico de órdenes, endpoint de activación ni implementación de envío de planes en S1.
El controlador abstracto y su envío se mantienen sin adaptador concreto.

Los JSON Schema exportados y ejemplos están en `data/franco/contratos` y `data/franco/ejemplos` tras ensamblar.
