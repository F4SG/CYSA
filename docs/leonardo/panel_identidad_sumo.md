# Panel, identidad y simulación
## Identidad
El realm template no incluye usuarios ni contraseñas. `preparar_local.py` de Franco genera usuarios locales operador y
administrador y sus contraseñas aleatorias dentro de infra/runtime. Las funciones técnicas de los integrantes no son roles del sistema.
El cliente cysa-panel es público, sin secret, con Authorization Code + PKCE S256 y audience mapper cysa-api.
El panel conserva tokens solo en memoria y el verificador/estado/nonce temporal en sessionStorage hasta consumir el callback.
La API verifica firma RS256, issuer, audience, expiración y roles; las pruebas usan claves RSA sintéticas, no Keycloak real.
La información de usuario decodificada en el panel sirve para mostrar identidad, no para conceder permisos de API.
El logout usa RP-Initiated Logout de Keycloak. La sesión del navegador debe probarse con el contenedor real.

## Panel
Tres vistas: conteos, inventario y estado de comunicación. Buscador y filtros de tiempo local convertidos a UTC.
Se muestran intervalos originales con paginación; PRUEBA identifica todo registro sintético.
No se confunden ausencia de datos y conteo cero. Estado >30 s se marca desactualizado, sin activar lógica del controlador.
El panel realiza consultas cada 15 s; el envío de estados de prueba nominal es cada 30 s. La latencia real está pendiente de medir.
No incluye simulación desde navegador, envío de planes, botones de verdes, MFA ni autorización.
Servir con Nginx del Compose; no abrir index.html con file:// por OIDC y módulos JS.

## SUMO reproducible
Dependencias fijadas: eclipse-sumo, sumolib y sumo-data 1.27.0. Instalar paquetes o binarios oficiales y comprobar
`sumo --version` y `netconvert --version`. Si no están en PATH, establecer SUMO_HOME a la instalación oficial.
`sumo_base.py --demo` genera una cruz de cuatro accesos con movimientos rectos, flujos sintéticos y plan fijo DEMO.
Esta geometría no reproduce Santa Cruz ni un piloto real; no acredita tiempos peatonales ni prioridades.
La asignación de fases se deriva de los linkIndex finales de netconvert para mantener accesos opuestos juntos.
Semilla 42, sigma 0 y speedFactor 1. No se modifican planes durante la corrida.
`--network red.net.xml --access-map accesos_red.csv` permite reutilizar una red suministrada con su plan fijo ya incorporado.
El mapa relaciona acceso con edge de entrada/salida; el método admite rutas rectas de dos edges contiguos.
Para redes con rutas más largas, preparar rutas/adaptación antes de usarlas: no inventarlas.
No usar flujos con intervalos superpuestos del mismo carril/clase. El script acepta una intersección por corrida.
La cantidad de cada intervalo se usa como número de vehículos durante ese intervalo, conservando su duración;
no se multiplica ciegamente a una hora ni se presenta la demanda provisional como conteo real.

Salidas: red.net.xml, flujos.rou.xml, base.sumocfg, tripinfo.xml, demora_base.csv y ejecucion.json.
Demora = media de timeLoss de vehículos completados por acceso de origen; departDelay se informa en tripinfo,
pero no se suma a esta métrica. Registrar esa elección al comparar Webster en S2.
No se permite teleport para ocultar congestión. Se escribe tripinfo de incompletos y se falla si no terminan todos los esperados.
La corrida termina tras última demanda +900 s; si el corredor requiere más tiempo, adaptar horizonte con justificación.
Antes de afirmar reproducibilidad real: verificar geometría, accesos, plan vigente, demanda y cobertura del inventario.
