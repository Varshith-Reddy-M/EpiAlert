from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def test_raw_and_processed_exist():
    assert (ROOT/'data/raw/ILINet.csv').exists()
    assert (ROOT/'data/processed/analysis_input.csv').exists()
def test_no_duplicate_time_keys():
    d=pd.read_csv(ROOT/'data/processed/analysis_input.csv')
    assert d.duplicated(['REGION','YEAR','WEEK']).sum()==0
def test_missing_not_zero():
    d=pd.read_csv(ROOT/'data/processed/analysis_input.csv')
    assert d.loc[d.SOURCE_STATUS=='UNAVAILABLE','ILITOTAL'].isna().all()
def test_alert_logic():
    d=pd.read_csv(ROOT/'results/epialert_results.csv')
    assert (d.ALERT==(d.CUSUM_SIGNAL|d.EWMA_SIGNAL)).all()
    assert d.loc[d.ALERT,'ILI_RATE_PCT'].notna().all()
def test_rate_bounds():
    d=pd.read_csv(ROOT/'data/processed/analysis_input.csv')
    r=d.ILI_RATE_PCT.dropna()
    assert (r>=0).all() and (r<=100).all()
