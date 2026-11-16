# Metodología ampliada · versión 2

Fuente: P. Quintanilla, D. Navia, F. Moreno, S. J. Neethling y P. R. Brito-Parada, MethodsX 10 (2023), 102081. **A methodology to implement a closed-loop feedback-feedforward level control in a laboratory-scale flotation bank using peristaltic pumps**. DOI https://doi.org/10.1016/j.mex.2023.102081. Artículo CC BY 4.0. Aplicación educativa independiente, no avalada por los autores.

Se revisaron las 15 páginas del PDF y se inspeccionaron visualmente las figuras 8,9,11,12 y Tabla 2 a mayor resolución. La versión anterior se conserva en Git (`v1-control-nivel`) y en METODOLOGIA_V1.md como documentación histórica.

## Procedencia y trazabilidad

- **Publicado:** tablas, ecuaciones rotuladas y valores IAE de las figuras. No son series originales recuperadas.
- **Digitalizado aproximado:** puntos leídos visualmente de Fig. 12; una sola curva visible por celda, sin fabricar repeticiones.
- **Sintético:** modelos y ruido calculados con semilla reproducible, nunca atribuidos a mediciones de los autores.
- **Propio:** observaciones introducidas por el docente. Se conserva su procedencia declarada, sin certificar cómo se obtuvieron.

| Componente | Fuente | Implementación |
|---|---|---|
| Banco y retorno de concentrados | pp. 2–5, Figs. 1–4 | Proceso con balance cerrado |
| Celdas 30×30×45 cm, A=0.09 m²; T-1=130 L | p. 2, Fig. 2 p. 4 | Auditoría y alternativa geométrica |
| Bombas: registros, 10 s y triplicados | p. 7, Fig. 9 p. 9 | Tabla/CSV, ajuste, residuos y estadística |
| Sensores 0–39 cm, descensos ~2 cm | pp. 6–10, Figs. 10–11 | Ajustes individuales LI-1/2/3 |
| Aire: lectura y salida | pp. 6–8, Fig. 8 | FIC-1/2/3 y velocidad superficial jg |
| INT 0–32767 y 4–20 mA | pp. 2,6–7 | Cadena ideal, cuantización y saturación |
| Identificación de k′ y θ | pp. 10–12, Fig. 12, Ec. 5 | Escalones, dos puntos, tres ensayos o importación |
| SIMC | Ecs. 2–6, pp. 8,10 | Calculadora, restricciones y alternativas PI |
| Modelos y PI finales | Tabla 2 p. 12 | k′=−0.001018; θ=(7,6,3); Kc=(−62,−76,−85); Ti=(56,30,44) |
| Feedforward | Ecs. 7–8, Fig. 13 p. 12 | Kff=(0.8,0.8,1), diferencia entre muestras |
| Primer orden | Ec. 4, Ecs. 10–15 p. 14 | Modelo independiente con respuesta analítica |
| 15 min, 1 s, mediana 10 muestras | p. 13 | Comparación dedicada y filtrado documentado |
| IAE y resultados publicados | Ec. 9, Fig. 14 p. 13 | Métricas reales/medidas/filtradas y panel experimental separado |
| Reactivos y tiempos | pp. 4–6,13 | Asistente de nueve etapas |

## Calibración

Ecuaciones transcritas de las figuras, con su precisión gráfica publicada:

| Instrumento | Ecuación rotulada | Salida |
|---|---|---|
| P-4 | Q=0.0035 N | L/min |
| P-1 | Q=0.0029 N | L/min |
| P-2, P-3 | Q=0.0033 N | L/min |
| LI-1 | h=−0.0018 N+40.1363 | cm |
| LI-2 | h=−0.0019 N+43.8823 | cm |
| LI-3 | h=−0.0020 N+41.293 | cm |
| Aire, lectura | Qair=0.0032 N | L/min |
| Aire, salida | Qair=0.0031 N | L/min |

N es el valor del registro INT. Los tres controladores de aire se declaran iguales en el artículo, pero los ajustes propios se guardan individualmente. Los coeficientes anteriores están redondeados y no constituyen nuevas mediciones digitalizadas.

Para bombas: Q=60V/Δt con V en L, Δt=10 s por defecto y registros 5000,10000,20000,25000,28000. Se ajustan todas las observaciones, con opción de intercepto libre o cero; se muestran pendiente, intercepto, R² centrado, RMSE, residuos y media/DE muestral por punto (`ddof=1`). Se comprueba el triplicado y se rechazan identificadores repetidos. Sin observaciones, una recta publicada no recibe R² o intervalos inventados.

El intervalo de predicción OLS 95% usa distribución t y n−p grados de libertad; presupone errores independientes, normales y de varianza constante. En sensores hay error en el eje de registro: OLS es aproximación docente, no certificación metrológica. La leyenda de Fig. 11 dice intercepto fijado en cero, pero las ecuaciones visibles tienen intercepto no nulo: se muestra la contradicción. El rango nominal 0–39 cm no implica validación experimental completa de la figura; las extrapolaciones se advierten.

## Identificación y SIMC

La planta individual integradora usa dy/dt=k′u(t−θ), en desviaciones respecto al punto inicial. Su entrada se mantiene constante y el escalón modifica la salida; no se aplica recirculación simultánea en este ensayo individual. Hay tres repeticiones sintéticas con ruido de semilla fija, o se importan las repeticiones existentes sin fabricar otras. Si un ensayo geométrico sale de 0–45 cm, se rechaza sin recortar la curva.

k′=(y2−y1)/[(t2−t1)Δu]. La estimación de θ prolonga la recta entre los puntos hasta la mediana de las muestras de los 10 s previos al escalón. Depende de ruido, selección y estabilidad de la línea base; no es un identificador universal. Se marcan retardos extrapolados inválidos y se permite aceptar θ por inspección. El banco usa un retardo entero ≥1 s, redondeado explícitamente.

SIMC: Kc=1/[k′(τc+θ)], Ti=min{τ1,4(τc+θ)}. En el límite integrador τ1→∞ se obtiene Ti=4(τc+θ). También puede explorarse τ1 finito. Se evalúan por separado τc≥θ y Ti≥4(τc+θ), según el texto; una contradicción con la operación min se informa.

Tabla 2 se conserva sin cambios. Para celda 3, k′=−0.001018, θ=3 y τc=8 dan Kc≈−89.30 y Ti=44 bajo el límite integrador, mientras la tabla rotula iniciales −78.1 y 52. Los Ti finales de celdas 2 y 3 tampoco cumplen esa cota usando los τc tabulados. Se muestran las diferencias; los finales publicados no se sustituyen por los iniciales. La comparación de τc usa la misma planta en ambos controladores. Guardar/aplicar un PI alternativo es explícito.

## Dos modelos independientes

Integrador, Tabla 2: dy/dt=k′u(t−θ); con condiciones iniciales nulas en desviaciones, sY=k′e^(−θs)U y G=k′e^(−θs)/s. Un escalón genera rampa después del retardo.

Primer orden, Ecs. 10–15: τ1 dy/dt=−y+ku(t−θ); τ1sY=−Y+ke^(−θs)U; G=ke^(−θs)/(τ1s+1). Un escalón converge a kΔu. El artículo no proporciona una pareja independiente (k,τ1) validada: en esta comparación son supuestos editables. Elegir k=k′τ1 iguala la pendiente inicial, no toda la respuesta. El primer orden se estudia por separado y no reemplaza el balance conservativo del banco.

## Geometría y discrepancia no resuelta

A=0.09 m²; Vmax=40.5 L; V=0.9h L con h en cm. El balance líquido implica k′=−1/(60×0.9)=−0.0185185 cm/s por L/min. Tabla 2 publica −0.001018, unas 18.19 veces menor. Interpretar esa ganancia como un balance puramente líquido exigiría almacenamiento efectivo 16.37 L/cm o área efectiva ~1.637 m², incompatible con el área geométrica sin escalamiento o física adicional.

Se consultaron la versión editorial, https://pmc.ncbi.nlm.nih.gov/articles/PMC9988547/ y repositorios Imperial/Brunel. La búsqueda por DOI y corrección no aportó una explicación verificable. Error de unidades, calibración o aireación son hipótesis, no hechos implementados. No se modifica arbitrariamente la geometría para forzar coincidencia.

Las alternativas son: geometría publicada, parámetros identificados por usuario y parámetros publicados Tabla 2. La última conserva un inventario efectivo matemático para la conservación; **no representa el volumen físico del equipo**.

## Banco, PI, instrumentación y filtro

V_i[k+1]=V_i[k]+(Qin_i−Qout_i−Qconc_i)/60; V_T[k+1]=V_T[k]+(Qout_3+ΣQconc−Qfeed)/60. Caudales L/min, volúmenes L, tiempo s. Las salidas reales alimentan simultáneamente la siguiente celda y todo concentrado vuelve a T-1. Se impide extraer inventario inexistente y el desborde retorna al tanque. Si T-1 supera 130 L, se detiene sin perder masa por recorte silencioso.

PI: u=Q0+Kc e+I+FF; I[k]=I[k−1]+Kc e[k]/Ti; e=SP−PV. Sesgo Q0, límites editables y anti-windup condicional son decisiones de ingeniería añadidas. No hay límite de velocidad de cambio. FF literal=Kff(Qin[k]−Qin[k−1]), Ecs. 7–8; la opción respecto al caudal inicial sigue marcada como extensión pedagógica.

Cadena PLC con ajustes individuales guardados o rectas publicadas: N=round[(I−4)32767/16], I=4+16N/32767; h=aLI N+bLI; NP=(Qorden−bP)/aP; Q=aP NP+bP. Se muestran valores ideales, cuantizados, saturados y escalados. La correspondencia eléctrica lineal es una convención ideal asumida, no emulación de códigos físicos GE. La vista calcula una muestra de PI con integral anterior editable; no se conecta a un PLC. No se inventa la relación bits/rpm a partir del rango 0–600 rpm.

El banco permite ruido gaussiano reproducible; ambas estrategias usan exactamente la misma realización. Mediana causal de N muestras incluida la actual, con relleno inicial al nivel inicial. Para N par se promedian los dos valores centrales. No se afirma equivalencia exacta con medfilt1 ni sus bordes. Se muestran señales real, medida, filtrada, sus errores y sus IAE trapezoidales; el filtro añade retraso y no garantiza mejorar seguimiento.

## Protocolo de Fig. 14 y alcance

El ensayo dedicado fija entrada C-1=45 L/min; entradas C-2/C-3 son los relaves previos, 900 s, 1 s y mediana 10. Sus niveles iniciales y escalones de consigna son didácticos, no las series originales. IAE experimentales rotulados, cm·s: C-1 198/164, C-2 325/187, C-3 260/221 para FB/FB+FF, mostrados separadamente. Fig. 14 ilustra cerca de 600 s aunque el texto declara 15 min; no se inventan datos faltantes. Los autores ofrecen originales bajo solicitud. Importar curvas propias o digitalizadas no equivale a validación experimental contra las series de los autores.

Concentrado constante 0.2 L/min por celda, límite 100 L/min, inventario T-1 inicial 100 L, sesgo, ubicación de retardos y lógica de desborde siguen como supuestos editables. No se simulan holdup, cinética de espuma, recuperación mineral, cámaras o DDE. El aire es constante en el banco; calibración y jg son módulos funcionales separados.

Los ajustes se guardan en sesión: calibraciones→PLC; identificación→planta/SIMC; SIMC→PI alternativo. Los parámetros JSON pueden exportarse/restaurarse y los CSV se descargan con manifiesto de procedencia. No hay persistencia remota de mediciones propias. Las pruebas matemáticas y de interfaz se separan de comprobaciones de transcripción; ninguna sustituye validar una planta física.
