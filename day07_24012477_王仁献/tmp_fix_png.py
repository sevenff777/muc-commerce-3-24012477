from pathlib import Path
p = Path('screenshots/02_dashboard.png')
p.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 20)
print(p.exists(), p.stat().st_size)
