# Detección y privacidad
## Fuente y preparación
Solo Cristhian dispone de webcam. `source: 0` la selecciona; URL de cámara IP o ruta externa autorizada se configuran en YAML.
La webcam es provisional y no equivale a la cámara IP del inventario del piloto. Confirmar escena vehicular y equipo con GPU.
`configuracion_verificada: false` impide ejecutar líneas inventadas por accidente. Copiar la plantilla, completar
intersección y cada línea/carril, comprobar el sentido de cruce y luego establecer true.
Las coordenadas de línea son normalizadas a [0,1], origen en esquina superior izquierda. Se usa el punto inferior central
sacado del bounding box. El signo se calcula respecto al segmento dirigido a→b; probar `negative_to_positive` o el opuesto.
No hay captura de imagen para calibrar líneas; se puede observar una vista en vivo externa autorizada sin grabarla.

## Modelo y conteo
YOLO26 preentrenado (`yolo26n.pt`), Ultralytics fijado en requirements. No entrenamiento.
Los pesos se obtienen de Ultralytics al primer uso o se preaprovisionan antes de entrar al corredor sin Internet.
COCO: car=2→auto, motorcycle=3→moto, bus=5→micro como aproximación. Un bus detectado no garantiza que sea
un micro local; los micros que el modelo confunda con otra clase requieren medición y documentar limitaciones.
No se cuenta truck como auto por defecto. No se infiere emergencia.
ByteTrack persistente conserva IDs. Se cuenta solo cruce de segmento finito en sentido configurado,
una vez por ID y línea; el registro de cruces no se reinicia al publicar cada intervalo. IDs ausentes >120 s se purgan.
Cambios de ID, oclusiones y líneas superpuestas pueden causar errores: la validación manual es obligatoria.
CPU está configurada únicamente como opción de arranque; `device: 0` solicita GPU cuando esté disponible.
Si una inferencia provoca una ventana >30.5 s, el detector se detiene para no enviar un intervalo fuera del contrato.

## Datos producidos
Cada intervalo emite auto/micro/moto por cada carril configurado, incluidos ceros de intervalos observados.
Al EOF emite solo el tramo observado, no un intervalo completo ficticio. Si se interrumpe con Ctrl+C el último tramo
puede no publicarse; excluir ventanas incompletas de la calibración. Reinicios del proceso reinician IDs del tracker.
CSV agregado conserva UUID para recuperar publicaciones fallidas sin fabricar IDs nuevos. El archivo puede tener
conteos pendientes de enviar si el broker falla: revisar y reintentar con el mismo evento, sin contarlos dos veces.
No se persiste una cola de cuadros. Un archivo de video se procesa en su tiempo de ejecución, no como reloj de tráfico
original; para inferir tasas reales usar captura en vivo o acordar un reproductor a velocidad original y documentar ventanas.
El detector por defecto usa reloj de pared UTC; no mezclarlo con timestamps del archivo sin sincronización explícita.

## Privacidad
Se leen cuadros en RAM y se descartan. model.track se llama con save/save_txt/save_crop/save_frames/show=false.
No se invocan VideoWriter, imwrite ni guardado de recortes. El tracker puede retener estado temporal en RAM mientras corre.
Solo CSV con números/identificadores y mensajes agregados salen del detector. No registrar URLs con credenciales ni cuadros.
Inventario, mensajes y SQL no contienen columnas de imagen, video o placa; contratos rechazan campos desconocidos.
Revisión de código no demuestra por sí sola ausencia de archivos: inspeccionar filesystem, logs, MQTT y BD al ejecutar.
Una captura para evidencia debe mostrar datos numéricos o tablas, nunca el cuadro de cámara.
