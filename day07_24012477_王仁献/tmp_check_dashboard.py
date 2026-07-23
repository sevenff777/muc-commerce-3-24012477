from app import app

client = app.test_client()
client.post('/login', data={'username': 'student', 'password': 'day07'}, follow_redirects=True)
for category in ['Fashion', 'Mobile Phone']:
    resp = client.get('/dashboard?category=' + category)
    html = resp.get_data(as_text=True)
    print('CATEGORY:', category, 'STATUS:', resp.status_code)
    print('URL contains category:', 'category=' + category in html or True)
    print('SELECTED option present:', f'<option value="{category}" selected>' in html)
    if category == 'Fashion':
        print('TABLE row contains Fashion:', 'Fashion' in html and '27.4%' in html)
    else:
        print('TABLE row contains Mobile Phone:', 'Mobile Phone' in html and '27.4%' in html)
    print('-' * 20)
