from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1] 
INP=ROOT/'data/processed/analysis_input.csv' 
OUT=ROOT/'results/cusum_results.csv'
BASELINE_YEARS=3
WEEK_HALF_WINDOW=2 
MIN_HISTORY=12
K=0.5
H=5.0

def wrap_week(w):
    while w<1: w+=53
    while w>53: w-=53
    return w

df=pd.read_csv(INP)
df['CUSUM']=np.nan
df['CUSUM_SIGNAL']=False 
df['Z_SCORE']=np.nan
df['BASELINE_MEAN']=np.nan 
df['BASELINE_SD']=np.nan
df['BASELINE_N']=0
for region,g in df.groupby('REGION',sort=False):
    idx=g.index.to_numpy()
    years=g.YEAR.to_numpy(int) 
    weeks=g.WEEK.to_numpy(int) 
    vals=g.ILI_RATE_PCT.to_numpy(float) 
    valid=g.VALID_FOR_DETECTION.to_numpy(bool)
    lookup={(int(y),int(w)):float(vals[p]) 
            for p,(y,w) in enumerate(zip(years,weeks)) 
            if valid[p]}
    cplus=0.0
    for p,i in enumerate(idx):
        if not valid[p]: 
            cplus=0.0
            continue
        hist=[]
        for py in range(years[p]-BASELINE_YEARS,years[p]):
            for dw in range(-WEEK_HALF_WINDOW,WEEK_HALF_WINDOW+1):
                key=(py,wrap_week(int(weeks[p])+dw))
                if key in lookup: 
                    hist.append(lookup[key])
        hist=list(dict.fromkeys((py,wrap_week(int(weeks[p])+dw),v) for py in range(years[p]-BASELINE_YEARS,years[p]) for dw in range(-WEEK_HALF_WINDOW,WEEK_HALF_WINDOW+1) if (py,wrap_week(int(weeks[p])+dw)) in lookup for v in [lookup[(py,wrap_week(int(weeks[p])+dw))]]))
        hist=[v for _,_,v in hist]
        if len(hist)<MIN_HISTORY: 
            cplus=0.0
            continue
        a=np.log1p(np.asarray(hist,dtype=float))
        cur=np.log1p(vals[p])
        mu=float(a.mean())
        sd=float(a.std(ddof=1)) 
        z=0.0 if sd<=1e-12 else (cur-mu)/sd
        if not np.isfinite(z): 
            cplus=0.0
            continue
        cplus=max(0.0,cplus+z-K) 
        signal=cplus>=H
        df.at[i,'Z_SCORE']=z 
        df.at[i,'BASELINE_MEAN']=mu 
        df.at[i,'BASELINE_SD']=sd
        df.at[i,'BASELINE_N']=len(hist) 
        df.at[i,'CUSUM']=cplus
        df.at[i,'CUSUM_SIGNAL']=signal
        if signal: cplus=0.0
cols=['REGION','YEAR','WEEK','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT','Z_SCORE','BASELINE_MEAN','BASELINE_SD','BASELINE_N','CUSUM','CUSUM_SIGNAL']
df[cols].to_csv(OUT,index=False)
print('CUSUM signals:',int(df.CUSUM_SIGNAL.sum()))