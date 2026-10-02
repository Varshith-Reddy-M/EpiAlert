from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
C=pd.read_csv(ROOT/'results/cusum_results.csv')
E=pd.read_csv(ROOT/'results/ewma_results.csv')
keys=['REGION','YEAR','WEEK']
df=C.merge(E[keys+['EWMA','EWMA_SIGNAL']],on=keys,how='left')
df['ALERT']=df['CUSUM_SIGNAL']|df['EWMA_SIGNAL']
df['STATUS']=np.select([df['CUSUM_SIGNAL']&df['EWMA_SIGNAL'],df['CUSUM_SIGNAL'],df['EWMA_SIGNAL']],["UNUSUAL ACTIVITY DETECTED","CUSUM SIGNAL","EWMA SIGNAL"],default="NORMAL")
df['DATA_STATUS']=np.where(df['ILI_RATE_PCT'].notna(),'OBSERVED','UNAVAILABLE')
cols=['REGION','YEAR','WEEK','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT','Z_SCORE','BASELINE_MEAN','BASELINE_SD','CUSUM','EWMA','CUSUM_SIGNAL','EWMA_SIGNAL','ALERT','STATUS','DATA_STATUS']
df[cols].to_csv(ROOT/'results/epialert_results.csv',index=False)
df[df.ALERT][cols].to_csv(ROOT/'results/alert_events.csv',index=False)
latest_year=int(df.YEAR.max()); latest_week=int(df[df.YEAR==latest_year].WEEK.max())
cur=df[(df.YEAR==latest_year)&(df.WEEK==latest_week)]
cur[cur.ALERT][cols].to_csv(ROOT/'results/current_alerts.csv',index=False)

# summary tables
summary=pd.DataFrame({
 'metric':['observations','regions','years','valid_detection_observations','alerts','cusum_signals','ewma_signals','both_signals','alert_rate_percent','latest_year','latest_week'],
 'value':[len(df),df.REGION.nunique(),df.YEAR.nunique(),int(df.ILI_RATE_PCT.notna().sum()),int(df.ALERT.sum()),int(df.CUSUM_SIGNAL.sum()),int(df.EWMA_SIGNAL.sum()),int((df.CUSUM_SIGNAL&df.EWMA_SIGNAL).sum()),100*df.ALERT.mean(),latest_year,latest_week]
})
summary.to_csv(ROOT/'results/overall_summary.csv',index=False)

y=df.groupby('YEAR').agg(observations=('ALERT','size'),valid=('ILI_RATE_PCT','count'),alerts=('ALERT','sum'),cusum=('CUSUM_SIGNAL','sum'),ewma=('EWMA_SIGNAL','sum')).reset_index()
y['alert_rate_percent']=100*y.alerts/y.valid
y.to_csv(ROOT/'results/yearly_summary.csv',index=False)

# ranking tables
disease=None
r=df.groupby('REGION').agg(observations=('ALERT','size'),valid=('ILI_RATE_PCT','count'),alerts=('ALERT','sum'),total_ili=('ILITOTAL','sum')).reset_index()
r['alert_rate_percent']=100*r.alerts/r.valid
r.sort_values('alerts',ascending=False).to_csv(ROOT/'results/region_summary.csv',index=False)
cur_nonzero=cur[cur.ILITOTAL>0].sort_values('ILITOTAL',ascending=False)
cur_nonzero.to_csv(ROOT/'results/latest_week_activity.csv',index=False)

# validation checks
checks=[]
def chk(name,ok,detail): checks.append({'check':name,'passed':bool(ok),'detail':detail})
chk('No duplicate region-year-week',df.duplicated(keys).sum()==0,int(df.duplicated(keys).sum()))
chk('Signals only on observed data',bool(df.loc[df.ALERT,'ILI_RATE_PCT'].notna().all()),'All alerts have observed ILI rate')
chk('No negative counts',bool((df.ILITOTAL.dropna()>=0).all()),'')
chk('Rate between 0 and 100',bool(((df.ILI_RATE_PCT.dropna()>=0)&(df.ILI_RATE_PCT.dropna()<=100)).all()),'')
chk('Alert is union of detector signals',bool((df.ALERT==(df.CUSUM_SIGNAL|df.EWMA_SIGNAL)).all()),'')
chk('2026 latest week exists',latest_week>=1,latest_week)
pd.DataFrame(checks).to_csv(ROOT/'results/validation_checks.csv',index=False)
print(summary.to_string(index=False))
print(pd.DataFrame(checks).to_string(index=False))
