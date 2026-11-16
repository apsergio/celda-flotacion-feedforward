import numpy as np
import pytest
from pathlib import Path
from model import Config, PI, simulate, compare, KC, TI, KFF

@pytest.mark.parametrize('gain',['published','geometric'])
@pytest.mark.parametrize('ff',[False,True])
def test_balance_and_bounds(gain,ff):
    d=simulate(Config(gain_mode=gain),ff)
    assert abs(d.balance_error_L).max()<1e-9
    assert d.tank_L.between(0,130).all()
    for i in range(1,4):
        assert d[f'c{i}_h_cm'].between(0,45).all()
        assert d[f'c{i}_u_L_min'].between(0,100).all()

@pytest.mark.parametrize('i',range(3))
def test_pi_direction_integral_and_saturation(i):
    p=PI(KC[i],TI[i],45,100)
    assert p.update(-.1)>45
    assert p.update(-.1)>45-KC[i]*.1
    for _ in range(100): assert p.update(-100)==100
    assert np.isfinite(p.integral)

def test_equilibrium():
    d=simulate(Config(disturbance=0,setpoint_step=(0,0,0)))
    for i in range(1,4): assert np.allclose(d[f'c{i}_h_cm'],25)

def test_iae_independent_integration():
    d=simulate()
    for i in range(1,4):
        expected=np.trapezoid(abs(d[f'c{i}_sp_cm']-d[f'c{i}_h_cm']),d.t_s)
        assert d[f'c{i}_iae_cm_s'].iloc[-1]==pytest.approx(expected)

def test_literal_ff_impulse():
    d=simulate(Config(setpoint_step=(0,0,0)),True)
    assert d.loc[180,'c1_ff_L_min']==pytest.approx(.8*8)
    assert d.loc[181,'c1_ff_L_min']==0

def test_delay_and_disturbance():
    d=simulate(Config(setpoint_step=(0,0,0)),False)
    assert d.loc[181,'c1_h_cm']>d.loc[180,'c1_h_cm']
    assert np.allclose(d.loc[:6,'c1_q_L_min'],44.8)
    assert d.loc[181,'c1_h_cm']-d.loc[180,'c1_h_cm']==pytest.approx(.001018*8)

def test_reference_ff_persists_explicit_variant():
    d=simulate(Config(ff_mode='reference'),True)
    assert d.loc[180,'c1_ff_L_min']==pytest.approx(6.4)
    assert d.loc[181,'c1_ff_L_min']==pytest.approx(6.4)

def test_sensor_median():
    d=simulate(Config())
    for i in range(1,4):
        h=d[f'c{i}_h_cm'].to_numpy()
        padded=np.r_[np.repeat(25.,9),h]
        expected=[np.median(padded[k:k+10]) for k in range(len(h))]
        assert np.allclose(d[f'c{i}_pv_cm'],expected)

def test_comparison_reproducible():
    d=compare(Config(duration=240))
    assert len(d)==482
    assert set(d['mode'])=={'FB','FB+FF'}
    assert not np.allclose(d[d['mode']=='FB'].c1_h_cm,d[d['mode']=='FB+FF'].c1_h_cm)

def test_interface():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=60).run()
    assert not app.exception
    next(b for b in app.button if 'Iniciar' in b.label).click().run()
    assert app.session_state['running']
    next(b for b in app.button if 'Pausar' in b.label).click().run()
    assert not app.session_state['running']
    next(b for b in app.button if 'Reiniciar' in b.label).click().run()
    assert not app.exception
    assert app.session_state['cursor']==0
