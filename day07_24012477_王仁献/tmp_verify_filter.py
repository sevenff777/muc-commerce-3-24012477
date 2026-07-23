from app import app

client = app.test_client()
for category in ['Fashion', 'Mobile Phone']:
    response = client.get('/dashboard?category=' + category)
    html = response.get_data(as_text=True)
    print(category, response.status_code, 'selected' in html.lower(), 'category' in html.lower())
