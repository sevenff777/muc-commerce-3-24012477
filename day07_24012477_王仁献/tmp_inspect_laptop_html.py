from app import app

client = app.test_client()
client.post('/login', data={'username': 'student', 'password': 'day07'}, follow_redirects=True)
resp = client.get('/dashboard?category=Laptop+%26+Accessory')
html = resp.get_data(as_text=True)
for idx, line in enumerate(html.splitlines()):
    if 'Laptop' in line or 'Accessory' in line or '&amp;' in line or 'selected' in line:
        print(idx+1, repr(line))
print('---SNIPPET---')
start = html.find('<select name="category"')
if start != -1:
    end = html.find('</select>', start)
    print(html[start:end+9])
