# Propuesta de reglas de simulación y autorización
Estado: BORRADOR, pendiente de revisión del equipo y aprobación docente.
Responsable de preparación: Leonardo. Alcance: iteraciones 1–4 de S1.

1. **Cuándo simular.** Se propone ejecutar SUMO desde la plataforma ante una propuesta de cambio de franja o de plan.
   La ejecución a pedido se limita a un comando de laboratorio del servidor para reproducir escenarios. El panel no ejecuta SUMO.
   Decisión a discutir el 30/10/2026 con Franco y Cristhian; no se registra esa reunión como realizada.
2. **Línea base.** En S1 se usa el plan fijo existente del piloto cuando esté disponible. La red DEMO sirve únicamente
   para probar el procedimiento. Guardar demanda, semilla, red, programa y timeLoss por acceso.
3. **Respuesta del operador.** Propuesta para S2: si no responde, conservar el último plan válido autorizado.
   No adoptar por defecto un plan recomendado ni interpretar silencio como aceptación. El tiempo máximo de espera
   sigue pendiente de acordar; no se inventa un timeout.
4. **Autorización.** Ningún plan nuevo se activa sin validación y autorización. En S1 no existe activación de planes.
   MFA y flujo efectivo de aprobación se implementan en S2, con cierre de pruebas en S3.
5. **Separación de responsabilidades.** Plataforma calcula/simula en etapas posteriores; operador revisa; administrador
   gestiona usuarios/configuraciones permitidas. No hay tercer rol ni control manual de luces desde el panel.
6. **Validación posterior.** Los umbrales de demora, peatones y prioridades del backlog se programan en S2.
   Este documento no demuestra su cumplimiento ni incluye esa implementación.

Registro de revisión: fecha ___; participantes ___; observaciones ___; decisión ___; evidencia ___.
Aprobación docente: fecha ___; nombre ___; decisión ___; evidencia ___.
Meta del sprint: revisión/aprobación antes del 06/11; hoy permanece pendiente.
