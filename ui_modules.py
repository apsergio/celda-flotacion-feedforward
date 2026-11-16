"""Módulos docentes conectados al mismo modelo de banco de la versión 1."""
from dataclasses import asdict
from pathlib import Path
from io import BytesIO
import json
import zipfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from model import Config, simulate, compare, KC, TI
from presentation import semantic_trace_color
from methodology import (PUBLISHED,PUMP_SLOPES,LEVEL_FITS,AIR_SLOPES,PROVENANCES,SOURCE,
    linear_fit,prediction_interval,triplicates,volume_to_flow,signal_to_register,
    register_to_signal,air_velocity,geometry_audit,simc,step_response,
    synthetic_identification,identify,causal_median,iae,filtering_demo,
    provenance_export,demo_calibration,scale)

ROOT=Path(__file__).resolve().parent
MODULES=['Proceso','Calibración','Identificación','Sintonización SIMC','Modelos matemáticos',
         'Instrumentación PLC','Procedimiento guiado','Ensayos Feedback','Ensayos Feedforward',
         'Comparación experimental','Filtrado','Resultados y exportación']

def chart(fig,title,x='Tiempo (s)',y='Nivel (cm)'):
    fig.update_layout(title=title,xaxis_title=x,yaxis_title=y,template='flotation',height=410,
                      margin=dict(t=50,b=45),legend=dict(orientation='h',y=-.25))
    for trace in fig.data:
        color=semantic_trace_color(trace.name)
        if color and trace.type=='scatter': trace.update(line_color=color,marker_color=color)
    st.plotly_chart(fig,use_container_width=True)

def csv_button(frame,label,name,key=None):
    st.download_button(label,frame.to_csv(index=False).encode('utf-8'),name,'text/csv',key=key)

def remember(name,frame,source,metadata=None):
    records=st.session_state.setdefault('exports',{})
    records[name]={'data':frame.copy(),'source':source,'metadata':metadata or {}}

def error_boundary(func):
    try: func()
    except (ValueError,KeyError,TypeError,pd.errors.ParserError,np.linalg.LinAlgError) as e:
        st.error(f'No se pudo calcular con esos datos: {e}')

def calibration():
    st.header('Calibración individual de instrumentos')
    st.caption('Figs. 7–11 · pp. 6–10. Los registros son valores INT, no una secuencia binaria.')
    instrument=st.selectbox('Instrumento',['P-4','P-1','P-2','P-3','LI-1','LI-2','LI-3','FIC-1','FIC-2','FIC-3'])
    direction=st.radio('Dirección de la calibración de aire',['lectura','salida'],horizontal=True) if instrument.startswith('FIC') else 'lectura'
    reference={'fuente':SOURCE}
    if instrument in PUMP_SLOPES:
        a,b=PUMP_SLOPES[instrument],0.; ylabel='Caudal (L/min)'
        st.latex(r'Q\,[L/min]=\frac{V\,[L]}{\Delta t\,[s]}\,60')
        st.write('Procedimiento publicado: registros 5000, 10000, 20000, 25000 y 28000; recoger volumen durante 10 s y repetir tres veces en cada punto.')
        default_zero=True; support=(0.,28000.)
    elif instrument in LEVEL_FITS:
        a,b=LEVEL_FITS[instrument]; ylabel='Nivel (cm)'; default_zero=False; support=(500.,8500.)
        st.write('Rango nominal publicado: 0–39 cm. Descender aproximadamente 2 cm y registrar tres lecturas por altura. Las figuras muestran solo parte de ese rango; extrapolar requiere validación propia.')
    else:
        a,b=AIR_SLOPES[direction],0.; ylabel='Caudal aire (L/min)'; default_zero=True; support=(0.,24000.)
        st.write('Fig. 8 distingue la calibración de lectura y la de salida. El artículo declara iguales los tres controladores de aire; los ajustes propios se guardan individualmente.')
        st.metric('Referencia publicada: 47 L/min',f'{float(air_velocity(47)):.4f} cm/s',delta='≈ 0.87 cm/s',delta_color='off')
        st.latex(r'j_g\,[cm/s]=\frac{Q_{air}\,[L/min]\,10^{-3}}{60 A\,[m^2]}100')
    source=st.radio('Origen de los datos',['Recta rotulada en el artículo',PROVENANCES[0],PROVENANCES[1]],horizontal=False)
    st.info(f'Referencia gráfica: y = {a:g} × registro + {b:g}. Coeficientes transcritos de la ecuación rotulada en la figura; precisión limitada por el redondeo publicado. No son mediciones originales recuperadas.')
    if source=='Recta rotulada en el artículo':
        x=np.linspace(*support,100); frame=pd.DataFrame({'bits':x,'ajuste_publicado':a*x+b})
        chart(go.Figure(go.Scatter(x=x,y=a*x+b,name='Recta publicada')),'Referencia de calibración','Registro PLC (0–32767)',ylabel)
        st.warning('No se calculan R², desviaciones ni intervalos con una recta sin observaciones. No se fabrican triplicados experimentales.')
        csv_button(provenance_export(frame,'Coeficientes rotulados publicados',instrument),'Descargar recta de referencia','recta_referencia.csv')
        if st.button('Usar recta publicada en instrumentación PLC'):
            st.session_state.setdefault('calibrations',{})[instrument+':'+direction]={'slope':a,'intercept':b,'source':'Coeficientes rotulados publicados','support':support}
            st.success('Referencia guardada para la cadena PLC. No equivale a calibración experimental propia.')
        return
    example=demo_calibration(instrument,direction)
    if source==PROVENANCES[0]:
        st.warning('Ejemplo sintético reproducible generado para practicar el cálculo. No contiene mediciones de los autores. En sensores, parte del rango se obtiene por extrapolación de la recta publicada.')
        data=st.data_editor(example,key=f'cal_demo_{instrument}_{direction}',num_rows='dynamic',use_container_width=True)
    else:
        own_key=f'cal_own_{instrument}_{direction}'
        upload=st.file_uploader('Importar CSV de mediciones propias',type='csv',key=own_key+'_upload')
        blank=example.copy(); blank['bits']=np.nan
        if 'volume_L' in blank: blank['volume_L']=np.nan; blank['bits']=example.bits
        if 'q_L_min' in blank: blank['q_L_min']=np.nan; blank['bits']=example.bits
        data=st.data_editor(pd.read_csv(upload) if upload else blank,key=own_key,num_rows='dynamic',use_container_width=True)
        csv_button(blank,'Descargar plantilla vacía',f'plantilla_{instrument}.csv')
        if data.isna().any().any(): st.info('Complete la tabla o importe el CSV para calcular. Cada punto usa repeat = 1, 2 y 3.'); return
    if data.empty: st.info('Ingrese al menos tres observaciones.'); return
    if not data.bits.between(0,32767).all(): raise ValueError('Registros fuera del rango INT 0–32767')
    if not np.allclose(data.bits,np.rint(data.bits)): raise ValueError('Los registros individuales deben ser enteros')
    if 'source' in data:
        st.caption('Procedencia contenida en el CSV: '+', '.join(str(v) for v in data.source.unique())+'. Se conserva como input_source al exportar, junto a la procedencia declarada en pantalla.')
    if instrument in PUMP_SLOPES:
        seconds=st.number_input('Tiempo de recolección (s); artículo: 10',min_value=.1,value=10.)
        data['q_L_min']=volume_to_flow(data.volume_L,seconds)
        group,value='bits','q_L_min'; x,y=data.bits,data.q_L_min
    elif instrument in LEVEL_FITS:
        if not data.h_cm.between(0,39).all(): raise ValueError('Alturas fuera de 0–39 cm')
        group,value='h_cm','bits'; x,y=data.bits,data.h_cm
    else:
        if not data.q_L_min.between(0,100).all(): raise ValueError('Caudal de aire fuera de 0–100 L/min')
        group,value='bits','q_L_min'; x,y=data.bits,data.q_L_min
    stats=triplicates(data,group,value)
    if not stats.triplicado_completo.all(): st.warning('Hay puntos con un número de repeticiones diferente de tres. Las estadísticas usan únicamente las mediciones existentes.')
    zero=st.checkbox('Forzar intercepto a cero',value=default_zero)
    if instrument in LEVEL_FITS and zero: st.warning('Las ecuaciones rotuladas de Fig. 11 tienen intercepto no nulo, pese a la leyenda. Se conserva la opción elegida y se informa esta discrepancia.')
    fit=linear_fit(x,y,zero)
    cols=st.columns(4)
    for col,label,val in zip(cols,['Pendiente','Intercepto','R²','RMSE'],[fit['slope'],fit['intercept'],fit['r2'],fit['rmse']]): col.metric(label,f'{val:.6g}')
    data['prediction']=fit['slope']*x+fit['intercept']; data['residual']=np.asarray(y)-data.prediction
    xx=np.linspace(float(min(x)),float(max(x)),150); mean,lo,hi=prediction_interval(fit,xx)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=xx,y=lo,line_width=0,showlegend=False))
    fig.add_trace(go.Scatter(x=xx,y=hi,line_width=0,fill='tonexty',name='Predicción 95% (regresión)'))
    fig.add_trace(go.Scatter(x=x,y=y,mode='markers',name='Observaciones: '+source))
    fig.add_trace(go.Scatter(x=xx,y=mean,name='Ajuste calculado'))
    if group=='bits': fig.add_trace(go.Scatter(x=stats[group],y=stats['mean'],mode='markers',error_y=dict(array=stats['std'].fillna(0)),name='Media ± 1 DE'))
    else: fig.add_trace(go.Scatter(x=stats['mean'],y=stats[group],mode='markers',error_x=dict(array=stats['std'].fillna(0)),name='Registro medio ± 1 DE'))
    chart(fig,'Curva individual y dispersión','Registro PLC',ylabel)
    st.caption('Intervalo de predicción OLS al 95%, con supuestos de residuos independientes, normales y de varianza constante. En sensores el error principal está en el eje de registro; OLS es una aproximación docente, no una calibración metrológica certificada.')
    st.dataframe(stats,use_container_width=True,hide_index=True)
    with st.expander('Errores de cada observación'): st.dataframe(data,use_container_width=True,hide_index=True)
    exported=provenance_export(data,source,instrument,{'direction':direction})
    csv_button(exported,'Descargar observaciones, ajustes y errores',f'calibracion_{instrument}.csv')
    csv_button(provenance_export(stats,source,instrument),'Descargar estadística de repeticiones',f'estadistica_{instrument}.csv')
    if st.button('Guardar ajuste individual y usarlo en PLC'):
        saved={k:fit[k] for k in ('slope','intercept','r2','rmse')}
        saved.update(source=source,support=[float(min(x)),float(max(x))])
        st.session_state.setdefault('calibrations',{})[instrument+':'+direction]=saved
        remember('calibracion_'+instrument+'_'+direction,exported,source,saved)
        st.success('Ajuste guardado para este instrumento en la sesión actual.')

def identification():
    st.header('Identificación en lazo abierto')
    st.caption('Fig. 12 · Ec. 5 · pp. 10–12. Ganancia de nivel respecto al caudal de salida.')
    cell=st.selectbox('Celda de identificación',[1,2,3])
    source=st.radio('Origen del ensayo',[PROVENANCES[0],PROVENANCES[2],PROVENANCES[1]])
    theta_pub=[7.,6.,3.][cell-1]
    if source==PROVENANCES[0]:
        col1,col2,col3=st.columns(3)
        q0=col1.number_input('Caudal inicial (L/min)',0.,100.,20.)
        delta=col2.number_input('Δu salida (L/min)',-50.,50.,20.)
        step_at=col3.number_input('Instante del escalón (s)',10.,100.,30.)
        duration=st.slider('Duración identificación (s)',120,600,180,30)
        noise=st.slider('Ruido sintético σ (cm)',0.,.1,.015,.005)
        gain_choice=st.selectbox('Planta del ensayo',['Ganancia publicada Tabla 2','Geometría publicada'])
        gain=-.001018 if gain_choice.startswith('Ganancia') else geometry_audit()['kprime_geometric']
        data=synthetic_identification(cell,q0,delta,step_at,duration,noise,gain)
        if not data.h_real_cm.between(0,45).all():
            st.error('El ensayo saldría del rango físico 0–45 cm. Reduzca Δu o la duración. No se recorta la curva para ocultar este resultado.'); return
        st.info('Tres repeticiones sintéticas con semillas reproducibles. Entrada de celda fijada en el equilibrio inicial; el escalón modifica únicamente su salida. No se ejecuta la recirculación del banco en este ensayo individual.')
    elif source==PROVENANCES[2]:
        raw=pd.read_csv(ROOT/'data/fig12_digitized.csv'); data=raw[raw.cell==cell].copy()
        delta=[43.5,49.5,49.5][cell-1]; step_at=30.; duration=120
        st.warning('Digitalización manual aproximada y escasa de la curva roja de Fig. 12, no datos originales. Solo hay una curva visible por celda: no se inventan tres repeticiones ni su variabilidad. El estado inicial no es estacionario y la estimación de θ puede ser sesgada.')
        st.write(f'Escalón leído de Fig. 12: Δu = {delta} L/min, alrededor de t = 30 s.')
    else:
        template=pd.DataFrame(columns=['t_s','h_cm','q_L_min','repeat'])
        csv_button(template,'Descargar plantilla de ensayo','plantilla_identificacion.csv')
        upload=st.file_uploader('CSV: t_s, h_cm, q_L_min, repeat',type='csv',key='ident_upload')
        data=st.data_editor(pd.read_csv(upload) if upload else template,num_rows='dynamic',key='ident_own',use_container_width=True)
        if data.empty: st.info('Introduzca o importe las repeticiones para calcular.'); return
        delta=st.number_input('Δu aplicado en el experimento (L/min)',value=20.)
        step_at=st.number_input('Instante experimental del escalón (s)',value=30.,min_value=0.)
        duration=float(data.t_s.max())
    for col in ('t_s','h_cm','repeat'):
        if col not in data: raise ValueError(f'Falta columna {col}')
    if not np.isfinite(data[['t_s','h_cm','repeat']].to_numpy(dtype=float)).all(): raise ValueError('Complete todos los valores numéricos')
    signature=str((source,cell,delta,step_at,duration))+data.to_csv(index=False)
    if st.session_state.get('ident_signature')!=signature:
        st.session_state.update(ident_signature=signature,ident_cursor=0.,ident_running=False)
    buttons=st.columns(4)
    if buttons[0].button('▶ Iniciar ensayo'): st.session_state.ident_running=True
    if buttons[1].button('Ⅱ Pausar ensayo'): st.session_state.ident_running=False
    if buttons[2].button('↺ Reiniciar ensayo'): st.session_state.update(ident_cursor=0.,ident_running=False)
    if buttons[3].button('Ver ensayo completo'): st.session_state.update(ident_cursor=duration,ident_running=False)
    @st.fragment(run_every=2 if st.session_state.ident_running else None)
    def play():
        if st.session_state.ident_running:
            st.session_state.ident_cursor=min(duration,st.session_state.ident_cursor+20)
            if st.session_state.ident_cursor>=duration: st.session_state.ident_running=False
        cursor=st.session_state.ident_cursor
        st.progress(cursor/duration,text=f'Ensayo: {cursor:g} / {duration:g} s')
        fig=go.Figure()
        for rep,g in data.groupby('repeat'):
            g=g[g.t_s<=cursor]
            fig.add_trace(go.Scatter(x=g.t_s,y=g.h_cm,name=f'Repetición {rep}'))
        fig.add_vline(x=step_at,line_dash='dash')
        chart(fig,'Respuesta de nivel: '+source)
        if 'q_L_min' in data:
            q=data[data.repeat==data.repeat.iloc[0]]; q=q[q.t_s<=cursor]
            chart(go.Figure(go.Scatter(x=q.t_s,y=q.q_L_min,name='Salida de la bomba')),'Escalón aplicado',y='Caudal (L/min)')
    play()
    st.caption('La reproducción no modifica el conjunto registrado; la identificación utiliza el ensayo completo mostrado en la tabla y exportable.')
    tmax=float(data.t_s.max()); tmin=float(data.t_s.min())
    if tmax<=step_at: raise ValueError('Faltan muestras posteriores al escalón')
    defaults=(min(step_at+max(theta_pub,10)+10,tmax-1),tmax-10 if tmax-10>step_at+20 else tmax)
    if defaults[1]<=defaults[0]: defaults=(step_at,tmax)
    point1=st.number_input('Punto 1: tiempo t1 (s)',min_value=max(step_at,tmin),max_value=tmax,value=float(defaults[0]))
    point2=st.number_input('Punto 2: tiempo t2 (s)',min_value=max(step_at,tmin),max_value=tmax,value=float(defaults[1]))
    outcome=identify(data,point1,point2,delta,step_at)
    st.latex(r"k'=\frac{y_2-y_1}{(t_2-t_1)\Delta u}\quad [cm\,s^{-1}/(L\,min^{-1})]")
    st.dataframe(outcome,hide_index=True,use_container_width=True)
    for column,label in [('kprime','k′'),('theta_extrapolada_s','θ extrapolado (s)')]:
        vals=outcome[column]
        st.write(f'{label}: media {vals.mean():.6g}; DE muestral {vals.std(ddof=1):.6g}' if len(vals)>1 else f'{label}: {vals.iloc[0]:.6g}; DE no estimable con una sola curva.')
    st.caption('θ se estima prolongando la recta entre los dos puntos hasta la mediana de las muestras de los 10 s previos al escalón. Depende de la selección, el ruido y la estabilidad de la línea base; no es un identificador universal.')
    if not outcome.theta_valida.all(): st.warning('Hay estimaciones extrapoladas de θ fuera del intervalo válido. Revise la línea base y los puntos; el valor aceptado por inspección se introduce por separado.')
    fig=go.Figure()
    for rep,g in data.groupby('repeat'):
        fig.add_trace(go.Scatter(x=g.t_s,y=g.h_cm,name=f'Rep. {rep}'))
        row=outcome[outcome.repeat==rep].iloc[0]
        fig.add_trace(go.Scatter(x=[point1,point2],y=[row.y1_cm,row.y2_cm],mode='markers+lines',marker_size=10,name=f'Puntos rep. {rep}'))
    chart(fig,'Selección de puntos para Δy y Δt')
    if len(outcome)!=3: st.warning('No hay tres repeticiones independientes disponibles. No se atribuye variabilidad experimental a datos inexistentes.')
    manual=st.number_input('θ aceptado por inspección (s)',min_value=1.,max_value=120.,value=theta_pub)
    st.caption('El banco discreto utiliza retardos enteros de al menos 1 s. Puede conservarse la estimación fraccionaria en el informe; el valor aplicado al banco se redondea y se muestra.')
    exported=provenance_export(data,source,f'C-{cell}')
    csv_button(exported,'Descargar ensayo con procedencia',f'identificacion_celda_{cell}.csv')
    csv_button(provenance_export(outcome,source,f'C-{cell}'),'Descargar identificación y variabilidad','parametros_identificados.csv')
    if st.button('Guardar identificación de esta celda'):
        k=float(outcome.kprime.mean())
        if k>=0: raise ValueError('La salida requiere ganancia negativa. Revise signo de Δu y puntos seleccionados.')
        saved={'kprime':k,'theta_s':float(manual),'delay_applied_s':int(round(manual)), 'source':source,'t1':point1,'t2':point2}
        st.session_state.setdefault('identified',{})[cell]=saved
        remember(f'identificacion_C{cell}',exported,source,saved)
        st.success(f'Identificación guardada; retardo aplicable al banco: {int(round(manual))} s. Disponible en Proceso y SIMC.')

@st.cache_data
def cached_simulate(config,ff=False): return simulate(config,ff)

@st.cache_data
def cached_compare(config): return compare(config)

def tuning():
    st.header('Calculadora SIMC y parámetros publicados')
    st.latex(r"K_c=\frac{1}{k'(\tau_c+\theta)},\qquad \tau_i=\min\{\tau_1,4(\tau_c+\theta)\}")
    st.caption('Ecs. 2–3, p. 8; condiciones de p. 10. En el límite integrador se usa τ1→∞, por lo que Ti = 4(τc+θ).')
    cell=st.selectbox('Celda para sintonización',[1,2,3]); pub=PUBLISHED.iloc[cell-1]
    source=st.radio('Planta de entrada',['Tabla 2','Identificación guardada en la sesión'])
    saved=st.session_state.get('identified',{}).get(cell)
    if source!='Tabla 2' and saved is None: st.warning('Primero guarde la identificación de esta celda.'); return
    kp=st.number_input('k′ [cm/s por L/min]',value=float(pub.kprime if source=='Tabla 2' else saved['kprime']),format='%.8f')
    theta=st.number_input('θ (s)',min_value=0.,value=float(pub.theta_s if source=='Tabla 2' else saved['theta_s']))
    tc=st.number_input('τc (s)',min_value=.1,value=float(pub.tau_c_s),step=1.)
    finite_tau=st.checkbox('Usar τ1 finito en Ec. 3 (en lugar del límite integrador)')
    tau1=st.number_input('τ1 (s)',min_value=.1,value=float(8*theta if theta>0 else 8.)) if finite_tau else None
    tune=simc(kp,theta,tc,tau1)
    a,b=st.columns(2); a.metric('Kc inicial calculado (L/min/cm)',f'{tune["Kc"]:.5f}'); b.metric('Ti inicial calculado (s)',f'{tune["Ti_s"]:.4f}')
    st.write(f'τc ≥ θ: {"cumple" if tune["tau_c_ok"] else "NO cumple"}. Ti ≥ 4(τc+θ) = {tune["Ti_min_s"]:g} s: {"cumple" if tune["Ti_ok"] else "NO cumple"}.')
    if not tune['tau_c_ok'] or not tune['Ti_ok']: st.warning('Los parámetros no satisfacen las condiciones indicadas en el artículo. Se permite analizarlos, pero no se presentan como una sintonización robusta.')
    rows=[]
    for _,r in PUBLISHED.iterrows():
        calc=simc(r.kprime,r.theta_s,r.tau_c_s)
        rows.append({**r.to_dict(),'Kc_Ec2_calculado':calc['Kc'],'Ti_limite_integrador_s':calc['Ti_s'],
                     'Kc_tabla_menos_calculo':r.Kc_inicial_tabla-calc['Kc'],
                     'Ti_tabla_menos_calculo_s':r.Ti_inicial_tabla_s-calc['Ti_s'],
                     'Ti_final_cumple_cota':bool(r.Ti_final_s>=calc['Ti_min_s'])})
    table=pd.DataFrame(rows); st.dataframe(table,hide_index=True,use_container_width=True)
    st.warning('La celda 3 da Kc≈−89.30 y Ti=44 s con k′=−0.001018, θ=3 y τc=8; Tabla 2 rotula −78.1 y 52 s como iniciales. No se fuerzan a coincidir. Los Ti finales de celdas 2 y 3 tampoco cumplen la cota usando esos τc. Se conservan los finales publicados como ajuste experimental.')
    st.subheader('Efecto de τc en el banco')
    st.caption('Ensayo simulado de 600 s, escalón +1 cm en la celda seleccionada a 120 s, sin perturbación externa. PI publicados en las otras dos celdas. No es una repetición del experimento original.')
    newkc=list(KC); newti=list(TI); newkc[cell-1]=tune['Kc']; newti[cell-1]=tune['Ti_s']
    steps=tuple(1. if j==cell-1 else 0. for j in range(3))
    plant_gains=[-.001018]*3; delays=[7,6,3]
    plant_gains[cell-1]=kp; delays[cell-1]=max(1,int(round(theta)))
    common=dict(duration=600,disturbance=0.,setpoint_at=120,setpoint_step=steps,
                gain_mode='identified',kprime=tuple(plant_gains),delays=tuple(delays))
    if kp>=0: st.error('Para este banco, k′ debe ser negativo por actuar sobre la salida.'); return
    ref=cached_simulate(Config(**common)); candidate=cached_simulate(Config(**common,kc=tuple(newkc),ti=tuple(newti)))
    fig=go.Figure()
    for label,d in [('PI final publicado',ref),('PI calculado con τc elegido',candidate)]:
        fig.add_trace(go.Scatter(x=d.t_s,y=d[f'c{cell}_pv_cm'],name=label))
    fig.add_trace(go.Scatter(x=ref.t_s,y=ref[f'c{cell}_sp_cm'],name='SP',line_dash='dash'))
    chart(fig,'Respuesta al variar la sintonización')
    st.write({label:float(d[f'c{cell}_iae_cm_s'].iloc[-1]) for label,d in [('IAE PI final (cm·s)',ref),('IAE PI calculado (cm·s)',candidate)]})
    csv_button(table,'Descargar comparación SIMC / Tabla 2','comparacion_simc.csv')
    if st.button('Guardar PI calculado como alternativa de esta celda'):
        st.session_state.setdefault('tuned',{})[cell]={'kc':tune['Kc'],'ti':tune['Ti_s'],'source':source,'tau_c':tc,'theta':theta,'kprime':kp}
        remember('simc',table,'Cálculo de ecuaciones; referencia Tabla 2',tune)
        st.success('Alternativa guardada. El modo predeterminado de Proceso sigue usando los PI finales publicados.')

def mathematical_models():
    st.header('Dos modelos matemáticos independientes')
    st.write('Se trabaja en desviaciones alrededor de un punto de operación: y = h − h₀ y u = Qsalida − Q₀. Un caudal de salida mayor hace disminuir el nivel, por lo que la ganancia es negativa.')
    a,b=st.columns(2)
    with a:
        st.subheader('A · Integrador con retardo — Tabla 2')
        st.latex(r"\frac{dy}{dt}=k'u(t-\theta)")
        st.latex(r"sY(s)=k'e^{-\theta s}U(s),\quad G_I(s)=\frac{k'e^{-\theta s}}s")
        st.write('k′: cm/s por L/min; θ: segundos. Con condiciones iniciales nulas para la transformada de desviaciones. Un escalón sostenido genera una rampa; no hay nivel de equilibrio propio.')
    with b:
        st.subheader('B · Primer orden — Ecs. 10–15')
        st.latex(r'\tau_1\frac{dy}{dt}=-y+ku(t-\theta)')
        st.latex(r'(\tau_1s+1)Y(s)=ke^{-\theta s}U(s),\quad G_F(s)=\frac{ke^{-\theta s}}{\tau_1s+1}')
        st.write('k: cm por L/min; τ1: constante de tiempo en segundos. Un escalón converge a kΔu. El artículo no publica una pareja independiente (k,τ1) validada para este modelo.')
    st.info('No son intercambiables. Relacionar k = k′τ1 iguala la pendiente inicial después del retardo, pero no sus respuestas a largo plazo. Esa relación es una elección comparativa, no un parámetro experimental adicional del artículo.')
    kp=st.number_input('k′ de comparación [cm/s por L/min]',value=-.001018,format='%.8f')
    theta=st.number_input('Retardo de comparación θ (s)',0.,120.,7.)
    tau=st.number_input('τ1 supuesto para primer orden (s)',1.,1000.,56.)
    linked=st.checkbox('Igualar pendiente inicial: k = k′τ1',value=True)
    k=kp*tau if linked else st.number_input('k del primer orden [cm por L/min]',value=-.057008,format='%.6f')
    du=st.number_input('Escalón de salida para comparar (L/min)',value=10.)
    t=np.arange(301); fig=go.Figure()
    frame=pd.DataFrame({'t_s':t,'integrador_cm':step_response(t,kp,theta,du),
        'primer_orden_cm':step_response(t,kp,theta,du,kind='first_order',tau1=tau,k=k)})
    for key,label in [('integrador_cm','Integrador'),('primer_orden_cm','Primer orden')]: fig.add_trace(go.Scatter(x=t,y=frame[key],name=label))
    chart(fig,'Respuesta independiente a un escalón de caudal')
    st.subheader('Auditoría de geometría y ganancia')
    audit=geometry_audit(); st.dataframe(pd.DataFrame([audit]),hide_index=True,use_container_width=True)
    st.latex(r"A=0.30\cdot0.30=0.09\;m^2,\quad V_{max}=40.5\;L")
    st.latex(r"\frac{dh\,[cm]}{dt\,[s]}=\frac{Q_{in}-Q_{out}-Q_{conc}}{60(0.9)}")
    st.write('Geometría: k′ = −0.0185185 cm/s por L/min. Tabla 2: −0.001018. Relación ≈18.19. El valor publicado implicaría A efectiva ≈1.637 m² si se interpreta como un balance puramente líquido; no equivale al área geométrica 0.09 m².')
    st.warning('No se encontró en las fuentes consultadas una corrección o un factor que resuelva la discrepancia. Aireación, escalamiento de señales y una posible errata son hipótesis, no conclusiones. No se cambia la geometría ni se convierte 16.37 L/cm en volumen físico del equipo.')
    st.markdown('[Versión editorial](https://doi.org/10.1016/j.mex.2023.102081) · [Texto completo PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9988547/) · [Repositorio Imperial](https://spiral.imperial.ac.uk/entities/publication/b2c4a9bd-e06f-4e55-80c2-4be6893a326a)')
    st.dataframe(pd.DataFrame([
        {'Alternativa':'Geometría publicada','Planta':'A = 0.09 m²; Vmax = 40.5 L','Control':'PI finales o alternativa elegida; su desempeño puede ser oscilatorio'},
        {'Alternativa':'Parámetros identificados por usuario','Planta':'k′ y θ guardados en Identificación','Control':'No se atribuyen esos parámetros a los autores'},
        {'Alternativa':'Tabla 2 publicada','Planta':'k′ = −0.001018; θ = 7,6,3 s','Control':'Kc = −62,−76,−85; Ti = 56,30,44 s'}]),hide_index=True,use_container_width=True)
    csv_button(provenance_export(frame,PROVENANCES[0],'Modelos independientes'),'Descargar respuestas comparadas','modelos.csv')
    remember('modelos',frame,PROVENANCES[0],{'kprime':kp,'theta':theta,'tau1_supuesto':tau,'k_supuesto':k})

def get_calibration(tag,direction='lectura'):
    saved=st.session_state.get('calibrations',{}).get(tag+':'+direction)
    if saved: return saved
    a,b=LEVEL_FITS[tag] if tag in LEVEL_FITS else (PUMP_SLOPES[tag],0.) if tag in PUMP_SLOPES else (AIR_SLOPES[direction],0.)
    return {'slope':a,'intercept':b,'source':'Coeficientes rotulados publicados (redondeados)'}

def instrumentation():
    st.header('Cadena de instrumentación y escalamiento PLC')
    st.caption('Figs. 4–9 y 11 · tipo INT 0–32767 · señal configurada 4–20 mA. Conversión eléctrica ideal lineal asumida; no emula registros físicos de módulos GE ni comunicación DDE.')
    st.markdown('**Nivel real → sensor → 4–20 mA → INT → escalamiento individual → PI → INT → 4–20 mA → bomba → caudal.**')
    cell=st.selectbox('Celda / instrumentos PLC',[1,2,3]); sensor=get_calibration(f'LI-{cell}'); pump=get_calibration(f'P-{cell}')
    st.write(f'LI-{cell}: {sensor["source"]}. P-{cell}: {pump["source"]}.')
    h=st.slider('Nivel físico de entrada (cm)',0.,39.,25.,.1)
    sp=st.slider('Consigna PI (cm)',0.,39.,25.,.1)
    previous_i=st.number_input('Estado integral anterior (L/min)',value=0.)
    bias=st.number_input('Sesgo de caudal del PI (L/min)',0.,100.,45.)
    if abs(sensor['slope'])<1e-15 or pump['slope']<=0: raise ValueError('Calibraciones no invertibles o pendiente de bomba no positiva')
    raw_sensor=(h-sensor['intercept'])/sensor['slope']
    sensor_bits=int(np.clip(np.rint(raw_sensor),0,32767)); ma=float(register_to_signal(sensor_bits))
    recovered=int(signal_to_register(ma)); pv=sensor['slope']*recovered+sensor['intercept']
    p_gain=float(KC[cell-1]); ti=float(TI[cell-1]); error=sp-pv
    integral=previous_i+p_gain/ti*error; command=bias+p_gain*error+integral
    raw_pump=(command-pump['intercept'])/pump['slope']
    pump_bits=int(np.clip(np.rint(raw_pump),0,32767)); pump_ma=float(register_to_signal(pump_bits))
    flow=pump['slope']*pump_bits+pump['intercept']
    if not 0<=raw_sensor<=32767 or not 0<=raw_pump<=32767: st.warning('Hay saturación por límites INT. Se muestran registros ideales y limitados por separado.')
    st.caption('Cálculo de una muestra de 1 s del PI publicado; el estado integral se introduce explícitamente. El banco usa integración temporal y anti-windup propios; esta vista explica cada conversión sin afirmar conectividad con un PLC real.')
    chain=pd.DataFrame([
        ['Nivel real',h,'cm'],['Registro sensor ideal',raw_sensor,'cuentas INT'],['Registro sensor cuantizado',sensor_bits,'cuentas INT'],
        ['Señal de sensor',ma,'mA'],['Registro recuperado',recovered,'cuentas INT'],['PV escalada',pv,'cm'],
        ['Error SP−PV',error,'cm'],['Integral después de 1 s',integral,'L/min'],['Orden PI',command,'L/min'],
        ['Registro bomba ideal',raw_pump,'cuentas INT'],['Registro bomba limitado',pump_bits,'cuentas INT'],
        ['Señal bomba',pump_ma,'mA'],['Caudal resultante',flow,'L/min']],columns=['Etapa','Valor','Unidad'])
    st.dataframe(chain,hide_index=True,use_container_width=True)
    fig=go.Figure(go.Bar(x=chain.Etapa,y=chain.Valor,text=chain.Unidad)); chart(fig,'Señales antes y después del escalamiento','Etapa','Valor (unidades distintas; ver tabla)')
    st.latex(r'N=\operatorname{round}\!\left(\frac{I-4}{16}32767\right),\quad I=4+16\frac{N}{32767}')
    st.latex(r'h=a_{LI}N+b_{LI},\quad N_P=(Q_{orden}-b_P)/a_P,\quad Q=a_PN_P+b_P')
    with st.expander('Conversor 4–20 mA / registro independiente'):
        v=st.number_input('Corriente para convertir (mA)',4.,20.,12.,.01)
        reg=st.number_input('Registro para convertir',0,32767,16384)
        st.write(f'{v:.2f} mA → {int(signal_to_register(v))} cuentas; {reg} cuentas → {float(register_to_signal(reg)):.6f} mA')
    st.caption('No se convierte automáticamente 32767 cuentas en 600 rpm: esa correspondencia específica no queda establecida por las curvas de caudal. Cada bomba conserva su propia calibración.')
    csv_button(provenance_export(chain,'Cálculo ideal con calibraciones seleccionadas',f'C-{cell}'),'Descargar cadena PLC','cadena_plc.csv')
    remember('instrumentacion',chain,'Cálculo ideal con calibraciones seleccionadas',{'sensor':sensor,'pump':pump})

STAGES=[
('Preparación de reactivos','El experimento es agua–aire sin sólidos. Concentraciones publicadas: azul de metileno 10 ppm; MIBC 330 ppm; Flottec F160–10 20 ppm; goma xantana 600 ppm. pp. 4–6. Las cantidades de solución comercial dependen de concentración, pureza y densidad, no especificadas aquí.'),
('Homogeneización del tanque','Añadir los tres primeros reactivos en el orden publicado: azul de metileno, MIBC y Flottec F160–10. Agitar el tanque durante 5 min. p. 6.'),
('Preparación de la solución de xantana','Preparar aparte para evitar grumos; cuando esté homogénea, añadir al tanque y agitar con agitador externo otros 5 min. El agua de esta preparación forma parte del volumen final. Ejemplo publicado: 98 L en tanque + 2 L para xantana = 100 L. No se publica un tiempo fijo para disolverla aparte. p. 6.'),
('Calibración de instrumentos','Configurar 4–20 mA. Calibrar bombas y sensores individualmente en triplicado; bombas con 10 s de recolección. Ver módulo Calibración y Figs. 7–11.'),
('Estabilización del aire','Establecer 47 L/min en cada celda durante 5 min antes del ensayo; jg ≈ 0.87 cm/s usando A = 0.09 m². p. 13.'),
('Identificación de cada celda','Aplicar escalones de salida en lazo abierto por triplicado. Seleccionar dos puntos posteriores al retardo y estimar k′ y θ. Fig. 12 y Ec. 5. Ver módulo Identificación.'),
('Cálculo de parámetros SIMC','Aplicar Ecs. 2–6 y revisar restricciones. Comparar parámetros iniciales calculados con Tabla 2, conservando los valores finales ajustados por ensayo y error. Ver Sintonización SIMC.'),
('Ensayos de control','Experimentos publicados: 15 min, muestreo 1 s y mediana de 10 s. Comparar PI solo y PI+FF con Kff = 0.8,0.8,1. Ver Ensayos Feedback y Feedforward.'),
('Comparación de resultados','Calcular IAE por celda y estrategia. Separar ensayos propios, digitalizaciones y simulaciones. Datos de Fig. 14 no equivalen a series originales; los autores los ofrecen bajo solicitud. Exportar resultados y procedencia.')]

def procedure():
    st.header('Procedimiento experimental guiado')
    st.warning('Guía educativa. No autoriza manipular reactivos ni operar equipos sin supervisión y los procedimientos del laboratorio.')
    index=st.selectbox('Etapa del procedimiento',range(9),format_func=lambda i:f'{i+1}. {STAGES[i][0]}')
    st.subheader(STAGES[index][0]); st.write(STAGES[index][1])
    if index in (0,2):
        volume=st.number_input('Volumen final de mezcla para cálculo docente (L)',1.,130.,100.)
        masses=pd.DataFrame({'Reactivo':['Azul de metileno','MIBC','Flottec F160–10','Goma xantana'],
            'Concentración publicada (ppm)':[10,330,20,600]})
        masses['Masa nominal equivalente (g)']=masses['Concentración publicada (ppm)']*volume/1000
        st.dataframe(masses,hide_index=True,use_container_width=True)
        st.caption('Cálculo derivado bajo aproximación acuosa diluida 1 ppm ≈ 1 mg/L. No son volúmenes de reactivo comercial ni una receta operativa; no se supone pureza o densidad.')
    checked=st.checkbox('Marcar esta etapa como revisada',key=f'procedure_stage_{index}')
    count=sum(bool(st.session_state.get(f'procedure_stage_{j}',False)) for j in range(9))
    st.progress(count/9,text=f'{count} de 9 etapas revisadas (no certifica ejecución física)')
    frame=pd.DataFrame({'etapa':[s[0] for s in STAGES],'procedimiento_publicado':[s[1] for s in STAGES],
        'revisada':[bool(st.session_state.get(f'procedure_stage_{j}',False)) for j in range(9)]})
    csv_button(frame,'Descargar registro de revisión','procedimiento_guiado.csv')

def experimental_comparison():
    st.header('Comparación experimental · ensayo inspirado en Fig. 14')
    st.info('La alimentación a C-1 se mantiene en 45 L/min. C-2 recibe los relaves de C-1 y C-3 los de C-2. Duración 900 s; muestreo 1 s; mediana causal de 10 muestras. Las consignas siguientes son supuestos didácticos y no una recuperación exacta de las series originales.')
    tab_sim,tab_published,tab_import=st.tabs(['Simulación del protocolo','Resultados experimentales publicados','Datos propios / digitalizados'])
    with tab_sim:
        noise=st.slider('Ruido de sensor σ para el protocolo (cm)',0.,.3,.03,.01)
        start=(29.,34.,33.)
        changes=tuple(st.number_input(f'ΔSP didáctico C-{i+1} a 150 s (cm)',-2.,2.,-1.,.5) for i in range(3))
        c=Config(duration=900,feed=45.,disturbance=0.,initial=start,sp=start,
                 setpoint_at=150,setpoint_step=changes,median_window=10,noise_cm=noise,tank_initial=60.)
        st.caption('Inventario inicial T-1 supuesto: 60 L, para alojar el retorno de los tres escalones de nivel sin exceder 130 L. No es una condición inicial publicada.')
        data=cached_compare(c); metrics=[]
        for i in range(1,4):
            fig=go.Figure()
            for mode,g in data.groupby('mode'):
                fig.add_trace(go.Scatter(x=g.t_s,y=g[f'c{i}_pv_cm'],name=mode+' filtrado'))
                metrics.append({'celda':i,'strategy':mode,'source':PROVENANCES[0],
                    'IAE_real_cm_s':iae(g.t_s,g[f'c{i}_sp_cm'],g[f'c{i}_h_cm']),
                    'IAE_medido_cm_s':iae(g.t_s,g[f'c{i}_sp_cm'],g[f'c{i}_measured_cm']),
                    'IAE_filtrado_cm_s':iae(g.t_s,g[f'c{i}_sp_cm'],g[f'c{i}_pv_cm'])})
            g=data[data['mode']=='FB']; fig.add_trace(go.Scatter(x=g.t_s,y=g[f'c{i}_sp_cm'],name='SP',line_dash='dash'))
            chart(fig,f'C-{i} · simulación del protocolo')
        st.dataframe(pd.DataFrame(metrics),hide_index=True,use_container_width=True)
        fig=go.Figure()
        for mode,g in data.groupby('mode'):
            fig.add_trace(go.Scatter(x=g.t_s,y=g.feed_L_min,name=f'{mode} entrada C-1'))
            for i in (1,2): fig.add_trace(go.Scatter(x=g.t_s,y=g[f'c{i}_q_L_min'],name=f'{mode} entrada C-{i+1}'))
        chart(fig,'Perturbaciones medidas: topología de Fig. 15',y='Caudal (L/min)')
        csv_button(provenance_export(data,PROVENANCES[0],'Banco inspirado Fig.14'),'Descargar comparación del protocolo','protocolo_fig14_simulado.csv')
        remember('fig14_simulado',data,PROVENANCES[0],asdict(c))
    with tab_published:
        published=pd.DataFrame({'celda':[1,2,3],'IAE_FB_cm_s':[198,325,260],'IAE_FB_FF_cm_s':[164,187,221]})
        published['reduccion_cm_s']=published.IAE_FB_cm_s-published.IAE_FB_FF_cm_s
        st.dataframe(published,hide_index=True,use_container_width=True)
        st.caption('Valores experimentales rotulados en Fig. 14, p. 13. No son métricas del simulador. La figura ilustra aproximadamente 600 s aunque el texto declara ensayos de 15 min; no se interpreta la tabla como una serie de 900 s disponible.')
        st.warning('No hay curvas numéricas originales incluidas. No se ajustan parámetros para hacer coincidir artificialmente los IAE. La diferencia simulación/experimento no constituye por sí sola un error de software ni una validación física.')
        csv_button(provenance_export(published,'Valores experimentales rotulados Fig.14','Banco'),'Descargar valores rotulados publicados','fig14_iae_publicados.csv')
    with tab_import:
        source=st.radio('Procedencia del CSV comparativo',[PROVENANCES[1],PROVENANCES[2]],key='comparison_source')
        template=pd.DataFrame(columns=['t_s','cell','strategy','h_cm','sp_cm'])
        csv_button(template,'Descargar plantilla comparativa','plantilla_comparativa.csv')
        upload=st.file_uploader('CSV con t_s, cell, strategy, h_cm y sp_cm',type='csv',key='comparison_upload')
        frame=st.data_editor(pd.read_csv(upload) if upload else template,num_rows='dynamic',key='comparison_editor',use_container_width=True)
        if not frame.empty:
            rows=[]; fig=go.Figure()
            for (cell,mode),g in frame.groupby(['cell','strategy']):
                g=g.sort_values('t_s')
                rows.append({'celda':cell,'strategy':mode,'IAE_cm_s':iae(g.t_s,g.sp_cm,g.h_cm),'source':source})
                fig.add_trace(go.Scatter(x=g.t_s,y=g.h_cm,name=f'C-{cell} {mode}'))
                fig.add_trace(go.Scatter(x=g.t_s,y=g.sp_cm,line_dash='dash',name=f'C-{cell} SP {mode}'))
            chart(fig,'Datos importados: '+source); st.dataframe(rows,hide_index=True)
            tagged=provenance_export(frame,source,'Comparación importada')
            csv_button(tagged,'Descargar datos con procedencia','comparacion_importada.csv')
            remember('comparacion_importada',tagged,source)

def filtering():
    st.header('Filtrado, error e IAE de cada señal')
    use_bank=st.radio('Señal de entrada',['Demostración sintética independiente','Banco con control y ruido'])
    sigma=st.slider('Ruido gaussiano σ (cm)',0.,.5,.15,.01)
    window=st.slider('Ventana de mediana causal (muestras)',1,21,10)
    seed=st.number_input('Semilla reproducible',min_value=0,value=2026,step=1)
    if use_bank.startswith('Demostración'):
        data=filtering_demo(sigma,int(seed),window)
    else:
        cell=st.selectbox('Celda para comparar señales',[1,2,3]); ff=st.checkbox('Activar Feedforward en el banco',value=True)
        bank=cached_simulate(Config(noise_cm=sigma,seed=int(seed),median_window=window),ff)
        data=pd.DataFrame({'t_s':bank.t_s,'sp_cm':bank[f'c{cell}_sp_cm'],'real_cm':bank[f'c{cell}_h_cm'],
            'medido_cm':bank[f'c{cell}_measured_cm'],'filtrado_cm':bank[f'c{cell}_pv_cm']})
    fig=go.Figure()
    for key,label in [('real_cm','Nivel real simulado'),('medido_cm','Medición con ruido'),('filtrado_cm','Mediana causal'),('sp_cm','SP')]:
        fig.add_trace(go.Scatter(x=data.t_s,y=data[key],name=label,line=dict(dash='dash' if key=='sp_cm' else 'solid')))
    chart(fig,'Señales simultáneas')
    errors=go.Figure(); metrics=[]
    for key,label in [('real_cm','Real'),('medido_cm','Medido'),('filtrado_cm','Filtrado')]:
        data['error_'+key]=data.sp_cm-data[key]
        errors.add_trace(go.Scatter(x=data.t_s,y=data['error_'+key],name='Error '+label))
        metrics.append({'Señal':label,'IAE_cm_s':iae(data.t_s,data.sp_cm,data[key])})
    chart(errors,'Error SP − señal',y='Error (cm)'); st.dataframe(metrics,hide_index=True)
    st.info('Mediana de las últimas N muestras, incluida la actual, con relleno inicial a 25 cm. Para N=10, la mediana de un número par de muestras promedia los dos valores centrales. Es causal. No se afirma equivalencia exacta con medfilt1 de MATLAB ni con sus convenciones de bordes.')
    st.caption('El filtro atenúa picos y también añade retraso: puede reducir el error causado por ruido y aumentar el error de seguimiento. La dirección del cambio de IAE se calcula, no se presupone.')
    tagged=provenance_export(data,PROVENANCES[0],'Filtro')
    csv_button(tagged,'Descargar señales y errores','filtrado.csv'); remember('filtrado',tagged,PROVENANCES[0],{'window':window,'noise_sigma_cm':sigma,'seed':seed})

def export_results():
    st.header('Resultados, parámetros y exportación reproducible')
    verdict=(ROOT/'docs/DICTAMEN_REPLICACION.md').read_text(encoding='utf-8')
    with st.expander('Validación para el docente: alcance de la réplica'):
        st.markdown(verdict)
    st.download_button('Descargar dictamen de replicación',verdict,'DICTAMEN_REPLICACION.md','text/markdown')
    st.caption('Los datos propios y ajustes se conservan en la sesión del navegador. Exporte antes de cerrar; no hay base de datos ni almacenamiento permanente de mediciones en el servidor.')
    exports=st.session_state.get('exports',{})
    calibrations=st.session_state.get('calibrations',{}); identified=st.session_state.get('identified',{}); tuned=st.session_state.get('tuned',{})
    settings={'calibrations':calibrations,'identified':identified,'tuned':tuned,'source_reference':SOURCE,'schema_version':2}
    st.json(settings,expanded=False)
    settings_json=json.dumps(settings,ensure_ascii=False,indent=2)
    st.download_button('Descargar sesión metodológica JSON',settings_json,'sesion_metodologica.json','application/json')
    uploaded=st.file_uploader('Restaurar ajustes JSON exportados por esta aplicación',type='json',key='session_import')
    if uploaded is not None and st.button('Restaurar ajustes de sesión'):
        obj=json.load(uploaded)
        if obj.get('schema_version')!=2: raise ValueError('Versión de sesión incompatible')
        # Solo claves numéricas y parámetros de instrumentos conocidos; no se ejecuta contenido.
        for tag,fit in obj.get('calibrations',{}).items():
            if tag.split(':')[0] not in list(PUMP_SLOPES)+list(LEVEL_FITS)+['FIC-1','FIC-2','FIC-3']: raise ValueError('Instrumento desconocido')
            if not np.isfinite([fit['slope'],fit['intercept']]).all() or fit['slope']==0: raise ValueError('Ajuste inválido')
        for item in obj.get('identified',{}).values():
            if not np.isfinite([item['kprime'],item['theta_s']]).all() or item['kprime']>=0 or item['theta_s']<1: raise ValueError('Identificación inválida')
        for item in obj.get('tuned',{}).values():
            if not np.isfinite([item['kc'],item['ti']]).all() or item['kc']>=0 or item['ti']<=0: raise ValueError('PI inválido')
        st.session_state['calibrations']=obj.get('calibrations',{})
        st.session_state['identified']={int(k):v for k,v in obj.get('identified',{}).items() if int(k) in (1,2,3)}
        st.session_state['tuned']={int(k):v for k,v in obj.get('tuned',{}).items() if int(k) in (1,2,3)}
        st.success('Ajustes restaurados. Las observaciones CSV se importan en sus módulos correspondientes.')
    buffer=BytesIO(); manifest=[]
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('sesion_metodologica.json',settings_json)
        for name,item in exports.items():
            frame=item['data'].copy(); frame['source']=item['source']; frame['reference']=SOURCE
            z.writestr(name+'.csv',frame.to_csv(index=False))
            manifest.append({'file':name+'.csv','source':item['source'],'metadata':item['metadata']})
        z.writestr('procedencia.json',json.dumps(manifest,ensure_ascii=False,indent=2,default=str))
    if manifest: st.dataframe(pd.DataFrame([{'archivo':x['file'],'procedencia':x['source']} for x in manifest]),hide_index=True,use_container_width=True)
    else: st.info('Todavía no guardó datos metodológicos en esta sesión. Los módulos con cálculos automáticos registran sus resultados al visitarlos; calibraciones e identificación requieren pulsar Guardar.')
    st.download_button('Descargar paquete de resultados de esta sesión',buffer.getvalue(),'resultados_metodologicos.zip','application/zip')
    st.markdown((ROOT/'docs/METODOLOGIA.md').read_text(encoding='utf-8'))

def render(module):
    funcs={'Calibración':calibration,'Identificación':identification,'Sintonización SIMC':tuning,
           'Modelos matemáticos':mathematical_models,'Instrumentación PLC':instrumentation,
           'Procedimiento guiado':procedure,'Comparación experimental':experimental_comparison,
           'Filtrado':filtering,'Resultados y exportación':export_results}
    if module in funcs: error_boundary(funcs[module])
