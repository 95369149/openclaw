
import os
files = sorted(os.listdir('output'))
for f in files:
    if f.endswith('.png'):
        sz = os.path.getsize(f'output/{f}')/1024
        print(f"✓ {f}: {sz:.0f} KB")
