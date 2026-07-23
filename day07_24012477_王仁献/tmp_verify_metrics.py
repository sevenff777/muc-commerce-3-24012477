from pathlib import Path
from services.data_service import load_dashboard_data

data = load_dashboard_data(Path('.'))
for metric in data['metrics']:
    print(metric['label'], metric['value'], metric['note'])
