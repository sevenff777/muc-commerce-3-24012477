from app import app

client = app.test_client()
client.post('/login', data={'username': 'student', 'password': 'day07'}, follow_redirects=True)
for category, expected_rate in [('Fashion', '15.5%'), ('Mobile Phone', '27.4%')]:
    resp = client.get('/dashboard?category=' + category)
    html = resp.get_data(as_text=True)
    selected = f'<option value="{category}" selected>' in html
    row_present = category in html and expected_rate in html
    print(category, resp.status_code, 'selected=', selected, 'row=', row_present)
