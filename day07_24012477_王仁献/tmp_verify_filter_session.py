from app import app

client = app.test_client()
response = client.post('/login', data={'username': 'student', 'password': 'day07'}, follow_redirects=True)
print('login', response.status_code)
for category in ['Fashion', 'Mobile Phone']:
    response = client.get('/dashboard?category=' + category)
    html = response.get_data(as_text=True)
    print(category, response.status_code, 'selected' in html.lower())
    print('Fashion' in html or 'Mobile Phone' in html)
