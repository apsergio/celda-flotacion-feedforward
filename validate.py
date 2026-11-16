from pathlib import Path
import json
from model import Config, compare

folder=Path('validation'); folder.mkdir(exist_ok=True)
data=compare(Config())
data.to_csv(folder/'default_comparison.csv',index=False)
final=data.groupby('mode').tail(1)
report={'scenario':'Config()','max_volume_residual_L':float(data.balance_error_L.abs().max()),
        'final_iae_cm_s':{row['mode']:[row[f'c{i}_iae_cm_s'] for i in range(1,4)] for _,row in final.iterrows()},
        'experimental_validation':False}
(folder/'metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
