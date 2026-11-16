# Banco de flotación: Feedback + Feedforward

## Ampliación metodológica · versión 2

La misma aplicación incorpora calibración individual de bombas, sensores y aire; identificación en lazo abierto; calculadora SIMC; comparación de modelos integrador/primer orden; cadena PLC; guía experimental; protocolo inspirado en Fig.14; filtrado e IAE por señal; exportación de resultados y procedencia. Consulte [Manual docente](docs/MANUAL.md), [metodología y límites](docs/METODOLOGIA.md) y [procedencia de digitalizaciones](data/PROCEDENCIA.md).

La presentación utiliza una paleta común de alto contraste: FB azul, FB+FF verde agua y SP ámbar discontinuo. El [dictamen de replicación](docs/DICTAMEN_REPLICACION.md) distingue una reproducción metodológica de una réplica numérica exacta, que no puede certificarse sin series y código originales.

Se conservan el banco y los controles de la versión 1. La etiqueta Git `v1-control-nivel` permite recuperar la entrega anterior. Los datos propios se procesan en la sesión; expórtelos antes de cerrar. Los modelos sintéticos y las digitalizaciones no equivalen a series experimentales originales.

Simulación científica educativa basada en Quintanilla et al., MethodsX (2023), DOI 10.1016/j.mex.2023.102081. Interfaz en español, tres celdas, tanque de retorno, cuatro bombas, PI publicados, retardos, perturbaciones, comparación e IAE.

Aplicación pública: https://celda-flotacion-feedforward.streamlit.app/
Repositorio: https://github.com/apsergio/celda-flotacion-feedforward

## Ejecución local (Python 3.11 recomendado)

Descomprima el ZIP, abra una terminal en la carpeta que contiene app.py y ejecute:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

En macOS/Linux use `.venv/bin/python` en lugar de `.venv\Scripts\python`.
Abra http://localhost:8501. Requiere Internet para instalar dependencias; después el cálculo funciona localmente.

1. Configure consignas, perturbación y escalones en el panel lateral.
2. Pulse Iniciar para reproducir; Pausar congela el tiempo y Reiniciar vuelve a cero.
3. Cambie estrategia visible para inspeccionar el banco. Ambas curvas aparecen en los gráficos.
4. Consulte IAE al final y descargue ambos ensayos en CSV.
5. Lea «Método y trazabilidad» antes de interpretar los resultados.

## Reproducibilidad y pruebas

```powershell
.venv\Scripts\python -m pytest -q
.venv\Scripts\python validate.py
```

`validation/` contiene CSV y resultados ejecutados. No hay aleatoriedad. Las curvas son calculadas; no son mediciones del laboratorio original. Las opciones «ganancia publicada» y «geometría» resuelven de forma explícita la discrepancia entre área y ganancia de la fuente. La variante FF respecto al caudal inicial es adicional; la predeterminada reproduce literalmente las diferencias entre muestras de las Ecs. 7–8.

## Publicación en GitHub y Streamlit Community Cloud

El proyecto está preparado para un repositorio Git. Cree un repositorio en su cuenta de GitHub, cargue estos archivos conservando las carpetas, y en https://share.streamlit.io seleccione «Create app», el repositorio, rama main y archivo app.py. Seleccione Python 3.11 en ajustes avanzados y publique. Requiere autenticación del propietario y vinculación de GitHub. No se incluyen credenciales. Verifique que la URL asignada abra y que Iniciar, Pausar, Reiniciar y CSV funcionen. No confunda localhost con una URL pública.

## Estructura

- `app.py`: interfaz y reproducción.
- `model.py`: balances, control PI, FF y simulación.
- `docs/METODOLOGIA.md`: ecuaciones, parámetros, referencias y supuestos.
- `tests/`: conservación, controles, IAE e interfaz.
- `validate.py`, `validation/`: reproducción de resultados.
- `requirements.txt`, `requirements-lock.txt`: dependencias y versiones probadas.

Código de esta entrega: licencia MIT (LICENSE). El artículo conserva su licencia CC BY 4.0 y su autoría original.
