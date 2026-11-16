# Informe de auditoría de entrega definitiva

Fecha: 16 de noviembre de 2026. Python 3.11.9 en Windows.

## Evidencia ejecutada en el proyecto

- Entorno virtual nuevo, sin reutilizar las bibliotecas del entorno de desarrollo.
- Instalación exclusivamente mediante `pip install -r requirements.txt`; dependencias transitivas resueltas por pip.
- `pip check`: sin dependencias rotas.
- Batería completa ejecutada de nuevo: **85 pruebas aprobadas en 65.00 s**. Incluye las 72 pruebas anteriores y 13 pruebas nuevas de integridad, exportación y finalización de reproducción.
- Imports reales de model, methodology, presentation y ui_modules: correctos. app.py se ejecuta mediante Streamlit AppTest.
- Auditoría de imports declarados y archivos requeridos: sin imports ausentes ni archivos requeridos faltantes.
- Exportación CSV: ida y vuelta verificada para el banco y los diez instrumentos, conservando valores, identificadores y procedencia.
- Informes JUnit sin nombre del equipo ni logs locales; no se detectaron rutas personales o credenciales en el inventario de distribución.

## Evidencia de la distribución

La instalación independiente desde el ZIP y los resultados de ejecución se añaden al cierre de la auditoría. No se presenta una ejecución anterior desde otro ZIP como evidencia de este archivo definitivo.

## Acceso público

Prueba de navegador en incógnito: **no realizada**. El sistema de control de Chrome se detuvo por no poder identificar la URL con suficiente confianza. Se conserva esta limitación aunque exista autorización del usuario.

Se ejecutan por separado conexiones nuevas HTTP y WebSocket sin credenciales o cookies iniciales. Los resultados de la versión final se registran al completar su publicación. No se equipara esa comprobación técnica con una inspección visual en incógnito.

## Alcance científico

Se conservan los modelos, calibraciones, identificación, SIMC, PI/FF, IAE, filtrado, comparación y exportación. Parámetros publicados, digitalización aproximada y datos sintéticos siguen diferenciados. No se dispone de series originales para declarar validación experimental exacta. Véanse docs/METODOLOGIA.md, docs/DICTAMEN_REPLICACION.md y docs/AUDITORIA_FINAL.md.
