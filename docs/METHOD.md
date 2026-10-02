# EpiAlert FluView — Statistical Method

## Objective
EpiAlert is a statistical surveillance system that identifies unusually high weekly influenza-like illness (ILI) activity in CDC FluView ILINet data. An alert is a statistical early-warning signal and is **not confirmation of an influenza outbreak**.

## Unit of analysis
Each CDC `REGION` is treated as an independent chronological weekly series. Rows are ordered by `YEAR` and `WEEK`.

## Primary measurement
The primary surveillance measure is the ILI visit rate:

`ILI_RATE_PCT = ILITOTAL / TOTAL PATIENTS × 100`

`ILITOTAL` and `TOTAL PATIENTS` are retained for interpretation. Using the rate reduces distortion from changes in the number of participating reported patient visits.

## Missing values
Literal `X` values in the CDC export are converted to unavailable (`NaN`) for numeric processing. They are never converted to zero. Explicit zero values remain zero. A missing week is retained in the source-aligned table but does not enter detector calculations.

## Baseline
For each region, the baseline for week t is seasonal: it uses observations from the **previous 3 calendar years** within **MMWR week t ± 2 weeks**, excluding the current year. At least 12 valid historical observations are required. This design reduces predictable seasonal effects while retaining a local historical reference. The detector works on `log(1 + ILI_RATE_PCT)` and standardizes the current value using the seasonal historical mean and sample standard deviation.

`z_t = (log(1+x_t) - μ_t) / σ_t`

where `μ_t` and `σ_t` are calculated only from the seasonal historical reference window.

## CUSUM
Upper one-sided standardized CUSUM:

`C_t = max(0, C_(t-1) + z_t - k)`

with `k = 0.5` and signal threshold `h = 5.0`. The accumulator is reset after a signal.

## EWMA
Standardized EWMA:

`E_t = λ z_t + (1-λ) E_(t-1)`

with `λ = 0.20` and an upper signal threshold of `2.70`. The EWMA state is reset after a signal.

## Interpretation
- `NORMAL`: no detector crossed its threshold.
- `CUSUM SIGNAL`: CUSUM crossed its threshold.
- `EWMA SIGNAL`: EWMA crossed its threshold.
- `UNUSUAL ACTIVITY DETECTED`: both detectors signaled for the same observation.

These thresholds are project parameters, not CDC outbreak thresholds.
