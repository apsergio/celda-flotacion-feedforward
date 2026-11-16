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

El ZIP se extrajo en una carpeta independiente con espacios en su nombre. Se creó allí un segundo entorno virtual y se instalaron únicamente las dependencias de requirements.txt. La instalación terminó correctamente y pip check no encontró incompatibilidades. La batería completa aprobó: **85 pruebas en 57.63 s**, registradas en junit-zip-final.xml.

Streamlit arrancó desde esa copia, usando el segundo entorno. Una conexión local HTTP/WebSocket recorrió los **12 módulos sin excepciones**; evidencia: zip_access_final.json. validate.py terminó correctamente, con residuo máximo de conservación de aproximadamente 1.82 × 10⁻¹² L en el protocolo de Figura 14. El intento de pruebas iniciado antes de finalizar pip falló por una instalación todavía incompleta; se descartó y se repitió después de terminar la instalación.

Al cerrar los informes se regenera la distribución y se compara por SHA-256 cada archivo Python, dependencia, configuración y dato con la copia probada. Solo se incorporan documentos y evidencias del cierre; no se cambia el código probado.

## Acceso público

Prueba de navegador en incógnito: **no realizada**. El sistema de control de Chrome se detuvo por no poder identificar la URL con suficiente confianza. Se conserva esta limitación aunque exista autorización del usuario.

La URL pública respondió HTTP 200 y se recorrieron sus **12 módulos sin excepciones** mediante una conexión nueva HTTP/WebSocket, sin credenciales ni cookies iniciales. Se observó el identificador «Entrega final auditada · 2026-11-16». Evidencia: public_access_final.json. No se equipara esa comprobación técnica con una inspección visual en incógnito. La aplicación entrega el código auditado; la configuración administrativa de Streamlit no se volvió a inspeccionar mediante navegador durante este cierre.

## Tabla de verificación

| Verificación | Resultado |
|---|---|
| Imports y módulos | Correctos; archivos requeridos incluidos |
| Instalación limpia | Dos entornos independientes, instalación completada y pip check correcto |
| Pruebas automatizadas | 85 aprobadas en cada entorno: 65.00 s y 57.63 s |
| Ejecución desde ZIP | Arranque correcto y 12 módulos sin excepciones |
| Exportación CSV | Banco y diez instrumentos verificados por ida y vuelta |
| Repositorio actualizado | Rama main; informes finales y fuente incluidos |
| Despliegue Streamlit | HTTP 200, identificador final y 12 módulos sin excepciones |
| Acceso público incógnito | Navegador no comprobado por bloqueo del control; acceso técnico anónimo comprobado |

## Alcance científico

Se conservan los modelos, calibraciones, identificación, SIMC, PI/FF, IAE, filtrado, comparación y exportación. Parámetros publicados, digitalización aproximada y datos sintéticos siguen diferenciados. No se dispone de series originales para declarar validación experimental exacta. Véanse docs/METODOLOGIA.md, docs/DICTAMEN_REPLICACION.md y docs/AUDITORIA_FINAL.md.
