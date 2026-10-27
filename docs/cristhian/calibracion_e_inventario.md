# Calibración e inventario
## Protocolo de medición pendiente
1. Confirmar fuentes de S0-09 sin copiarlas al sistema; describir origen, autorización, fecha y cobertura de clases.
2. Fijar intersección/acceso/carril, línea de conteo y sentido. Hacer conteo manual independiente del detector.
3. Seleccionar las mismas ventanas y registrar auto, micro y moto en `calibracion.csv`; no usar números sintéticos
   como evidencia. `prueba=false` solo si la fila proviene de medición real identificada.
4. Copiar las cantidades automáticas del CSV agregado de esas mismas ventanas. Excluir intervalos parciales o no sincronizados.
5. Ejecutar `calibrar.py entrada.csv salida.csv`.
6. Error por muestra: abs(automático-manual)/manual*100. Si manual=0, registrar falsos positivos absolutos y
   resultado SIN_BASE_PORCENTUAL; no dividir por cero. Revisar cada clase y carril, no ocultar fallos con un promedio global.
7. La meta es ≤10 %. Acordar volumen representativo y criterio global con equipo/docente; el script no concede aprobación.

No se suministran resultados reales ni se afirma GPU, escena, webcam o clasificación verificada. La plantilla está vacía.

## Inventario
CSV con activo_id, interseccion, acceso, tipo, ubicacion, protocolo y prueba. Referenciar IDs estables de los contratos.
Cargar intersecciones/accesos y todos los dispositivos reales del piloto. Completar ubicación/protocolo, no adivinarlos.
`inventario_DEMO.csv` contiene únicamente activos sintéticos, incluido un controlador ficticio; no acredita hardware disponible.
`cargar_inventario.py --validar` valida sin servicios. Sin ese flag envía a la API con `CYSA_TOKEN` de administrador.
La API ofrece lectura a ambos roles y carga/edición solo al administrador. La edición exige un activo existente.
Comprobar cobertura 100 % contra el listado real del piloto cuando exista; ese denominador hoy está pendiente.
