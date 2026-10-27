# De la API a los flujos SUMO
Con el sistema activo y un token de lectura en CYSA_TOKEN, desde repo_s1:

```powershell
python simulacion/exportar_conteos.py --desde 2026-10-26T12:00:00Z --hasta 2026-10-26T13:00:00Z --interseccion DEMO_INT_01 --out resultados/flujos_api.csv
```

Las fechas y el ID anteriores son solo un ejemplo; sustituir por la ventana con datos. El exportador pagina hasta
agotar la consulta y conserva la marca prueba. Antes de simular, revisar que la consulta no mezcle fuentes reales
con ejemplos de la misma intersección/carril/intervalo y que no haya solapamientos.
Pasar ese CSV a sumo_base.py con la red y el mapa adecuados. La red DEMO exige prueba=true; los conteos reales
solo deben usarse en una red suministrada/documentada. El formato CSV coincide con el generado por detección
(sus campos extra UUID/version se admiten al leer demanda, sin enviarlos a SUMO).
