from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DATA=pd.read_csv(ROOT/'data/processed/analysis_input.csv')
RES=pd.read_csv(ROOT/'results/epialert_results.csv')
FIG=ROOT/'figures'
FIG.mkdir(exist_ok=True)

def wrap(w):
    while w<1:w+=53
    while w>53:w-=53
    return w

def run_detector(baseline='seasonal', k=.5,h=5,lam=.2,eth=2.7):
    out=[]
    for region,g in DATA.groupby('REGION',sort=False):
        idx=g.index.to_numpy()
        y=g.YEAR.to_numpy(int)
        w=g.WEEK.to_numpy(int)
        x=g.ILI_RATE_PCT.to_numpy(float)
        v=g.VALID_FOR_DETECTION.to_numpy(bool)
        if baseline=='seasonal':
            lookup={(int(yy),int(ww)):float(x[p]) for p,(yy,ww) in enumerate(zip(y,w)) if v[p]}
        else: lookup=None
        c=e=0.
        valid_hist=[]
        for p,i in enumerate(idx):
            if not v[p]: 
                c=e=0.
                continue
            if baseline=='seasonal':
                hist=[] 
                seen=set()
                for py in range(y[p]-3,y[p]):
                    for dw in range(-2,3):
                        key=(py,wrap(int(w[p])+dw))
                        if key in lookup and key not in seen: 
                            hist.append(lookup[key]); seen.add(key)
            else:
                hist=valid_hist[-26:]
            if len(hist)<12:
                c=e=0. 
                valid_hist.append(x[p])
                continue
            a=np.log1p(np.asarray(hist)) 
            cur=np.log1p(x[p]) 
            sd=a.std(ddof=1) 
            z=0 if sd<=1e-12 else (cur-a.mean())/sd
            c=max(0,c+z-k) 
            cs=c>=h
            c=0 if cs else c
            e=lam*z+(1-lam)*e
            es=e>=eth
            e=0 if es else e
            out.append((region,int(y[p]),int(w[p]),bool(cs),bool(es)))
            valid_hist.append(x[p])
    return pd.DataFrame(out,columns=['REGION','YEAR','WEEK','CUSUM','EWMA'])

# parameter sensitivity
rows=[]
for k in [.25,.5,.75]:
 for h in [4,5,6]:
  z=run_detector(k=k,h=h,lam=.2,eth=2.7)
  rows.append({'detector':'CUSUM','k':k,'h':h,'lambda':np.nan,'threshold':h,'signals':int(z.CUSUM.sum())})
for lam in [.1,.2,.3,.4]:
 for th in [2.5,2.7,3.0]:
  z=run_detector(k=.5,h=5,lam=lam,eth=th)
  rows.append({'detector':'EWMA','k':np.nan,'h':np.nan,'lambda':lam,'threshold':th,'signals':int(z.EWMA.sum())})
sens=pd.DataFrame(rows) 
sens.to_csv(ROOT/'results/parameter_sensitivity.csv',index=False)

# baseline comparison
season=run_detector('seasonal')
rolling=run_detector('rolling')
sm=int((season.CUSUM|season.EWMA).sum()) 
rm=int((rolling.CUSUM|rolling.EWMA).sum())
b=pd.DataFrame([{'baseline':'Seasonal: prior 3 years, week ±2','cusum':int(season.CUSUM.sum()),'ewma':int(season.EWMA.sum()),'combined':sm}, {'baseline':'Rolling: prior 26 valid observations','cusum':int(rolling.CUSUM.sum()),'ewma':int(rolling.EWMA.sum()),'combined':rm}])
b.to_csv(ROOT/'results/baseline_comparison.csv',index=False)

# distribution and case-study tables
a=RES[RES.ALERT].copy()
a['case_bin']=pd.cut(a.ILITOTAL,[-1,0,5,25,100,500,1000,5000,1e9],labels=['0','1-5','6-25','26-100','101-500','501-1000','1001-5000','>5000'])
a.groupby('case_bin',observed=False).size().rename('alerts').reset_index().to_csv(ROOT/'results/alert_case_count_distribution.csv',index=False)
# four representative rows: latest CUSUM, latest both, EWMA-only, normal comparator in same region/week neighborhood
cases=[]
for label,sub in [('CUSUM signal',RES[RES.CUSUM_SIGNAL]),('EWMA signal',RES[RES.EWMA_SIGNAL & ~RES.CUSUM_SIGNAL]),('Both signals',RES[RES.CUSUM_SIGNAL & RES.EWMA_SIGNAL])]:
 if len(sub): 
    cases.append(dict(sub.sort_values(['YEAR','WEEK'],ascending=False).iloc[0],case=label))
# Add a normal observation from the same latest year
n=RES[(RES.YEAR==2026)&(~RES.ALERT)&RES.ILI_RATE_PCT.notna()].sort_values('ILI_RATE_PCT',ascending=False).iloc[0].to_dict() | {'case':'Normal comparator'}
pd.DataFrame(cases+[n]).to_csv(ROOT/'results/case_studies.csv',index=False)

# Figures
ys=RES.groupby('YEAR',as_index=False).agg(alerts=('ALERT','sum'),valid=('ILI_RATE_PCT','count'))
plt.figure(figsize=(8,4.5))
plt.plot(ys.YEAR,ys.alerts,marker='o')
plt.xlabel('Year')
plt.ylabel('Alerts')
plt.title('Annual EpiAlert signals')
plt.tight_layout()
plt.savefig(FIG/'annual_alerts.png',dpi=180)
plt.close()
cb=RES[RES.ALERT].groupby('STATUS').size().sort_values(ascending=False)
plt.figure(figsize=(6,4)); cb.plot(kind='bar'); plt.ylabel('Alert events')
plt.title('Alert type distribution')
plt.tight_layout()
plt.savefig(FIG/'alert_types.png',dpi=180)
plt.close()
latest=RES[(RES.YEAR==2026)&(RES.WEEK==37)&RES.ILI_RATE_PCT.notna()].sort_values('ILITOTAL',ascending=False).head(10)
plt.figure(figsize=(8,5))
plt.barh(latest.REGION.iloc[::-1],latest.ILITOTAL.iloc[::-1])
plt.xlabel('ILI visits')
plt.title('Top reported ILI activity — 2026 Week 37')
plt.tight_layout()
plt.savefig(FIG/'latest_week_top_regions.png',dpi=180)
plt.close()
# parameter sensitivity heatmaps as simple line plots
for det in ['CUSUM','EWMA']:
 sub=sens[sens.detector==det]
 plt.figure(figsize=(7,4.5))
 if det=='CUSUM':
  for k in sorted(sub.k.unique()):
   q=sub[sub.k==k].sort_values('h')
   plt.plot(q.h,q.signals,marker='o',label=f'k={k}')
  plt.xlabel('h')
  plt.ylabel('Signals')
  plt.title('CUSUM parameter sensitivity')
  plt.legend()
 else:
  for lam in sorted(sub['lambda'].unique()):
   q=sub[sub['lambda']==lam].sort_values('threshold')
   plt.plot(q.threshold,q.signals,marker='o',label=f'λ={lam}')
  plt.xlabel('Threshold')
  plt.ylabel('Signals')
  plt.title('EWMA parameter sensitivity')
  plt.legend()
 plt.tight_layout()
 plt.savefig(FIG/f'{det.lower()}_sensitivity.png',dpi=180)
 plt.close()

print('Sensitivity and figures generated.')
print(sens.to_string(index=False))
print(b.to_string(index=False))