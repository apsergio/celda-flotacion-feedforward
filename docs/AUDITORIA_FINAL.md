# Auditoría final de integridad y ejecución

Fecha de auditoría: 16 de noviembre de 2026. Plataforma comprobada: Windows, Python 3.11.

## Alcance

Se revisaron código, dependencias, configuración, datos de referencia, documentos y resultados del proyecto existente. `ui_modules.py` es un archivo que contiene los módulos docentes; no depende de una carpeta externa del mismo nombre. Los archivos locales importados son model.py, methodology.py, presentation.py y ui_modules.py. Las funciones originales se mantienen.

La auditoría incluye inventario SHA-256 por archivo, parseo AST de Python, resolución de imports, lectura de documentos y CSV, sanitización de metadatos JUnit y exclusión de entornos, cachés, historial Git y archivos privados de la distribución.

## Correcciones de integridad

- Lectura de la documentación de app.py relativa al archivo de aplicación, no a una carpeta externa del equipo.
- Finalización de los temporizadores de reproducción al llegar al final del ensayo, para evitar redibujados indefinidos.
- Instrucciones de activación diferenciadas para CMD y PowerShell, con alternativa sin activación ni cambio de política de seguridad.
- Corrección del README: hay ruido opcional reproducible; las alternativas geométrica e identificada exponen una discrepancia, sin afirmar que la resuelvan físicamente.
- Regeneración de requirements-lock.txt desde el entorno limpio instalado únicamente con requirements.txt; sin dependencias de análisis PDF ajenas a la aplicación.
- Informes XML sin el nombre del equipo ni logs locales. ZIP de distribución sin bundle Git, credenciales, temporales ni rutas personales.

## Funciones conservadas y comprobaciones

| Sección | Evidencia de comprobación |
|---|---|
| Banco de tres celdas y tanque | Conservación, límites, equilibrio y respuesta perturbada |
| Cuatro bombas | Curvas y estadística por instrumento; CSV ida/vuelta |
| Tres sensores y tres FIC | Ajustes individuales, triplicados y navegación |
| Identificación y k′/θ | Recuperación analítica sin ruido y ensayo interactivo |
| SIMC | Ecuaciones, restricciones, tabla publicada y alternativas |
| Modelos independientes | Respuesta integradora y primer orden con sus límites |
| Instrumentación PLC | Extremos 4–20 mA, INT y cuantización |
| Feedback / Feedforward | PI por celda, compensación, comparación y IAE |
| Protocolo Fig.14 | Ensayo dedicado y métricas separados de datos publicados |
| Filtrado | Mediana causal, señales con ruido y tres IAE |
| Exportación | CSV conservando filas, números, Unicode y procedencia |

## Instalaciones limpias

El primer entorno virtual se creó fuera del proyecto y se instaló únicamente mediante `pip install -r requirements.txt`. `pip check` no encontró incompatibilidades. Las **85 pruebas** se ejecutaron de nuevo y aprobaron en **65.00 s**. No se reutiliza el resultado de las antiguas 72 pruebas como evidencia de esta auditoría.

La comprobación del ZIP utiliza otra carpeta independiente y un segundo entorno virtual creado después de extraerlo. Los resultados ejecutados de esa segunda instalación se registran en validation/INFORME_FINAL.md y sus archivos JUnit. El código de la distribución final se compara por SHA-256 con la copia probada.

## Acceso público e incógnito

La prueba de Chrome en modo incógnito no pudo realizarse: el sistema de control detuvo el acceso porque no pudo determinar con suficiente confianza la URL de la ventana. La autorización del usuario no elimina ese límite del entorno. **No se registra como aprobada una prueba de incógnito no ejecutada.**

Se realiza por separado una prueba de conexión nueva HTTP y WebSocket sin encabezado de autorización ni cookies iniciales. Esa prueba ejecuta la aplicación y sus módulos mediante su protocolo de cliente y permite comprobar acceso sin credenciales, pero no equivale a inspección visual en una ventana privada. Sus resultados y la versión observada se registran en el informe final.

## Límites científicos

Se preserva la distinción entre parámetros publicados, digitalización aproximada, datos sintéticos y datos propios. Las pruebas de software no demuestran equivalencia exacta con curvas experimentales de los autores. Las discrepancias del artículo, el almacenamiento efectivo del modelo identificado, las condiciones iniciales supuestas y la representación ideal de PLC permanecen documentados en METODOLOGIA.md y DICTAMEN_REPLICACION.md.
