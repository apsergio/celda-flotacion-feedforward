"""Cálculos metodológicos puros; las mediciones de ejemplo nunca son originales."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

SOURCE = 'https://doi.org/10.1016/j.mex.2023.102081'
PUMP_SLOPES = {'P-4': .0035, 'P-1': .0029, 'P-2': .0033, 'P-3': .0033}
LEVEL_FITS = {'LI-1': (-.0018,40.1363), 'LI-2': (-.0019,43.8823), 'LI-3': (-.002,41.293)}
AIR_SLOPES = {'lectura': .0032, 'salida': .0031}
PUBLISHED = pd.DataFrame({'celda':[1,2,3], 'kprime':[-.001018]*3, 'theta_s':[7.,6.,3.],
    'tau_c_s':[7.,6.,8.], 'Kc_inicial_tabla':[-70.2,-81.8,-78.1],
    'Ti_inicial_tabla_s':[56.,48.,52.], 'Kc_final':[-62.,-76.,-85.],
    'Ti_final_s':[56.,30.,44.], 'Kff':[.8,.8,1.]})
PROVENANCES = ['Sintéticos de demostración','Datos propios del usuario','Digitalización aproximada del artículo']

def finite(values, name='datos'):
    a=np.asarray(values,dtype=float)
    if not np.isfinite(a).all(): raise ValueError(f'{name}: faltan valores o hay números no finitos')
    return a

def linear_fit(x,y,zero=False):
    x,y=finite(x),finite(y)
    if len(x)!=len(y) or len(x)<3 or len(np.unique(x))<2:
        raise ValueError('Se necesitan al menos 3 pares y dos valores distintos de entrada')
    X=x[:,None] if zero else np.column_stack([x,np.ones(len(x))])
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    slope=float(beta[0]); intercept=0. if zero else float(beta[1])
    pred=slope*x+intercept; residual=y-pred; dof=len(x)-X.shape[1]
    sse=float(residual@residual); total=float(((y-y.mean())**2).sum())
    covariance=sse/dof*np.linalg.pinv(X.T@X)
    return dict(slope=slope,intercept=intercept,r2=1-sse/total if total else float(sse==0),
                rmse=float(np.sqrt(np.mean(residual**2))),residual=residual,
                covariance=covariance,dof=dof,zero=zero,sigma2=sse/dof)

def prediction_interval(fit,x):
    x=finite(x); X=x[:,None] if fit['zero'] else np.column_stack([x,np.ones(len(x))])
    mean=fit['slope']*x+fit['intercept']
    se=np.sqrt(fit['sigma2']+np.einsum('ij,jk,ik->i',X,fit['covariance'],X))
    margin=student_t.ppf(.975,fit['dof'])*se
    return mean,mean-margin,mean+margin

def triplicates(frame,group,value):
    data=frame.copy(); data[value]=finite(data[value],value)
    if 'repeat' not in data or data.duplicated([group,'repeat']).any():
        raise ValueError('Cada punto necesita identificadores de repetición únicos')
    stats=data.groupby(group)[value].agg(['count','mean','std']).reset_index()
    stats['triplicado_completo']=stats['count']==3
    return stats

def volume_to_flow(volume_L,seconds=10.):
    if seconds<=0: raise ValueError('El tiempo debe ser positivo')
    v=finite(volume_L)
    if np.any(v<0): raise ValueError('Volumen negativo')
    return v*60/seconds

def signal_to_register(ma,quantize=True):
    a=finite(ma,'mA')
    if np.any((a<4)|(a>20)): raise ValueError('Señal fuera de 4–20 mA')
    x=(a-4)/16*32767
    return np.rint(x).astype(int) if quantize else x

def register_to_signal(bits):
    b=finite(bits,'registro')
    if np.any((b<0)|(b>32767)): raise ValueError('Registro fuera de 0–32767')
    return 4+16*b/32767

def scale(value,lo,hi,out_lo,out_hi):
    if hi<=lo: raise ValueError('Rango de entrada inválido')
    return out_lo+(finite(value)-lo)/(hi-lo)*(out_hi-out_lo)

def air_velocity(q_L_min,area_m2=.09):
    if area_m2<=0: raise ValueError('Área debe ser positiva')
    return finite(q_L_min)*.001/60/area_m2*100 # m/s → cm/s

def geometry_audit(area_m2=.09,kprime=-.001018):
    if area_m2<=0 or kprime>=0: raise ValueError('Área positiva y ganancia de salida negativa requeridas')
    capacity=area_m2*10 # L por cm
    geometric=-1/(60*capacity)
    effective=1/(60*abs(kprime))
    return {'area_m2':area_m2,'capacity_L_cm':capacity,'volume_45cm_L':45*capacity,
            'kprime_geometric':geometric,'capacity_effective_L_cm':effective,
            'ratio':abs(geometric/kprime),'effective_area_m2':effective/10}

def simc(kprime,theta,tau_c,tau1=None):
    if not np.isfinite([kprime,theta,tau_c]).all() or kprime==0 or theta<0 or tau_c<=0:
        raise ValueError('k′ no nulo, θ ≥ 0 y τc > 0, todos finitos')
    bound=4*(tau_c+theta)
    if tau1 is not None and (not np.isfinite(tau1) or tau1<=0): raise ValueError('τ1 debe ser positivo')
    ti=bound if tau1 is None else min(tau1,bound)
    return {'Kc':1/(kprime*(tau_c+theta)),'Ti_s':ti,'Ti_min_s':bound,
            'tau_c_ok':tau_c>=theta,'Ti_ok':ti>=bound-1e-10,
            'tau1_assumption':'límite integrador τ1→∞' if tau1 is None else 'τ1 definido por usuario'}

def step_response(time,kprime=-.001018,theta=7.,delta_u=10.,step_at=20.,
                  h0=25.,kind='integrator',tau1=56.,k=None):
    time=finite(time,'tiempo')
    if theta<0 or tau1<=0: raise ValueError('θ ≥ 0 y τ1 > 0')
    elapsed=np.maximum(time-step_at-theta,0)
    if kind=='integrator': return h0+kprime*delta_u*elapsed
    if kind!='first_order': raise ValueError('Modelo desconocido')
    gain=kprime*tau1 if k is None else k
    return h0+gain*delta_u*(-np.expm1(-elapsed/tau1))

def synthetic_identification(cell=1,q0=20.,delta_u=20.,step_at=30.,duration=180,
                             noise=.015,gain=-.001018,theta=None,seed=2026):
    if cell not in (1,2,3) or delta_u==0 or q0<0 or q0+delta_u<0 or not 0<=step_at<duration:
        raise ValueError('Escalón/caudal/tiempo inválidos')
    theta=[7.,6.,3.][cell-1] if theta is None else theta
    rng=np.random.default_rng(seed); t=np.arange(duration+1,dtype=float)
    h=step_response(t,gain,theta,delta_u,step_at)
    return pd.concat([pd.DataFrame({'t_s':t,'h_cm':h+rng.normal(0,noise,len(t)),
        'h_real_cm':h,'q_L_min':q0+delta_u*(t>=step_at),'repeat':r,
        'source':PROVENANCES[0]}) for r in (1,2,3)],ignore_index=True)

def identify(frame,t1,t2,delta_u,step_at,baseline_window=10.):
    if t2<=t1 or delta_u==0 or t1<step_at: raise ValueError('t2 > t1 ≥ instante del escalón y Δu ≠ 0')
    rows=[]
    for rep,g in frame.groupby('repeat'):
        g=g.sort_values('t_s'); t=finite(g.t_s); y=finite(g.h_cm)
        if len(t)<3 or np.any(np.diff(t)<=0) or t1<t.min() or t2>t.max():
            raise ValueError('Tiempo ordenado, sin duplicados; puntos dentro de cada repetición')
        y1,y2=np.interp([t1,t2],t,y); slope=(y2-y1)/(t2-t1)
        base=y[(t>=step_at-baseline_window)&(t<=step_at)]
        if len(base)<2: raise ValueError('Faltan al menos dos muestras de línea base antes del escalón')
        baseline=float(np.median(base))
        theta=float(t1+(baseline-y1)/slope-step_at) if abs(slope)>1e-12 else np.nan
        rows.append({'repeat':rep,'y1_cm':y1,'y2_cm':y2,'delta_y_cm':y2-y1,
            'delta_t_s':t2-t1,'delta_u_L_min':delta_u,'kprime':slope/delta_u,
            'theta_extrapolada_s':theta,'baseline_cm':baseline,
            'theta_valida':bool(np.isfinite(theta) and 0<=theta<=t1-step_at)})
    return pd.DataFrame(rows)

def causal_median(values,window=10,initial=None):
    a=finite(values)
    if window<1 or int(window)!=window or not len(a): raise ValueError('Ventana entera positiva y señal no vacía')
    init=a[0] if initial is None else initial
    padded=np.r_[np.repeat(init,window-1),a]
    return np.array([np.median(padded[i:i+window]) for i in range(len(a))])

def iae(time,sp,signal):
    t,s,y=finite(time),finite(sp),finite(signal)
    if len(t)!=len(s) or len(t)!=len(y) or np.any(np.diff(t)<=0):
        raise ValueError('Señales con igual longitud y tiempo estrictamente creciente')
    return float(np.trapezoid(np.abs(s-y),t))

def filtering_demo(noise=.15,seed=2026,window=10):
    t=np.arange(901); sp=np.where(t<300,25.,26.)
    real=25+np.where(t<300,0.,1-np.exp(-(t-300).clip(0)/40))
    measured=real+np.random.default_rng(seed).normal(0,noise,len(t))
    filtered=causal_median(measured,window,initial=25.)
    return pd.DataFrame({'t_s':t,'sp_cm':sp,'real_cm':real,'medido_cm':measured,
        'filtrado_cm':filtered,'error_real_cm':sp-real,'error_medido_cm':sp-measured,
        'error_filtrado_cm':sp-filtered,'source':PROVENANCES[0]})

def provenance_export(frame,source,instrument,extra=None):
    result=frame.copy()
    if 'source' in result and 'input_source' not in result:
        result['input_source']=result['source']
    result['source']=source; result['instrument']=instrument
    result['reference']=SOURCE
    for k,v in (extra or {}).items(): result[k]=v
    return result

def demo_calibration(instrument,direction='lectura',seed=2026):
    rng=np.random.default_rng(seed)
    if instrument in PUMP_SLOPES:
        x=np.repeat([5000.,10000.,20000.,25000.,28000.],3)
        q=PUMP_SLOPES[instrument]*x+rng.normal(0,.25,len(x))
        return pd.DataFrame({'bits':x,'repeat':np.tile([1,2,3],5),'volume_L':q/6})
    if instrument in LEVEL_FITS:
        h=np.repeat(np.r_[np.arange(39.,0.,-2),0.],3)
        a,b=LEVEL_FITS[instrument]
        bits=np.rint((h-b)/a+rng.normal(0,12,len(h)))
        return pd.DataFrame({'h_cm':h,'repeat':np.tile([1,2,3],len(h)//3),'bits':bits})
    if instrument.startswith('FIC-'):
        x=np.repeat([1000.,5000.,10000.,15000.,20000.,24000.],3)
        return pd.DataFrame({'bits':x,'repeat':np.tile([1,2,3],6),
            'q_L_min':AIR_SLOPES[direction]*x+rng.normal(0,.2,len(x))})
    raise ValueError('Instrumento desconocido')
