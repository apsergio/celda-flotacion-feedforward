# Validación de la entrega

Fecha: 16 de noviembre de 2026. Python 3.11, entorno virtual nuevo; versiones instaladas en requirements-lock.txt.

- 15 pruebas automatizadas aprobadas, incluidas conservación en ambos modelos y estrategias, límites de inventario y actuadores, PI individuales, equilibrio, respuesta perturbada, ganancia publicada, FF literal y variante, filtro mediano, IAE independiente y comparación reproducible.
- Streamlit AppTest: carga sin excepciones; Iniciar, Pausar y Reiniciar comprobados.
- Copia extraída del ZIP: 15 pruebas aprobadas en 56.53 s, usando el mismo entorno virtual recién instalado. No se hizo una segunda descarga de dependencias en otro entorno.
- Navegador: aplicación local abierta en http://127.0.0.1:8501; banco, indicadores, curvas, tabla IAE y avance del reloj observados.
- Residuo máximo de volumen en escenario predeterminado: 1.3642420526593924e-12 L.
- IAE calculado FB / FB+FF, cm·s: C-1 34.146408 / 34.146145; C-2 68.406659 / 66.931127; C-3 92.050535 / 88.678645.
- No hay validación frente a series experimentales originales: no fueron proporcionadas. No se validan recuperación metalúrgica ni dinámica de espuma.

La verificación pública se registra separadamente cuando se termine el despliegue. Este informe no afirma que la publicación haya finalizado.
