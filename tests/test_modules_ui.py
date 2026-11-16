from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'
MODULES=['Calibración','Identificación','Sintonización SIMC','Modelos matemáticos',
         'Instrumentación PLC','Procedimiento guiado','Ensayos Feedback','Ensayos Feedforward',
         'Comparación experimental','Filtrado','Resultados y exportación']

def open_module(name):
    app=AppTest.from_file(APP,default_timeout=90).run()
    app.radio(key='navigation').set_value(name).run()
    assert not app.exception
    assert not app.error, [e.value for e in app.error]
    return app

@pytest.mark.parametrize('name',MODULES)
def test_module_default_is_functional(name):
    app=open_module(name)
    assert len(app.header)+len(app.title)>0

def find(elements,label): return next(e for e in elements if e.label==label)

def test_calibration_save_is_consumed_by_plc():
    app=open_module('Calibración')
    find(app.radio,'Origen de los datos').set_value('Sintéticos de demostración').run()
    assert not app.exception and not app.error
    find(app.button,'Guardar ajuste individual y usarlo en PLC').click().run()
    assert 'P-4:lectura' in app.session_state['calibrations']
    find(app.selectbox,'Instrumento').set_value('P-1').run()
    find(app.button,'Guardar ajuste individual y usarlo en PLC').click().run()
    app.radio(key='navigation').set_value('Instrumentación PLC').run()
    assert not app.exception and not app.error
    assert app.session_state['calibrations']['P-1:lectura']['source']=='Sintéticos de demostración'

def test_identification_save_and_playback_controls():
    app=open_module('Identificación')
    find(app.button,'▶ Iniciar ensayo').click().run()
    assert app.session_state['ident_running']
    find(app.button,'Ⅱ Pausar ensayo').click().run()
    assert not app.session_state['ident_running']
    find(app.button,'↺ Reiniciar ensayo').click().run()
    assert app.session_state['ident_cursor']==0
    find(app.button,'Guardar identificación de esta celda').click().run()
    assert app.session_state['identified'][1]['kprime']<0
    app.radio(key='navigation').set_value('Sintonización SIMC').run()
    find(app.radio,'Planta de entrada').set_value('Identificación guardada en la sesión').run()
    assert not app.exception and not app.error

def test_simc_save_preserves_published_defaults():
    app=open_module('Sintonización SIMC')
    find(app.button,'Guardar PI calculado como alternativa de esta celda').click().run()
    assert app.session_state['tuned'][1]['ti']==56
    app.radio(key='navigation').set_value('Proceso').run()
    assert find(app.selectbox,'Controladores PI').value=='Finales publicados Tabla 2'
    assert not app.exception and not app.error

@pytest.mark.parametrize('tag',['LI-1','LI-2','LI-3','FIC-1','FIC-2','FIC-3'])
def test_sensor_air_synthetic_ui(tag):
    app=open_module('Calibración')
    find(app.selectbox,'Instrumento').set_value(tag).run()
    find(app.radio,'Origen de los datos').set_value('Sintéticos de demostración').run()
    assert not app.exception and not app.error

def test_digitalized_identification_ui():
    app=open_module('Identificación')
    find(app.radio,'Origen del ensayo').set_value('Digitalización aproximada del artículo').run()
    assert not app.exception and not app.error
