"""Sistema visual compartido; sin cambios en las ecuaciones del simulador."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

COLORS={'background':'#08111F','surface':'#102137','text':'#EDF3FC',
        'FB':'#7FA9F5','FB+FF':'#35D6BB','SP':'#FFC76A',
        'real':'#7FA9F5','measured':'#F29CBC','filtered':'#35D6BB'}

def install_visual_theme():
    pio.templates['flotation']=go.layout.Template(layout=dict(
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#0D1B2E',
        font=dict(family='Arial, sans-serif',color=COLORS['text'],size=13),
        colorway=['#35D6BB','#7FA9F5','#FFC76A','#C4A2FF','#F29CBC','#75D4EF'],
        xaxis=dict(gridcolor='#22334A',zerolinecolor='#334760',showline=False),
        yaxis=dict(gridcolor='#22334A',zerolinecolor='#334760',showline=False),
        hoverlabel=dict(bgcolor='#172B44',font_color='#EDF3FC'),
        legend=dict(bgcolor='rgba(0,0,0,0)',font_size=12)))
    st.markdown('''<style>
    .stApp {background:radial-gradient(ellipse at 85% 0%,#13253E 0%,#08111F 55%)}
    .block-container {padding-top:2.2rem;padding-bottom:3rem;max-width:1440px}
    h1 {letter-spacing:-1.5px;font-weight:750!important}
    h2 {letter-spacing:-.6px}
    h3 {color:#C6D9F5}
    [data-testid="stSidebar"] {background:#0D1B2D;border-right:1px solid #223650}
    [data-testid="stMetric"] {background:linear-gradient(135deg,#152B45,#102137);
      border:1px solid #2B4563;border-top:3px solid #35D6BB;
      padding:18px;border-radius:14px;box-shadow:0 8px 22px #00000018}
    [data-testid="stMetricLabel"] {color:#C6D9F5}
    [data-testid="stMetricValue"] {color:#F5F8FF}
    [data-testid="stButton"] button,[data-testid="stDownloadButton"] button {
      border-radius:10px;border:1px solid #39516E;transition:border-color .15s}
    [data-testid="stButton"] button:hover,[data-testid="stDownloadButton"] button:hover {
      border-color:#35D6BB}
    [data-testid="stTabs"] [role="tablist"] {gap:8px;border-bottom:1px solid #263B55}
    [data-testid="stTabs"] [role="tab"] {border-radius:8px 8px 0 0;padding:10px 16px}
    [data-testid="stTabs"] [aria-selected="true"] {background:#163344;color:#5BE3CB}
    [data-testid="stExpander"] {border-color:#2B405D;border-radius:12px}
    </style>''',unsafe_allow_html=True)

def semantic_trace_color(name):
    name=str(name).lower()
    if name=='sp' or 'consigna' in name: return COLORS['SP']
    if 'fb+ff' in name or 'feedforward' in name: return COLORS['FB+FF']
    if name=='fb' or 'fb filtrado' in name: return COLORS['FB']
    if 'medición con ruido' in name or 'error medido' in name: return COLORS['measured']
    if 'nivel real' in name or 'error real' in name: return COLORS['real']
    if 'mediana' in name or 'error filtrado' in name: return COLORS['filtered']
    return None
