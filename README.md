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
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

La activación anterior corresponde a Símbolo del sistema (CMD) en Windows. En PowerShell use `.\.venv\Scripts\Activate.ps1`. Si la política del equipo impide activar scripts, no es necesario modificarla: ejecute `.venv\Scripts\python -m pip install -r requirements.txt` y `.venv\Scripts\python -m streamlit run app.py` directamente.

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

`validation/` contiene CSV y resultados ejecutados. El ruido opcional utiliza una semilla reproducible. Las curvas son calculadas; no son mediciones del laboratorio original. Las opciones «ganancia publicada» y «geometría» exponen la discrepancia entre área y ganancia de la fuente, sin afirmar que la resuelvan físicamente. La variante FF respecto al caudal inicial es adicional; la predeterminada reproduce literalmente las diferencias entre muestras de las Ecs. 7–8.

## Publicación en GitHub y Streamlit Community Cloud

La aplicación existente utiliza el repositorio `apsergio/celda-flotacion-feedforward`, rama `main`, archivo `app.py`, Python 3.11. Los cambios de la rama principal se publican en la misma URL. El propietario necesita autenticación para administrar el despliegue; el visitante debe poder usar la URL pública sin iniciar sesión. No se incluyen credenciales en el proyecto. La entrega final se publica como un archivo adjunto de GitHub Releases con descarga directa.

## Estructura

- `app.py`: interfaz y reproducción.
- `model.py`: balances, control PI, FF y simulación.
- `ui_modules.py`: todos los módulos docentes y su navegación; es un archivo, no una carpeta de submódulos.
- `methodology.py`: calibración, identificación, SIMC, modelos y cálculos científicos.
- `presentation.py`: configuración visual compartida.
- `docs/METODOLOGIA.md`: ecuaciones, parámetros, referencias y supuestos.
- `tests/`: conservación, controles, IAE e interfaz.
- `validate.py`, `validation/`: reproducción de resultados.
- `audit_delivery.py`: inventario, comprobación de imports y revisión de distribución portable.
- `requirements.txt`, `requirements-lock.txt`: dependencias y versiones probadas.

Código de esta entrega: licencia MIT (LICENSE). El artículo conserva su licencia CC BY 4.0 y su autoría original.
