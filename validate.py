from pathlib import Path
import json
from model import Config, compare
from methodology import (PUBLISHED,simc,synthetic_identification,identify,filtering_demo,
    iae,geometry_audit,demo_calibration,PUMP_SLOPES,LEVEL_FITS,AIR_SLOPES,
    linear_fit,volume_to_flow,PROVENANCES,provenance_export)

folder=Path('validation'); folder.mkdir(exist_ok=True)
data=compare(Config())
data.to_csv(folder/'default_comparison.csv',index=False)
final=data.groupby('mode').tail(1)
report={'scenario':'Config()','max_volume_residual_L':float(data.balance_error_L.abs().max()),
        'final_iae_cm_s':{row['mode']:[row[f'c{i}_iae_cm_s'] for i in range(1,4)] for _,row in final.iterrows()},
        'experimental_validation':False}
(folder/'metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

method=folder/'methodology'; method.mkdir(exist_ok=True)
audit=[]
for _,r in PUBLISHED.iterrows():
    calculated=simc(r.kprime,r.theta_s,r.tau_c_s)
    audit.append({**r.to_dict(),'Kc_calculado':calculated['Kc'],'Ti_calculado_s':calculated['Ti_s']})
pd=__import__('pandas')
pd.DataFrame(audit).to_csv(method/'simc_audit.csv',index=False)
identified=[]
for cell in (1,2,3):
    trial=synthetic_identification(cell,noise=0.)
    provenance_export(trial,PROVENANCES[0],f'C-{cell}').to_csv(method/f'openloop_C{cell}.csv',index=False)
    result=identify(trial,60,150,20,30); result['cell']=cell
    identified.append(result)
pd.concat(identified,ignore_index=True).to_csv(method/'identified_noiseless.csv',index=False)
for instrument in list(PUMP_SLOPES)+list(LEVEL_FITS)+['FIC-1','FIC-2','FIC-3']:
    for direction in (('lectura','salida') if instrument.startswith('FIC') else ('lectura',)):
        calibration=demo_calibration(instrument,direction)
        if instrument in PUMP_SLOPES:
            calibration['q_L_min']=volume_to_flow(calibration.volume_L)
            fit=linear_fit(calibration.bits,calibration.q_L_min,True)
        elif instrument in LEVEL_FITS: fit=linear_fit(calibration.bits,calibration.h_cm)
        else: fit=linear_fit(calibration.bits,calibration.q_L_min,True)
        provenance_export(calibration,PROVENANCES[0],instrument,{'direction':direction,
            'slope_calculated':fit['slope'],'intercept_calculated':fit['intercept']}).to_csv(method/f'calibration_{instrument}_{direction}.csv',index=False)
signals=filtering_demo()
signals.to_csv(method/'filtering_signals.csv',index=False)
filter_metrics={key:iae(signals.t_s,signals.sp_cm,signals[key]) for key in ('real_cm','medido_cm','filtrado_cm')}
protocol=compare(Config(duration=900,feed=45.,disturbance=0.,initial=(29.,34.,33.),
    sp=(29.,34.,33.),setpoint_at=150,setpoint_step=(-1.,-1.,-1.),noise_cm=.03,tank_initial=60.))
provenance_export(protocol,PROVENANCES[0],'Protocolo inspirado Fig.14').to_csv(method/'fig14_protocol_simulated.csv',index=False)
summary={'geometry':geometry_audit(),'filtering_iae_cm_s':filter_metrics,
    'protocol_max_mass_residual_L':float(protocol.balance_error_L.abs().max()),
    'published_equation_transcription_checked':True,'experimental_series_validation':False,
    'digitalized_fig12_independent_repetitions_per_cell':1}
(method/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
