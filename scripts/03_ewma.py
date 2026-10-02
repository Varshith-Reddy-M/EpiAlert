from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
INP=ROOT/'data/processed/analysis_input.csv'
OUT=ROOT/'results/ewma_results.csv'
BASELINE_YEARS=3
WEEK_HALF_WINDOW=2
MIN_HISTORY=12
LAMBDA=0.20
THRESHOLD=2.70

def wrap_week(w):
    while w<1: w+=53
    while w>53: w-=53
    return w

df=pd.read_csv(INP) 
df['EWMA']=np.nan
df['EWMA_SIGNAL']=False
for region,g in df.groupby('REGION',sort=False):
    idx=g.index.to_numpy()
    years=g.YEAR.to_numpy(int) 
    weeks=g.WEEK.to_numpy(int) 
    vals=g.ILI_RATE_PCT.to_numpy(float) 
    valid=g.VALID_FOR_DETECTION.to_numpy(bool)
    lookup={(int(y),int(w)):float(vals[p]) for p,(y,w) in enumerate(zip(years,weeks)) if valid[p]}
    ewma=0.0
    for p,i in enumerate(idx):
        if not valid[p]: 
            ewma=0.0 
            continue
        hist=[]
        seen=set()
        for py in range(years[p]-BASELINE_YEARS,years[p]):
            for dw in range(-WEEK_HALF_WINDOW,WEEK_HALF_WINDOW+1):
                ww=wrap_week(int(weeks[p])+dw)
                key=(py,ww)
                if key in lookup and key not in seen: 
                    hist.append(lookup[key])
                    seen.add(key)
        if len(hist)<MIN_HISTORY: 
            ewma=0.0 
            continue
        a=np.log1p(np.asarray(hist,dtype=float))
        cur=np.log1p(vals[p])
        sd=float(a.std(ddof=1))
        z=0.0 if sd<=1e-12 else (cur-float(a.mean()))/sd
        if not np.isfinite(z): 
            ewma=0.0
            continue
        ewma=LAMBDA*z+(1-LAMBDA)*ewma
        signal=ewma>=THRESHOLD
        df.at[i,'EWMA']=ewma
        df.at[i,'EWMA_SIGNAL']=signal
        if signal: ewma=0.0
cols=['REGION','YEAR','WEEK','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT','EWMA','EWMA_SIGNAL']
df[cols].to_csv(OUT,index=False)
print('EWMA signals:',int(df.EWMA_SIGNAL.sum()))