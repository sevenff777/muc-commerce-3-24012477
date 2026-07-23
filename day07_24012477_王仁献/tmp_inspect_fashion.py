from app import app
client = app.test_client()
client.post('/login', data={'username': 'student', 'password': 'day07'}, follow_redirects=True)
resp = client.get('/dashboard?category=Fashion')
html = resp.get_data(as_text=True)
for idx, line in enumerate(html.splitlines()):
    if 'Fashion' in line or '27.4%' in line or 'selected' in line:
        print(idx+1, line)
print('---RENDERED---')
print(html)
