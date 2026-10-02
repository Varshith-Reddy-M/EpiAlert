from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for s in ['01_prepare_data.py','02_cusum.py','03_ewma.py','04_generate_outputs.py']:
    print('\n###',s)
    subprocess.run([sys.executable,str(ROOT/'scripts'/s)],check=True)
print('\nPipeline completed successfully.')
