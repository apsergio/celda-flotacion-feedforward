"""Comprobaciones de integridad y exportación para la entrega portable."""
import ast
from io import StringIO
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
import pytest
from model import Config, compare
from methodology import provenance_export, SOURCE, demo_calibration

ROOT=Path(__file__).resolve().parents[1]

def test_source_modules_and_declared_imports_exist():
    files=list(ROOT.glob('*.py'))+list((ROOT/'tests').glob('*.py'))
    required={'app','model','methodology','presentation','ui_modules','validate'}
    assert required.issubset({p.stem for p in files})
    for p in files:
        tree=ast.parse(p.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
            for name in names:
                top=name.split('.')[0]
                assert importlib.util.find_spec(top) is not None, f'{p.name}: {name}'
    for name in ('METODOLOGIA.md','DICTAMEN_REPLICACION.md','MANUAL.md'):
        assert (ROOT/'docs'/name).is_file()
    assert (ROOT/'data/fig12_digitized.csv').is_file()
    assert (ROOT/'.streamlit/config.toml').is_file()

def test_csv_bank_roundtrip_retains_time_modes_and_numeric_results():
    frame=compare(Config(duration=210,noise_cm=.03))
    tagged=provenance_export(frame,'Sintético de auditoría','Banco de tres celdas')
    text=tagged.to_csv(index=False)
    restored=pd.read_csv(StringIO(text))
    assert len(restored)==422 and set(restored['mode'])=={'FB','FB+FF'}
    assert restored.source.eq('Sintético de auditoría').all()
    assert restored.reference.eq(SOURCE).all()
    for i in range(1,4):
        assert np.allclose(restored[f'c{i}_h_cm'],frame[f'c{i}_h_cm'],rtol=0,atol=1e-12)
        assert restored[f'c{i}_iae_cm_s'].iloc[-1]==pytest.approx(frame[f'c{i}_iae_cm_s'].iloc[-1])

@pytest.mark.parametrize('instrument',['P-4','P-1','P-2','P-3','LI-1','LI-2','LI-3','FIC-1','FIC-2','FIC-3'])
def test_calibration_csv_roundtrip_all_instruments(instrument):
    frame=demo_calibration(instrument)
    tagged=provenance_export(frame,'Sintéticos de demostración',instrument)
    restored=pd.read_csv(StringIO(tagged.to_csv(index=False)))
    assert list(restored.columns)==list(tagged.columns)
    assert len(restored)==len(frame)
    assert restored.instrument.eq(instrument).all()
    assert restored.groupby('bits' if instrument.startswith(('P-','FIC-')) else 'h_cm').repeat.nunique().eq(3).all()

def test_playback_terminates_at_end_instead_of_refreshing_forever():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(ROOT/'app.py',default_timeout=90).run()
    app.session_state['cursor']=899
    app.session_state['running']=True
    app.run()
    assert not app.exception
    assert app.session_state['cursor']==900
    assert not app.session_state['running']
