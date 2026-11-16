# Manual docente · versión 2

Aplicación: https://celda-flotacion-feedforward.streamlit.app/
Repositorio: https://github.com/apsergio/celda-flotacion-feedforward

## Instalación

Descomprima el ZIP. Python 3.11 recomendado. Abra terminal donde está app.py:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

La activación indicada corresponde a CMD en Windows. En PowerShell use `.\.venv\Scripts\Activate.ps1`. Si el equipo impide activar scripts, use directamente `.venv\Scripts\python -m pip install -r requirements.txt` y `.venv\Scripts\python -m streamlit run app.py`, sin cambiar la política de seguridad del equipo.

En Linux/macOS use `.venv/bin/python`. `requirements-lock.txt` conserva versiones probadas. Se necesita Internet para instalar; luego el cálculo local no depende del alojamiento público.

## Recorrido

1. **Procedimiento guiado:** revise nueve etapas. Marcar revisión no certifica ejecución física ni autoriza manipular reactivos.
2. **Calibración:** seleccione instrumento y procedencia. La recta publicada no fabrica observaciones. Para practicar use datos sintéticos; para medir, complete plantilla o CSV. Bombas: volumen en L recogido en 10 s, tres repeticiones. Guarde ajustes para Instrumentación PLC.
3. **Identificación:** seleccione celda y origen. Iniciar/Pausar/Reiniciar controlan reproducción; Ver ensayo completo muestra todas las muestras. Seleccione t1,t2 después del retardo, revise Δy,Δt,k′ y θ. Acepte θ por inspección y guarde cada celda. Fig. 12 digitalizada tiene una sola curva por celda.
4. **SIMC:** use Tabla 2 o identificación guardada, varíe τc y revise restricciones y respuesta. Los PI finales publicados permanecen disponibles. Solo se aplica una alternativa si la guarda y luego la selecciona en Proceso.
5. **Modelos matemáticos:** compare integrador y primer orden; revise la discrepancia geométrica. Los parámetros del primer orden son supuestos editables.
6. **Instrumentación PLC:** seleccione celda; cambie nivel, SP e integral anterior. Revise una muestra calculada de la cadena eléctrica, usando las calibraciones individuales guardadas. No hay conexión física al PLC.
7. **Proceso / Ensayos Feedback / Ensayos Feedforward:** conservan las funciones anteriores. En Modelo y supuestos puede elegir planta geométrica, Tabla 2 o las tres identificaciones guardadas, PI publicados o alternativos y ruido. Reproduzca y exporte ambas estrategias.
8. **Comparación experimental:** panel 1 simula protocolo de 900 s inspirado en Fig. 14, C-1 a 45 L/min constante. Panel 2 muestra IAE rotulados publicados. Panel 3 importa curvas propias/digitalizadas y calcula sus IAE por separado.
9. **Filtrado:** vea nivel real, medición ruidosa, mediana, errores e IAE, con señal sintética independiente o banco con control.
10. **Resultados y exportación:** descargue CSV y manifiesto de procedencia más ajustes JSON. Puede restaurar ajustes JSON; reimporte observaciones CSV en cada módulo. Los datos de sesión no son persistentes: exporte antes de cerrar.

## CSV

Comas, punto decimal, UTF-8. Cabeceras:

- Bombas: `bits,repeat,volume_L`.
- Nivel: `h_cm,repeat,bits`.
- Aire: `bits,repeat,q_L_min`, seleccionando lectura o salida.
- Identificación: `t_s,h_cm,q_L_min,repeat`.
- Comparación: `t_s,cell,strategy,h_cm,sp_cm`.

Cada repetición de identificación necesita tiempos sin duplicados, dos muestras previas al escalón y ambos puntos dentro de su rango. Identificadores de repetición no pueden duplicarse por punto de calibración. Se rechazan registros fuera de 0–32767 y niveles de calibración fuera de 0–39 cm. No se declara éxito ante datos incompletos.

## Interpretar y probar

Compare IAE de la misma señal y horizonte. El FF literal no garantiza mejorar todos los escenarios. El modelo Tabla 2 usa almacenamiento efectivo, no volumen físico; el geométrico puede oscilar con esos PI. Lea METODOLOGIA.md.

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python validate.py
```

Streamlit Cloud puede suspender por inactividad y tardar en despertar. El ZIP permite ejecución independiente. La versión anterior está preservada en la etiqueta Git v1-control-nivel y en un ZIP separado.
