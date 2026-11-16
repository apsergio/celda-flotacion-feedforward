# Informe metodológico y de validación · versión 2

Fecha: 16 de noviembre de 2026. Proyecto existente ampliado; Python 3.11, Streamlit, NumPy, SciPy, Pandas y Plotly. Versiones de la instalación utilizada en requirements-lock.txt.

## Estado de verificación

- **72 pruebas aprobadas en 42.82 s** en el proyecto de trabajo. Resultado legible por máquina: junit-v2.xml.
- Se ejecutaron las 15 pruebas originales: se conserva el comportamiento del banco sin ruido y con parámetros predeterminados.
- 36 pruebas de cálculos y correspondencia documental: regresiones, intervalos, triplicados, conversiones, unidades, k′/θ, SIMC, modelos independientes, mediana, IAE, ruido común y procedencia.
- 21 pruebas de interfaz: todos los módulos, calibraciones de sensores/aire, guardado y uso de ajustes, identificación, pausa/reinicio y conservación de parámetros publicados como opción predeterminada.
- Navegador local: carga de la navegación ampliada y calibración; importación real de un CSV sintético de 15 observaciones, cálculo de pendiente/R²/errores/estadística y descarga CSV verificados. Se inspeccionó el archivo descargado: contiene residuos e input_source=«Sintéticos de demostración». El ensayo no se presenta como medición original.

## Distinción entre tipos de pruebas

**Matemáticas:** se usan soluciones analíticas y datos de coeficientes conocidos, no solo salidas del propio código: conversión de litros/segundos, extremos 4/20 mA, cuantización, regresión, DE muestral, respuestas a escalón, recuperación exacta de k′/θ sin ruido e integral de error con resultado conocido. También se comprueba conservación y límites en ambas plantas y estrategias.

**Correspondencia con el artículo:** transcripciones de Tabla 2 y ecuaciones rotuladas de Figs.8,9,11 verificadas contra las páginas renderizadas; pruebas fijan esos valores y mantienen visible la discrepancia SIMC de celda 3. Se comprueba que la digitalización de Fig.12 contiene una sola curva visible por celda, sin fabricar triplicados. Estas pruebas documentales no validan experimentalmente una planta.

**Integración/interfaz:** Streamlit AppTest ejecuta cálculos reales de cada módulo y verifica ausencia de excepciones y mensajes de error; comprueba que los valores guardados se consumen en otros módulos. La importación/exportación CSV se ejecutó además mediante navegador.

## Resultados reproducibles

`python validate.py` produce validation/methodology con calibraciones sintéticas para cada instrumento, identificación de las tres celdas, auditoría SIMC, señales de filtro, protocolo inspirado en Fig.14 y resumen JSON.

- Banco predeterminado: residuo máximo de volumen 1.3642420526593924e-12 L.
- Protocolo inspirado en Fig.14: residuo máximo 1.8189894035458565e-12 L; T-1 inicial supuesto 60 L para permitir el retorno sin superar 130 L.
- Banco predeterminado, IAE físico FB / FB+FF (cm·s): C-1 34.146408 / 34.146145; C-2 68.406659 / 66.931127; C-3 92.050535 / 88.678645. Se conservan los resultados de versión 1.
- Demostración independiente de filtro: IAE real 40.502071, medido 138.556667, filtrado 79.430116 cm·s. El filtro reduce parte del error de ruido, pero no elimina el error de seguimiento ni se obliga a mejorar en todo escenario.
- Identificación sintética sin ruido: se recuperan k′=−0.001018 y θ=7,6,3 s con las tres repeticiones.

## Límites y decisiones metodológicas

No se dispone de series originales de autores ni de código MATLAB. No se declara validación contra curvas experimentales completas. La digitalización de Fig.12 es aproximada a intervalos de 10 s y no resuelve los retardos experimentales pequeños. Las ecuaciones rotuladas de calibración son redondeadas; la extrapolación y datos sintéticos se identifican.

La relación entre ganancia geométrica y publicada es 18.191079. No se encontró una explicación verificable en las fuentes consultadas; el área real no se modifica. El modelo Tabla 2 usa almacenamiento efectivo matemático. El primer orden usa parámetros supuestos y no se confunde con el integrador. Se conservan discrepancias de la Tabla 2 y las restricciones SIMC sin corregirlas silenciosamente.

La cadena PLC es un modelo ideal de señales y una muestra calculada de PI, no comunicación con hardware. Las calibraciones guardadas se aplican en esa cadena; no se afirma que el banco completo emule corriente, PLC y mecánica de bomba en cada paso. El aire es constante en el banco; calibración de aire y jg se calculan separadamente. Los parámetros propios y datos se conservan en la sesión y se exportan, sin persistencia remota.

## Distribución

Aplicación existente: https://celda-flotacion-feedforward.streamlit.app/
Repositorio existente: https://github.com/apsergio/celda-flotacion-feedforward
La versión 1 se conserva mediante etiqueta Git v1-control-nivel y ZIP separado.

**ZIP ampliado descomprimido:** 72 pruebas aprobadas en 61.17 s desde una carpeta nueva, usando el mismo entorno virtual de dependencias ya instalado. Se registró junit-zip-v2.xml. No se afirma una segunda instalación de dependencias desde cero. La comprobación CRC del archivo fue satisfactoria.

**Aplicación pública ampliada:** verificada en navegador tras publicar el commit 1589e6c. Se observó la navegación de versión 2 y se ejecutó Sintonización SIMC: al cambiar τc de 7 a 14 s, Kc pasó de −70.16559 a −46.77706 L/min/cm y Ti de 56 a 84 s; la gráfica y el IAE alternativo se recalcularon. Captura entregada: ampliacion-metodologica-publicada.jpg. No se atribuye a una prueba manual de cada combinación posible; los 12 módulos y controles descritos se verifican además por AppTest.

El cierre de distribución modifica documentación y añade el informe del ZIP; el código Python del ZIP final se compara por SHA-256 con la copia que pasó las 72 pruebas.

## Actualización visual y dictamen de replicación

Se unificó la paleta de gráficas, indicadores y proceso. FB azul (#7FA9F5), FB+FF verde agua (#35D6BB), SP ámbar (#FFC76A) y fondo de gráfica #0D1B2E. Contraste calculado de líneas sobre ese fondo: 7.332:1, 9.468:1 y 11.233:1; texto principal: 15.517:1. Esta medida no sustituye una auditoría completa de accesibilidad. Los gráficos mantienen nombres de serie y línea discontinua para consigna.

La actualización visual pasó las 72 pruebas existentes en 40.00 s. Tras añadir el dictamen descargable, los 21 casos de interfaz pasaron de nuevo en 43.16 s. Las ecuaciones, parámetros y resultados numéricos del banco no fueron modificados por el cambio de presentación. Se revisaron visualmente colores, nivel del tanque, marcas de consigna y conexiones de las bombas.

docs/DICTAMEN_REPLICACION.md contiene la matriz de alcance para el docente. La conclusión es reproducción metodológica verificable con supuestos declarados; no certificación de igualdad numérica con experimentos originales sin disponer de datos y código de los autores.

El ZIP de la actualización visual fue extraído en una carpeta nueva y aprobó las 72 pruebas en 51.08 s (junit-zip-visual.xml), con las mismas dependencias ya instaladas. No se alteraron los modelos para mejorar artificialmente la coincidencia con los resultados del artículo.

La actualización visual del commit f2aae2a se verificó en la URL pública. Streamlit quedó temporalmente en aprovisionamiento; tras un reinicio autorizado expresamente por el usuario volvió a abrir con la paleta y diagrama nuevos. Se inspeccionaron el banco completo y los indicadores, y se guardó diseno-profesional-publicado.jpg como evidencia. Esta verificación acredita disponibilidad y presentación, no equivalencia con series experimentales originales.
