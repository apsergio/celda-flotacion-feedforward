"""Modelo educativo trazable a Quintanilla et al., MethodsX 102081 (2023)."""
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
import pandas as pd

KC = np.array([-62., -76., -85.])
TI = np.array([56., 30., 44.])
KFF = np.array([.8, .8, 1.])
DELAY = (7, 6, 3)

@dataclass
class Config:
    duration: int = 900
    sp: tuple = (25., 25., 25.)
    initial: tuple = (25., 25., 25.)
    feed: float = 45.
    disturbance: float = 8.
    disturbance_at: int = 180
    setpoint_at: int = 450
    setpoint_step: tuple = (1., 0., 0.)
    qmax: float = 100.
    concentrate: float = .2
    gain_mode: str = 'published'
    ff_mode: str = 'literal'
    median_window: int = 10
    tank_initial: float = 100.

class PI:
    def __init__(self, kc, ti, bias, limit):
        self.kc, self.ti, self.bias, self.limit = kc, ti, bias, limit
        self.integral = 0.

    def update(self, error, ff=0.):
        candidate = self.integral + self.kc / self.ti * error
        raw = self.bias + self.kc * error + candidate + ff
        # Integración condicional: no acumular error hacia una saturación.
        if (0 <= raw <= self.limit or (raw > self.limit and self.kc*error < 0)
                or (raw < 0 and self.kc*error > 0)):
            self.integral = candidate
        return float(np.clip(self.bias + self.kc*error + self.integral + ff, 0, self.limit))

def simulate(c=Config(), feedforward=False):
    if c.duration < 1 or c.qmax <= 0 or c.median_window < 1:
        raise ValueError('Duración, límite y ventana deben ser positivos')
    h = np.array(c.initial, dtype=float)
    if np.any(h < 0) or np.any(h > 45) or not 0 <= c.tank_initial <= 130:
        raise ValueError('Inventario inicial fuera de límites')
    # L/cm: área 900 cm² => .9 L/cm; Table 2 => 1/(60*.001018).
    capacity = 1/(60*.001018) if c.gain_mode == 'published' else .9
    volume = h*capacity
    tank = c.tank_initial
    base = np.maximum(c.feed - c.concentrate*np.arange(1,4), 0)
    controllers = [PI(KC[i],TI[i],base[i],c.qmax) for i in range(3)]
    queues = [deque([base[i]]*DELAY[i]) for i in range(3)]
    history = [deque([h[i]]*c.median_window,maxlen=c.median_window) for i in range(3)]
    previous = np.r_[c.feed,base[:2]]
    reference = previous.copy()
    iae = np.zeros(3)
    rows = []
    initial_total = tank + volume.sum()
    for t in range(c.duration+1):
        sp = np.array(c.sp) + (np.array(c.setpoint_step) if t >= c.setpoint_at else 0)
        pv = np.array([np.median(x) for x in history])
        out = np.array([q.popleft() for q in queues])
        feed = np.clip(c.feed + (c.disturbance if t >= c.disturbance_at else 0),0,c.qmax)
        # Límites de inventario: no extraer más líquido del disponible.
        feed = min(feed,tank*60)
        out = np.minimum(out,volume*60)
        conc = np.minimum(c.concentrate,np.maximum(volume*60-out,0))
        inlet = np.r_[feed,out[:2]]
        delta = inlet - (previous if c.ff_mode == 'literal' else reference)
        ff = KFF*delta if feedforward else np.zeros(3)
        command = np.array([controllers[i].update(sp[i]-pv[i],ff[i]) for i in range(3)])
        row = {'t_s':t,'mode':'FB+FF' if feedforward else 'FB','tank_L':tank,
               'feed_L_min':feed,'volume_total_L':tank+volume.sum(),
               'balance_error_L':tank+volume.sum()-initial_total}
        for i in range(3):
            for key,val in [('h_cm',h[i]),('pv_cm',pv[i]),('sp_cm',sp[i]),
                            ('q_L_min',out[i]),('u_L_min',command[i]),('ff_L_min',ff[i]),
                            ('conc_L_min',conc[i]),('iae_cm_s',iae[i])]:
                row[f'c{i+1}_{key}'] = val
        rows.append(row)
        if t == c.duration: break
        next_volume = volume+(inlet-out-conc)/60
        # Desborde de líquido al retorno de concentrados; supuesto explícito.
        spill = np.maximum(next_volume-45*capacity,0)
        volume = next_volume-spill
        tank += (out[2]+conc.sum()-feed)/60+spill.sum()
        if tank > 130+1e-8:
            raise ValueError('Tanque T-1 excede 130 L: reduzca inventario o perturbación')
        h = volume/capacity
        # IAE trapezoidal de nivel físico sin filtro, Eq.9.
        next_sp = np.array(c.sp)+(np.array(c.setpoint_step) if t+1 >= c.setpoint_at else 0)
        iae += .5*(np.abs(sp-np.array([row[f'c{i+1}_h_cm'] for i in range(3)]))+np.abs(next_sp-h))
        for i in range(3):
            queues[i].append(command[i]); history[i].append(h[i])
        previous = inlet.copy()
    return pd.DataFrame(rows)

def compare(c):
    return pd.concat([simulate(c,False),simulate(c,True)],ignore_index=True)
