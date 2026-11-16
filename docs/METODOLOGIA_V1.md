# Modelo, metodología y trazabilidad

Fuente principal: P. Quintanilla, D. Navia, F. Moreno, S. J. Neethling y P. R. Brito-Parada, «A methodology to implement a closed-loop feedback-feedforward level control in a laboratory-scale flotation bank using peristaltic pumps», MethodsX 10 (2023), 102081. DOI: https://doi.org/10.1016/j.mex.2023.102081. Licencia CC BY 4.0. Se revisaron las 15 páginas. La aplicación es una simulación independiente y no fue validada por los autores.

## Parámetros publicados

| Componente | Valor / implementación | Fuente |
|---|---|---|
| Topología | T-1 → P-4 → C-1 → P-1 → C-2 → P-2 → C-3 → P-3 → T-1; concentrados al tanque | pp. 2–5, Figs. 1–4 |
| Geometría | Cada celda: 300 × 300 × 450 mm; T-1: 130 L | p. 2, Fig. 2 p. 4 |
| Bombas | Masterflex L/S 77916–10, 0–600 rpm | Tabla 1, p. 4 |
| Sensores | Flotador con sensor óptico; rango indicado 0–39 cm | pp. 2, 6–10, Fig. 11 |
| Ganancia k′ | −0.001018 cm/s por L/min, las tres celdas | Tabla 2, p. 12 |
| Retardo θ | 7, 6, 3 s | Tabla 2 |
| Kc final | −62, −76, −85 L/min/cm | Tabla 2 |
| Ti final | 56, 30, 44 s | Tabla 2 |
| Kff | 0.8, 0.8, 1.0 | p. 12, Ecs. 7–8 |
| PI | e = SP − PV; u = Kc(e + integral(e)/Ti) + Kff ΔQ | Ecs. 1 y 7 |
| ΔQ | Qd[k] − Qd[k−1], NO caudal absoluto | Ec. 8 |
| Muestreo / duración | 1 s / 15 min | p. 13 |
| Filtro | Mediana de ventana 10 s | p. 13 |
| IAE | Integral de valor absoluto del error | Ec. 9, p. 13 |
| Aire / alimentación | 47 L/min aire por celda; alimentación 45 L/min | pp. 13–14 |

## Balance y dos opciones de modelo

Se integran volúmenes de líquido a pasos de 1 s:

V_i[k+1] = V_i[k] + (Q_in,i − Q_out,i − Q_conc,i)/60.

V_T[k+1] = V_T[k] + (Q_out,3 + suma(Q_conc) − Q_feed)/60.

Q_in = (Q_feed, Q_out,1, Q_out,2). Todos los caudales están en L/min, volúmenes en L, niveles en cm y tiempos en s. Cada salida real se usa una única vez y simultáneamente como entrada de la celda siguiente. Los retardos de la Tabla 2 se representan como colas de órdenes de cada bomba. Esa ubicación física del retardo es un supuesto de implementación: el artículo identifica un retardo del proceso, sin descomponer sensor, bomba y transporte.

**Opción Tabla 2 (predeterminada):** V_i = C_eff h_i, C_eff = 1/(60 × 0.001018) = aproximadamente 16.37 L/cm. Así la derivada local respecto al caudal de salida coincide con la función integradora publicada, Gp = −0.001018 exp(−θs)/s. Es un inventario efectivo matemático, NO el volumen geométrico del equipo. La aparente capacidad de estas celdas supera la geometría real y no debe usarse para dimensionamiento físico.

**Opción geométrica:** V_i = 0.9 h_i, a partir del área de 900 cm². La ganancia resultante es −1/(60 × 0.9) = −0.0185185 cm/s por L/min, aproximadamente 18.2 veces la ganancia publicada. Se mantienen los PI de la Tabla 2 para mostrar la sensibilidad, lo que puede generar oscilaciones fuertes. No es posible imponer simultáneamente ambos valores sin una conversión o física adicional no publicada.

Las Ecs. 4 y 10–15 presentan una aproximación de primer orden autorregulada, mientras la Tabla 2 da explícitamente un integrador con retardo. Se usa la Tabla 2 porque corresponde a los parámetros finales del experimento; no se inventa una constante de autorregulación.

## Control discreto

PI posicional: u[k] = Q0 + Kc e[k] + I[k] + FF[k], I[k] = I[k−1] + Kc/Ti × e[k] × 1 s. El sesgo Q0 mantiene el equilibrio inicial y es un supuesto necesario para una formulación en variables de desviación. Se aplican límites 0–Qmax y anti-windup mediante integración condicional, añadido de ingeniería no especificado en el artículo. No se limita la velocidad de cambio, conforme a p. 14.

La modalidad predeterminada implementa literalmente FF[k] = Kff (Qin[k] − Qin[k−1]). Un escalón produce una contribución de una sola muestra. No se acumula esa contribución a escondidas. La opción «reference» es una variante pedagógica explícita: FF = Kff(Qin[k] − Qin[0]); no se atribuye a las Ecs. 7–8. El filtro es una mediana causal con 10 muestras inicializadas al nivel inicial; MATLAB medfilt1 puede usar otra convención de bordes/centrado, no especificada para implementación en línea.

El IAE mostrado integra el error del nivel físico con trapecios, incluyendo los saltos de SP en la malla de 1 s. Los gráficos muestran PV filtrado. Los CSV permiten recalcular también el IAE de PV. No se asume que una estrategia siempre mejora: cada resultado se calcula y se informa con su signo.

## Supuestos y datos ausentes

- Nivel inicial 25 cm; inventario inicial T-1 100 L; escalón de SP +1 cm en C-1 a 450 s y perturbación +8 L/min a 180 s son escenarios didácticos, no la secuencia exacta de Fig. 14.
- Concentrado líquido constante por celda: 0.2 L/min editable, sin cinética de espuma ni recuperación mineral. El experimento es bifásico agua/aire sin sólidos. El aire se considera constante a 47 L/min; no se modelan holdup ni compresibilidad.
- Qmax = 100 L/min editable: límite supuesto; 600 rpm es publicado, pero NO equivale a 100 L/min. No se presentan rpm ni bits sintéticos como calibrados. Fig. 9 proporciona curvas, pero no se transcriben coeficientes con precisión no disponible.
- Se impide retirar más líquido del disponible y se retorna desborde de celda a T-1. El cálculo se detiene si T-1 supera 130 L, con explicación en pantalla. No se pierde masa por recorte silencioso.
- No hay ruido ni deriva de sensor por defecto. Sensores, tuberías y bombas se representan funcionalmente; no se simulan PLC, electricidad, cámaras ni propiedades mecánicas.
- Los autores indican en p. 15 que los datos se facilitan bajo solicitud. No se cuenta con las series originales ni con el código MATLAB. No se afirma reproducir numéricamente los IAE experimentales ni validar contra datos medidos.

## Procedimiento experimental publicado y alcance

El artículo prepara agua con azul de metileno 10 ppm, MIBC 330 ppm, Flottec F160–10 20 ppm y goma xantana 600 ppm (pp. 4–6). Calibra por triplicado caudales y niveles (pp. 6–10); identifica k′ y θ mediante escalones abiertos y aplica SIMC: Kc = 1/[k′(τc+θ)], Ti = min(τ1,4(τc+θ)), Ecs. 2–6. Los valores finales se ajustan experimentalmente. La aplicación usa esos finales y no realiza una nueva identificación de planta. El artículo menciona SSE en antecedentes, pero compara IAE en los resultados. Se utiliza IAE.

La Fig. 14 publica comparaciones experimentales; p. 14 informa mejoras de 33 a 138 cm·s. Estas cifras son del artículo y no se usan como resultados calculados aquí. La evaluación de esta entrega es consistencia matemática, conservación y pruebas de software; no equivalencia experimental.

Valores rotulados en Fig. 14 (lectura visual, cm·s): C-1 FB 198 y FB+FF 164; C-2 325 y 187; C-3 260 y 221. No se importan como series ni se ajusta el modelo para forzar su coincidencia.
