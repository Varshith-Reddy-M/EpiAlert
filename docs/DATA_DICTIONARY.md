# Data dictionary

| Field | Description | Role |
|---|---|---|
| REGION | CDC region/jurisdiction label | Analysis key |
| YEAR | Surveillance year | Time |
| WEEK | MMWR week | Time |
| ILITOTAL | Number of reported visits meeting the ILI definition | Count/context |
| TOTAL PATIENTS | Total reported patient visits | Denominator |
| NUM. OF PROVIDERS | Participating reporting providers | Context |
| %UNWEIGHTED ILI | CDC-provided unweighted ILI percentage | Context |
| ILI_RATE_PCT | ILITOTAL / TOTAL PATIENTS × 100 | Primary detector variable |
| VALID_FOR_DETECTION | Whether the denominator and ILI count are usable | Processing flag |
| SOURCE_STATUS | OBSERVED or UNAVAILABLE | Provenance |
