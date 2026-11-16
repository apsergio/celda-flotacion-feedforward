"""Pruebas matemáticas independientes y transcripciones verificadas del PDF."""
import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from methodology import (linear_fit,prediction_interval,triplicates,volume_to_flow,
    signal_to_register,register_to_signal,air_velocity,geometry_audit,simc,
    step_response,synthetic_identification,identify,causal_median,iae,
    PUBLISHED,PUMP_SLOPES,LEVEL_FITS,AIR_SLOPES,demo_calibration,provenance_export)
from model import Config,simulate

@pytest.mark.parametrize('zero',[False,True])
def test_linear_regression_known_coefficients(zero):
    x=np.array([1.,2.,3.,4.,5.]); b=0. if zero else 7.
    fit=linear_fit(x,3*x+b,zero)
    assert fit['slope']==pytest.approx(3)
    assert fit['intercept']==pytest.approx(b)
    assert fit['r2']==pytest.approx(1)
    assert fit['rmse']<1e-12

def test_prediction_interval_and_noise():
    x=np.arange(12.); y=2*x+3+np.array([1,-1,2,-2,0,0]*2)
    fit=linear_fit(x,y); mean,lo,hi=prediction_interval(fit,x)
    assert np.all(lo<mean) and np.all(mean<hi)
    assert np.allclose(mean,fit['slope']*x+fit['intercept'])

def test_triplicate_statistics_and_duplicate_rejection():
    d=pd.DataFrame({'bits':[5000]*3,'repeat':[1,2,3],'q':[1.,2.,3.]})
    stats=triplicates(d,'bits','q').iloc[0]
    assert stats['mean']==2 and stats['std']==1 and stats.triplicado_completo
    with pytest.raises(ValueError): triplicates(pd.concat([d,d.iloc[:1]]),'bits','q')

def test_volume_units():
    assert volume_to_flow([1.,2.],10).tolist()==[6.,12.]
    with pytest.raises(ValueError): volume_to_flow([1],0)
    with pytest.raises(ValueError): volume_to_flow([-1],10)

def test_signal_endpoints_and_quantization_roundtrip():
    assert signal_to_register([4,12,20]).tolist()==[0,16384,32767]
    assert register_to_signal([0,32767]).tolist()==[4.,20.]
    current=np.linspace(4,20,101)
    assert np.max(abs(register_to_signal(signal_to_register(current))-current))<=8/32767+1e-12

@pytest.mark.parametrize('value',[3.99,20.01,np.nan])
def test_current_invalid(value):
    with pytest.raises(ValueError): signal_to_register(value)

@pytest.mark.parametrize('value',[-1,32768,np.inf])
def test_register_invalid(value):
    with pytest.raises(ValueError): register_to_signal(value)

def test_air_velocity_and_real_geometry():
    assert float(air_velocity(47))==pytest.approx(.87037037037037)
    g=geometry_audit()
    assert g['volume_45cm_L']==pytest.approx(40.5)
    assert g['kprime_geometric']==pytest.approx(-1/54)
    assert g['ratio']==pytest.approx((1/54)/.001018)
    assert g['effective_area_m2']>.09

def test_simc_equations_and_conditions():
    r=simc(-.001018,7,7)
    assert r['Kc']==pytest.approx(-1/(.001018*14))
    assert r['Ti_s']==56 and r['tau_c_ok'] and r['Ti_ok']
    assert not simc(-.001018,7,6)['tau_c_ok']
    assert not simc(-.001018,7,7,20)['Ti_ok']
    with pytest.raises(ValueError): simc(0,7,7)

def test_pdf_table2_transcription_and_visible_inconsistency():
    # Correspondencia documental: Tabla 2 p.12, verificación visual.
    assert PUBLISHED.Kc_final.tolist()==[-62.,-76.,-85.]
    assert PUBLISHED.Ti_final_s.tolist()==[56.,30.,44.]
    assert PUBLISHED.theta_s.tolist()==[7.,6.,3.]
    c3=PUBLISHED.iloc[2]; calc=simc(c3.kprime,c3.theta_s,c3.tau_c_s)
    assert abs(calc['Kc']-c3.Kc_inicial_tabla)>10
    assert calc['Ti_s']==44 and c3.Ti_inicial_tabla_s==52

def test_pdf_calibration_equation_transcriptions():
    # Correspondencia documental: ecuaciones rotuladas Figs.8,9,11.
    assert PUMP_SLOPES=={'P-4':.0035,'P-1':.0029,'P-2':.0033,'P-3':.0033}
    assert LEVEL_FITS['LI-2']==(-.0019,43.8823)
    assert AIR_SLOPES=={'lectura':.0032,'salida':.0031}

@pytest.mark.parametrize('tag',['P-4','P-1','P-2','P-3','LI-1','LI-2','LI-3','FIC-1','FIC-2','FIC-3'])
def test_synthetic_calibration_triplicates_fit(tag):
    d=demo_calibration(tag)
    if tag in PUMP_SLOPES:
        d['q']=volume_to_flow(d.volume_L); stats=triplicates(d,'bits','q'); fit=linear_fit(d.bits,d.q,True)
        assert fit['slope']==pytest.approx(PUMP_SLOPES[tag],rel=.02)
    elif tag in LEVEL_FITS:
        stats=triplicates(d,'h_cm','bits'); fit=linear_fit(d.bits,d.h_cm)
        assert fit['slope']==pytest.approx(LEVEL_FITS[tag][0],rel=.02)
    else:
        stats=triplicates(d,'bits','q_L_min'); fit=linear_fit(d.bits,d.q_L_min,True)
        assert fit['slope']==pytest.approx(AIR_SLOPES['lectura'],rel=.02)
    assert stats.triplicado_completo.all() and fit['r2']>.99

def test_distinct_integrator_first_order_limits_and_delay():
    t=np.array([0,7,8,10000.]); kp=-.001; du=10
    a=step_response(t,kp,7,du,0)
    b=step_response(t,kp,7,du,0,kind='first_order',tau1=50,k=-.05)
    assert a[0]==a[1]==25 and a[2]==pytest.approx(24.99)
    assert b[-1]==pytest.approx(24.5)
    assert a[-1]<0 # Matemático independiente, sin recorte físico oculto.
    assert b[2]>a[2]

@pytest.mark.parametrize('cell,delay',[(1,7),(2,6),(3,3)])
def test_kprime_and_delay_from_independent_noiseless_experiments(cell,delay):
    d=synthetic_identification(cell,noise=0)
    r=identify(d,60,150,20,30)
    assert len(r)==3 and np.allclose(r.kprime,-.001018)
    assert np.allclose(r.theta_extrapolada_s,delay)
    assert r.theta_valida.all()

def test_identification_rejects_invalid_points():
    d=synthetic_identification(noise=0)
    with pytest.raises(ValueError): identify(d,60,60,20,30)
    with pytest.raises(ValueError): identify(d,60,150,0,30)
    with pytest.raises(ValueError): identify(d,60,1000,20,30)

def test_filter_causal_edges_and_iae_analytic():
    assert causal_median([1,5,2,9],3,initial=0).tolist()==[0,1,2,5]
    assert causal_median([0,2],2,initial=0).tolist()==[0,1]
    assert iae([0,1,2],[2,2,2],[0,1,2])==2
    with pytest.raises(ValueError): iae([0,0],[1,1],[0,0])

def test_noise_same_realization_comparison_and_all_iaes():
    c=Config(duration=240,noise_cm=.1)
    fb=simulate(c); ff=simulate(c,True)
    for i in range(1,4):
        noise_fb=fb[f'c{i}_measured_cm']-fb[f'c{i}_h_cm']
        noise_ff=ff[f'c{i}_measured_cm']-ff[f'c{i}_h_cm']
        assert np.allclose(noise_fb,noise_ff)
        for suffix,col in [('measured','measured'),('filtered','pv')]:
            assert fb[f'c{i}_iae_{suffix}_cm_s'].iloc[-1]==pytest.approx(iae(fb.t_s,fb[f'c{i}_sp_cm'],fb[f'c{i}_{col}_cm']))

def test_identified_plant_is_used_in_bank():
    c=Config(duration=210,gain_mode='identified',kprime=(-.002,-.001018,-.001018),setpoint_step=(0,0,0))
    d=simulate(c)
    assert d.loc[181,'c1_h_cm']-d.loc[180,'c1_h_cm']==pytest.approx(.002*8)
    assert abs(d.balance_error_L).max()<1e-9

def test_digitalized_csv_is_single_visible_curve_not_fake_triplicates():
    path=Path(__file__).resolve().parents[1]/'data/fig12_digitized.csv'
    d=pd.read_csv(path)
    assert set(d.cell)=={1,2,3} and d.groupby('cell').repeat.nunique().eq(1).all()
    assert d.source.str.startswith('Digitalización aproximada').all()
    for cell,du in [(1,43.5),(2,49.5),(3,49.5)]:
        r=identify(d[d.cell==cell],30,100,du,30).iloc[0]
        expected=([-3.1,-3.1,-3.0][cell-1])/(70*du)
        assert r.kprime==pytest.approx(expected)

def test_provenance_import_does_not_erase_original_label():
    d=pd.DataFrame({'value':[1.],'source':['Sintético']})
    out=provenance_export(d,'Datos propios del usuario','P-4')
    assert out.source.iloc[0]=='Datos propios del usuario'
    assert out.input_source.iloc[0]=='Sintético'
