# Dictamen de replicación para revisión docente

## Conclusión

**Se puede reproducir computacionalmente la metodología publicada y explorar sus modelos. No se puede certificar una réplica numérica exacta del experimento de los autores con la información actualmente disponible.** Las pruebas de software no acreditan equivalencia experimental. Este dictamen no es una certificación emitida por el docente ni por los autores.

El artículo de Quintanilla et al., MethodsX 10 (2023),102081, DOI https://doi.org/10.1016/j.mex.2023.102081 describe una implementación experimental de control con bombas, sensores, PLC y MATLAB. No se entregó una simulación original ejecutable que pueda copiarse o compararse directamente. En p.15 los autores indican que los datos se ofrecen bajo solicitud.

## Matriz de cumplimiento

| Requisito | Estado verificable | Límite |
|---|---|---|
| Calibración, triplicados y unidades | Implementados con importación/edición y regresión | Ejemplos sintéticos y coeficientes rotulados, no triplicados originales |
| Identificación k′/θ | Implementada y verificada con soluciones conocidas | Fig.12 digitalizada es aproximada y de una sola curva por celda |
| SIMC, PI finales y FF | Ecuaciones y tablas conservadas; cálculo y comparación funcionales | Inconsistencias del artículo se muestran sin reemplazar cifras |
| Banco de tres celdas y recirculación | Balance conservativo, ambas estrategias y protocolo dedicado | Concentrado, inventario y algunos límites son supuestos explícitos |
| Integrador y primer orden | Dos modelos independientes con ecuaciones y respuestas | El primer orden necesita parámetros no publicados como pareja validada |
| Filtro e IAE | Implementados y probados | Mediana causal; no se afirma equivalencia exacta de bordes MATLAB |
| Instrumentación | Conversión ideal 4–20 mA/INT y ajustes individuales | No emula hardware GE, DDE ni toda la mecánica de bombas |
| Igualdad con curvas originales | No demostrada | Faltan series completas, código y resolución de discrepancias |

## Información necesaria para exigir «tal cual»

1. Código MATLAB original y definición exacta de la actualización PI/FF, sesgos, saturaciones y condiciones iniciales.
2. Series temporales originales de consignas, niveles sin filtrar/filtrados, caudales y señales de cada ensayo y repetición.
3. Calibraciones originales sin redondear y sus observaciones por triplicado.
4. Tratamiento exacto de bordes y ejecución en línea de medfilt1, así como marcas temporales.
5. Aclaración de la discrepancia entre A=0.09 m² y k′=−0.001018, y de los parámetros iniciales de celda 3 en Tabla 2.

El docente debe precisar si acepta reproducción de la metodología con supuestos declarados o exige coincidencia de curvas. En el segundo caso, las fuentes anteriores son necesarias: cambiar colores o aprobar pruebas unitarias no suple esos datos.

## Validación disponible

La entrega incluye pruebas matemáticas, comprobaciones de transcripción, pruebas de interfaz, ensayo del ZIP descomprimido y verificación de la aplicación pública. Sus resultados ejecutados están en validation/INFORME.md y archivos JUnit. La actualización visual usa azul para FB, verde agua para FB+FF y ámbar discontinuo para SP; nombres y estilos evitan depender solo del color. Esa presentación no modifica las ecuaciones ni convierte datos sintéticos en experimentales.
