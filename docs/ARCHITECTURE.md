# Transparent architecture

```text
ILINet.csv (raw CDC export)
        |
        v
01_prepare_data.py
        |
        v
analysis_input.csv
        |
        +-------------------+
        |                   |
        v                   v
02_cusum.py           03_ewma.py
        |                   |
        v                   v
cusum_results.csv     ewma_results.csv
        |                   |
        +---------+---------+
                  v
       04_generate_outputs.py
                  |
        +---------+---------+----------------+
        |                   |                |
        v                   v                v
 epialert_results.csv  alert_events.csv  current_alerts.csv
        |
        v
      app.py
```

Every statistical detector is implemented in a separate script so the calculation is visible and reproducible.
