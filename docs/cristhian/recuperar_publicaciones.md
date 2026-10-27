# Reenvío de conteos agregados
Si la publicación falla después de escribir el CSV, no reiniciar inventando nuevos UUID para esas filas.
Después de recuperar el broker y configurar PYTHONPATH, ejecutar:

```powershell
python tools/franco/cargar_env.py infra/runtime/clientes/deteccion.env -- python tools/cristhian/reenviar_conteos.py resultados/conteos.csv
```

El mismo CSV puede reenviarse completo porque la clave mensaje_id/inicio evita repetirlo en BD.
El archivo nunca contiene cuadros de cámara. Revisar intervalos, origen y errores del consumidor por API.
No se ha ensayado este reenvío con un broker real en el entorno autor.
