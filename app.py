from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from model import Config, compare, KC, TI, KFF
from dataclasses import asdict
from ui_modules import MODULES, render, remember
from presentation import install_visual_theme, COLORS

st.set_page_config(page_title='Flotation Lab | Control de nivel',page_icon='🫧',layout='wide')
install_visual_theme()
st.caption('LABORATORIO VIRTUAL · METHODSX 102081 · 2023')
st.title('Banco de flotación')
st.write('Control de nivel con bombas peristálticas · Feedback y Feedforward')
st.caption('● Azul: Feedback   ·   ● Verde agua: Feedback + Feedforward   ·   ● Ámbar: consigna. Las curvas también se identifican por nombre y tipo de línea.')
with st.sidebar:
    navigation=st.radio('Módulo',MODULES,key='navigation')
    st.caption('Versión 2 · calibrar → identificar → sintonizar → controlar')
if navigation not in ('Proceso','Ensayos Feedback','Ensayos Feedforward'):
    render(navigation)
    st.stop()
with st.sidebar:
    st.header('Experimento')
    mode=st.radio('Estrategia visible',['FB','FB+FF'],index=0 if navigation=='Ensayos Feedback' else 1,key='visible_strategy_'+navigation)
    duration=st.slider('Duración (s)',120,1800,900,60)
    sp=tuple(st.number_input(f'SP celda {i+1} (cm)',5.,38.,25.,.5) for i in range(3))
    st.subheader('Perturbación P-4')
    feed=st.slider('Alimentación inicial (L/min)',5.,75.,45.)
    disturbance=st.slider('Cambio de alimentación (L/min)',-20.,20.,8.)
    at=st.slider('Aplicar perturbación en (s)',0,duration, min(180,duration))
    st.subheader('Escalón de consigna')
    step=tuple(st.number_input(f'ΔSP celda {i+1} (cm)',-3.,3.,1. if i==0 else 0.,.5) for i in range(3))
    step_at=st.slider('Aplicar ΔSP en (s)',0,duration,min(450,duration))
    with st.expander('Modelo y supuestos'):
        gain=st.selectbox('Ganancia',['published','geometric','identified'],format_func=lambda x:{'published':'Tabla 2: parámetros publicados','geometric':'Geometría publicada: área 900 cm²','identified':'Identificación guardada por usuario'}[x])
        ff_mode=st.selectbox('Interpretación Feedforward',['literal','reference'],format_func=lambda x:'Ecs. 7–8: diferencia entre muestras' if x=='literal' else 'Variante: diferencia respecto al caudal inicial')
        qmax=st.number_input('Límite de caudal supuesto (L/min)',50.,200.,100.)
        conc=st.number_input('Concentrado por celda supuesto (L/min)',0.,1.,.2,.1)
        window=st.slider('Mediana causal (muestras)',1,10,10)
        noise=st.slider('Ruido de sensor σ (cm)',0.,.3,0.,.01)
        tuning_mode=st.selectbox('Controladores PI',['Finales publicados Tabla 2','Alternativas SIMC guardadas'])
    st.caption('Los caudales máximos y el concentrado son supuestos editables. El artículo no proporciona su ley dinámica.')

identified=st.session_state.get('identified',{})
if gain=='identified' and any(i not in identified for i in (1,2,3)):
    st.warning('Para este modelo, guarde una identificación de cada una de las tres celdas. Elija Tabla 2 o Geometría para ejecutar los modelos publicados.'); st.stop()
gains=tuple(identified[i]['kprime'] for i in (1,2,3)) if gain=='identified' else (-.001018,)*3
delays=tuple(identified[i]['delay_applied_s'] for i in (1,2,3)) if gain=='identified' else (7,6,3)
kc=list(KC); ti=list(TI)
if tuning_mode!='Finales publicados Tabla 2':
    custom=st.session_state.get('tuned',{})
    if not custom: st.warning('Primero guarde una alternativa en Sintonización SIMC.'); st.stop()
    for i,item in custom.items(): kc[i-1]=item['kc']; ti[i-1]=item['ti']
    st.info('Se aplican los PI alternativos guardados. Las celdas sin alternativa conservan sus parámetros finales publicados.')
if gain=='published': st.caption('Planta identificada de Tabla 2. Su almacenamiento efectivo conserva el balance matemático, pero no representa el volumen geométrico real. Consulte Modelos matemáticos.')
elif gain=='identified': st.caption('Parámetros de planta procedentes de la identificación guardada en esta sesión; no se atribuyen automáticamente al artículo.')
c=Config(duration=duration,sp=sp,feed=feed,disturbance=disturbance,disturbance_at=at,
         setpoint_step=step,setpoint_at=step_at,qmax=qmax,concentrate=conc,gain_mode=gain,
         ff_mode=ff_mode,median_window=window,kprime=gains,delays=delays,kc=tuple(kc),ti=tuple(ti),noise_cm=noise)
@st.cache_data
def results(c): return compare(c)
try: data=results(c)
except ValueError as e: st.error(str(e)); st.stop()
remember('banco_control',data,'Sintéticos de simulación del banco',asdict(c))
signature=repr(c)
if st.session_state.get('signature')!=signature:
    st.session_state.update(signature=signature,cursor=0,running=False)
for key,default in [('cursor',0),('running',False)]:
    if key not in st.session_state: st.session_state[key]=default
a,b,d=st.columns(3)
if a.button('▶ Iniciar',use_container_width=True): st.session_state.running=True
if b.button('Ⅱ Pausar',use_container_width=True): st.session_state.running=False
if d.button('↺ Reiniciar',use_container_width=True): st.session_state.update(cursor=0,running=False)
st.caption('Reproducción de un experimento calculado a 1 s. Ambas estrategias usan el mismo escenario; la recirculación genera perturbaciones internas distintas.')

def diagram(row):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 340"><defs><linearGradient id="water" x2="0" y2="1"><stop stop-color="#35D6BB" stop-opacity=".9"/><stop offset="1" stop-color="#198FAD"/></linearGradient></defs><rect width="1000" height="340" rx="18" fill="#102137"/><g fill="#EDF3FC" font-family="Arial,sans-serif">']
    tank_fill=176*min(max(row.tank_L/130,0),1)
    parts.append(f'<rect x="24" y="90" width="130" height="180" rx="8" fill="#0D1B2E" stroke="#7FA9F5"/><rect x="26" y="{268-tank_fill}" width="126" height="{tank_fill}" rx="5" fill="url(#water)"/><text x="40" y="65">T-1 · 130 L</text><text x="40" y="190">{row.tank_L:.1f} L</text>')
    parts.append('<text x="35" y="35" fill="#7cb6c6">Aire: 47 L/min/celda (constante)</text>')
    for i,x in enumerate([250,500,750]):
        h=row[f'c{i+1}_h_cm']; water=160*h/45
        target=268-160*row[f'c{i+1}_sp_cm']/45
        parts.append(f'<path d="M{x} 90 V270 H{x+150} V90" fill="#0D1B2E" stroke="#7FA9F5" stroke-width="3"/><rect x="{x+2}" y="{268-water}" width="146" height="{water}" fill="url(#water)"/><path d="M{x+5} {target} H{x+145}" stroke="#FFC76A" stroke-width="2" stroke-dasharray="6 4"/><text x="{x}" y="58">C-{i+1} · LI-{i+1}</text><text x="{x+12}" y="240">{h:.2f} cm</text><text x="{x}" y="295">P-{i+1}: {row[f"c{i+1}_q_L_min"]:.1f} L/min</text>')
        if i<2: parts.append(f'<path d="M{x+150} 245 H{x+175} V135 H{x+250}" fill="none" stroke="#35D6BB" stroke-width="4"/><text x="{x+218}" y="125">→</text>')
        parts.append(f'<circle cx="{x+170}" cy="245" r="13" fill="#102536" stroke="#31d3b1" stroke-width="3"/><path d="M{x+163} 245 l12 -6 v12 z" fill="#31d3b1"/>')
        parts.append(f'<path d="M{x+145} 100 V78 H90" fill="none" stroke="#e9b85c" stroke-width="2"/>')
    parts.append('<path d="M900 245 H960 V320 H90 V270" fill="none" stroke="#35D6BB" stroke-width="4"/><path d="M154 180 H200 V135 H250" fill="none" stroke="#35D6BB" stroke-width="4"/><circle cx="200" cy="180" r="13" fill="#102137" stroke="#35D6BB" stroke-width="3"/><text x="390" y="338">Relaves C-3 → T-1 · retorno cerrado</text><text x="380" y="25" fill="#FFC76A">Concentrados C-1/2/3 → T-1</text>')
    parts.append(f'<text x="165" y="210">P-4</text><text x="165" y="230">{row.feed_L_min:.1f}</text></g></svg>')
    return ''.join(parts)

@st.fragment(run_every=2 if st.session_state.running else None)
def playback():
    if st.session_state.running:
        st.session_state.cursor=min(duration,st.session_state.cursor+20)
        if st.session_state.cursor==duration: st.session_state.running=False
    cursor=st.session_state.cursor
    selected=data[data['mode']==mode].iloc[cursor]
    st.progress(cursor/duration,text=f'Tiempo simulado: {cursor} / {duration} s · {mode}')
    st.markdown(diagram(selected),unsafe_allow_html=True)
    cols=st.columns(3)
    for i,col in enumerate(cols):
        col.metric(f'Celda {i+1} · PV',f'{selected[f"c{i+1}_pv_cm"]:.2f} cm',f'SP {selected[f"c{i+1}_sp_cm"]:.1f} cm',delta_color='off')
        col.caption(f'Orden P-{i+1}: {selected[f"c{i+1}_u_L_min"]:.2f} L/min · FF: {selected[f"c{i+1}_ff_L_min"]:+.2f} L/min')
    for i in range(3):
        fig=go.Figure()
        for strategy,color in [('FB',COLORS['FB']),('FB+FF',COLORS['FB+FF'])]:
            frame=data[(data['mode']==strategy)&(data.t_s<=cursor)]
            fig.add_trace(go.Scatter(x=frame.t_s,y=frame[f'c{i+1}_pv_cm'],name=strategy,line_color=color))
        frame=data[(data['mode']==mode)&(data.t_s<=cursor)]
        fig.add_trace(go.Scatter(x=frame.t_s,y=frame[f'c{i+1}_sp_cm'],name='SP',line=dict(color=COLORS['SP'],dash='dash')))
        fig.update_layout(title=f'Celda {i+1} · nivel filtrado',xaxis_title='Tiempo (s)',yaxis_title='Nivel (cm)',height=280,margin=dict(t=50,b=40),template='flotation',legend_orientation='h')
        st.plotly_chart(fig,use_container_width=True,key=f'level{i}')
playback()
tab1,tab2,tab3=st.tabs(['Comparación final','Señales y descarga','Método y trazabilidad'])
with tab1:
    final=data.groupby('mode').tail(1).set_index('mode')
    table=[]
    for i in range(3):
        fb=final.loc['FB',f'c{i+1}_iae_cm_s']; ff=final.loc['FB+FF',f'c{i+1}_iae_cm_s']
        table.append({'Celda':i+1,'IAE FB (cm·s)':fb,'IAE FB+FF (cm·s)':ff,'Reducción (%)':100*(fb-ff)/fb if fb else 0})
    st.dataframe(table,hide_index=True,use_container_width=True)
    st.info('Resultados calculados, no datos experimentales. La fórmula literal de las Ecs. 7–8 no garantiza una mejora del IAE en este modelo. Una reducción negativa indica empeoramiento.')
with tab2:
    st.dataframe(data[data['mode']==mode],hide_index=True,use_container_width=True)
    st.download_button('Descargar ambos experimentos CSV',data.to_csv(index=False).encode('utf-8'),'comparacion.csv','text/csv')
    st.download_button('Descargar parámetros del escenario',signature,'escenario.txt')
    st.download_button('Descargar escenario reproducible JSON',__import__('json').dumps(asdict(c),ensure_ascii=False,indent=2),'escenario.json','application/json')
with tab3:
    st.markdown(Path('docs/METODOLOGIA.md').read_text(encoding='utf-8'))
