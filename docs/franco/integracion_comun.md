# Integración acumulativa en una sola PC

Leer primero Guia_Completa_Pruebas_PC_Franco.docx o PDF, entregada junto con los tres ZIP. Cubre instalación y las ocho iteraciones. La copia en Markdown está en docs/franco/guia_completa_pc_franco.md tras ensamblar.

Los ZIP 1 a 8 sustituyen a los anteriores y usan release s1-it1a8-v1. Extraer Franco y ejecutar su ensamblador con los tres ZIP hacia una carpeta nueva. El ensamblador rechaza releases mezcladas y no sobrescribe S0.

Crear venv de Python 3.12, instalar backend/requirements.txt, tests/requirements.txt y simulacion/requirements.txt. Ejecutar tools/franco/probar.py. La detección y PyTorch son opcionales hasta disponer de cámara/fuente autorizada.

Con Docker Desktop activo, generar configuración una sola vez con tools/franco/preparar_local.py --repo ., validar Compose y ejecutar el único infra/compose.yaml. No instalar servicios Docker también en Windows. Broker localhost:8883, panel localhost:8088 y Keycloak localhost:8080.

login_local.py obtiene tokens por navegador y los pasa solo al comando hijo. aceptacion_local.py permite prueba con administrador y pruebas de rol separadas. El ejecutor crea evidencia sintética y no aprueba precisión de cámara. Usar carpetas nuevas de salida en cada corrida.

No se recibió S0. Revisar módulos y migraciones antes de incorporarlos por ramas al repositorio existente; no borrar volúmenes para forzar initdb. Las aprobaciones y datos reales siguen pendientes si no se suministran.
