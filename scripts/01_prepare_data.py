from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/ILINet.csv'
OUT=ROOT/'data/processed/analysis_input.csv'
QC=ROOT/'results/data_quality_summary.csv'

# CDC ILINet export contains a descriptive title row before the CSV header.
df=pd.read_csv(RAW, skiprows=1, dtype=str)
expected=['REGION TYPE','REGION','YEAR','WEEK','% WEIGHTED ILI','%UNWEIGHTED ILI','AGE 0-4','AGE 25-49','AGE 25-64','AGE 5-24','AGE 50-64','AGE 65','ILITOTAL','NUM. OF PROVIDERS','TOTAL PATIENTS']
assert df.columns.tolist()==expected, f'Unexpected columns: {df.columns.tolist()}'

# Keep only fields required for surveillance analysis plus provenance/context fields.
for c in ['YEAR','WEEK','ILITOTAL','NUM. OF PROVIDERS','TOTAL PATIENTS','%UNWEIGHTED ILI']:
    df[c]=pd.to_numeric(df[c],errors='coerce')

df['REGION']=df['REGION'].str.strip()
df['REGION TYPE']=df['REGION TYPE'].str.strip()
df=df.sort_values(['REGION','YEAR','WEEK']).reset_index(drop=True)

df['ILI_RATE_PCT']=np.where(df['TOTAL PATIENTS']>0, df['ILITOTAL']/df['TOTAL PATIENTS']*100, np.nan)
df['VALID_FOR_DETECTION']=df['ILITOTAL'].notna() & df['TOTAL PATIENTS'].notna() & (df['TOTAL PATIENTS']>0)
df['SOURCE_STATUS']=np.select([df['ILITOTAL'].isna() | df['TOTAL PATIENTS'].isna(), df['TOTAL PATIENTS'].notna() & (df['TOTAL PATIENTS']<=0)], ['UNAVAILABLE','INVALID_DENOMINATOR'], default='OBSERVED')

outcols=['REGION TYPE','REGION','YEAR','WEEK','ILITOTAL','TOTAL PATIENTS','NUM. OF PROVIDERS','%UNWEIGHTED ILI','ILI_RATE_PCT','VALID_FOR_DETECTION','SOURCE_STATUS']
df[outcols].to_csv(OUT,index=False)

summary=pd.DataFrame({
 'metric':['raw_rows','regions','years','min_year','max_year','missing_ili_total','missing_total_patients','zero_ili_total','valid_observations','duplicate_region_year_week','invalid_nonpositive_denominator'],
 'value':[
  len(df),df.REGION.nunique(),df.YEAR.nunique(),df.YEAR.min(),df.YEAR.max(),
  int(df.ILITOTAL.isna().sum()),int(df['TOTAL PATIENTS'].isna().sum()),int((df.ILITOTAL==0).sum()),int(df.VALID_FOR_DETECTION.sum()),
  int(df.duplicated(['REGION','YEAR','WEEK']).sum()),int(((df['TOTAL PATIENTS']<=0)&df['TOTAL PATIENTS'].notna()).sum())]
})
QC.parent.mkdir(exist_ok=True) 
summary.to_csv(QC,index=False)
print(summary.to_string(index=False))