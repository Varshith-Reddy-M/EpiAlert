# EpiAlert — CDC FluView ILINet

EpiAlert is a transparent statistical surveillance project using CDC FluView ILINet data to identify unusual weekly influenza-like illness activity with CUSUM and EWMA.

## Important interpretation
The system detects **statistically unusual ILI surveillance activity**. It does not confirm influenza infection or declare an outbreak.

## Run

```bash
python scripts/run_all.py
streamlit run app.py
```

## Project structure

- `data/raw/` — original CDC export
- `data/processed/` — cleaned analysis input
- `scripts/` — preprocessing and detector calculations
- `results/` — reproducible outputs
- `docs/` — method, architecture, data dictionary and reproducibility notes
- `paper/` — manuscript-ready material
- `app.py` — dashboard
