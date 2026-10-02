import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
ROOT=Path(__file__).resolve().parent
R=ROOT/'results'
st.set_page_config(page_title='EpiAlert — FluView',page_icon='📈',layout='wide')
@st.cache_data
def load():
  return pd.read_csv(R/'epialert_results.csv')
df=load()
df['DATE_KEY']=df.YEAR.astype(str)+'-W'+df.WEEK.astype(str).str.zfill(2)
latest_year=int(df.YEAR.max())
latest_week=int(df[df.YEAR==latest_year].WEEK.max())
cur=df[(df.YEAR==latest_year)&(df.WEEK==latest_week)]
st.sidebar.title('EpiAlert')
st.sidebar.caption('CDC FluView ILINet statistical surveillance')
page=st.sidebar.radio('Navigate',['Overview','Week Explorer','Activity Trends','Region Detail','Method'])
st.sidebar.caption(f'Data: {int(df.YEAR.min())}–{latest_year} • {df.REGION.nunique()} regions')
def kpi(label,val): st.metric(label, f'{val:,}' if isinstance(val,(int,float)) else val)
if page=='Overview':
 st.title('EpiAlert — ILI Surveillance Overview')
 st.caption(f'Latest available surveillance period: MMWR Week {latest_week}, {latest_year}')
 a=cur.ALERT.sum()
 active=(cur.ILITOTAL.fillna(0)>0).sum()
 total=cur.ILITOTAL.sum(skipna=True)
 c=st.columns(4)
 with c[0]: kpi('Reported ILI visits',int(total))
 with c[1]: kpi('Active regions',int(active))
 with c[2]: kpi('Current alerts',int(a))
 with c[3]: kpi('Regions with alerts',int(cur.loc[cur.ALERT,'REGION'].nunique()))
 st.subheader('Current alerts')
 alerts=cur[cur.ALERT].sort_values(['STATUS','ILITOTAL'],ascending=[True,False])
 st.dataframe(alerts[['REGION','WEEK','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT','CUSUM','EWMA','STATUS']],use_container_width=True,hide_index=True)
 st.subheader('Highest current ILI activity')
 st.dataframe(cur[cur.ILITOTAL>0].sort_values('ILITOTAL',ascending=False)[['REGION','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT']],use_container_width=True,hide_index=True)
 st.info('An alert indicates statistically unusual ILI surveillance activity relative to the recent history of the same region. It is not confirmation of an influenza outbreak.')
elif page=='Week Explorer':
 st.title('Week Explorer')
 years=sorted(df.YEAR.unique(),reverse=True)
 y=st.selectbox('Year',years,index=0)
 weeks=sorted(df.loc[df.YEAR==y,'WEEK'].unique(),reverse=True)
 w=st.selectbox('MMWR Week',weeks,index=0)
 x=df[(df.YEAR==y)&(df.WEEK==w)]
 c=st.columns(3)
 c[0].metric('ILI visits',int(x.ILITOTAL.sum(skipna=True)))
 c[1].metric('Alerts',int(x.ALERT.sum()))
 c[2].metric('Observed regions',int(x.ILI_RATE_PCT.notna().sum()))
 st.dataframe(x.sort_values(['ALERT','ILITOTAL'],ascending=[False,False])[['REGION','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT','CUSUM','EWMA','STATUS']],use_container_width=True,hide_index=True)
elif page=='Activity Trends':
 st.title('Activity Trends')
 agg=df.groupby(['YEAR','WEEK'],as_index=False).agg(ILI_visits=('ILITOTAL','sum'),observed_regions=('ILI_RATE_PCT','count'),alerts=('ALERT','sum'))
 agg['period']=agg.YEAR.astype(str)+'-W'+agg.WEEK.astype(str).str.zfill(2)
 fig=px.line(agg,x='period',y='ILI_visits',title='Weekly reported ILI visits across regions')
 fig.update_xaxes(nticks=15); st.plotly_chart(fig,use_container_width=True)
 top=cur.sort_values('ILITOTAL',ascending=False).head(10)
 st.subheader(f'Top regions — Week {latest_week}, {latest_year}')
 st.bar_chart(top.set_index('REGION')['ILITOTAL'])
elif page=='Region Detail':
 st.title('Region Detail')
 region=st.selectbox('Region',sorted(df.REGION.unique()))
 x=df[df.REGION==region].sort_values(['YEAR','WEEK'])
 st.metric('Latest ILI visits', 'Unavailable' if pd.isna(x.iloc[-1].ILITOTAL) else f"{int(x.iloc[-1].ILITOTAL):,}")
 fig=px.line(x,x='DATE_KEY',y='ILITOTAL',title=f'{region} — reported ILI visits')
 st.plotly_chart(fig,use_container_width=True)
 fig2=px.line(x,x='DATE_KEY',y='ILI_RATE_PCT',title=f'{region} — ILI rate among reported patient visits')
 st.plotly_chart(fig2,use_container_width=True)
 st.dataframe(x.tail(52)[['YEAR','WEEK','ILITOTAL','TOTAL PATIENTS','ILI_RATE_PCT','CUSUM','EWMA','STATUS']],use_container_width=True,hide_index=True)
else:
 st.title('Method')
 st.markdown(open(ROOT/'docs/METHOD.md').read())
 st.markdown(open(ROOT/'docs/ARCHITECTURE.md').read())