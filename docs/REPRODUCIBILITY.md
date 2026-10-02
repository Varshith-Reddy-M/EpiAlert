# Reproducibility checklist

1. Place the CDC `ILINet.csv` export in `data/raw/`.
2. Run `python scripts/run_all.py`.
3. Inspect `results/validation_checks.csv`; every check should pass.
4. Inspect `results/overall_summary.csv` and `results/yearly_summary.csv`.
5. Run `streamlit run app.py` to open the dashboard.

The raw export is preserved unchanged in `data/raw/`; all transformations are scripted.
