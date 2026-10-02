# Project status — journal-ready build

## Completed
- Raw CDC ILINet export preserved unchanged.
- Only `ILINet.csv` retained; the other three ZIP files are excluded.
- Data dictionary and scripted preprocessing completed.
- `X` values treated as unavailable, not zero.
- Explicit zeros retained.
- Primary metric: ILI rate among reported patient visits.
- Seasonal baseline: previous 3 years, same MMWR week ±2 weeks, minimum 12 valid observations.
- CUSUM and EWMA implemented as separate transparent scripts.
- Detector parameters documented.
- Combined output and alert-event files generated.
- Dashboard implemented.
- Automated validation tests added.
- Parameter sensitivity analysis completed.
- Rolling-baseline comparison completed.
- External contextual comparison against CDC Week 37 2026 and Week 5 2025 reports documented.
- Manuscript draft and figures generated.

## Current headline results
- 45,138 observations
- 55 regions
- 2010–2026
- 44,297 valid detector observations
- 772 unavailable observations
- 2,820 combined alerts
- 2,711 CUSUM signals
- 402 EWMA signals
- 293 both-method signals
- 6.25% alert rate among valid observations

## Important interpretation
An EpiAlert signal means statistically unusual ILI surveillance activity relative to the seasonal reference. It is not confirmation of influenza infection or an outbreak.
