import urllib.request
import json
try:
    r = urllib.request.urlopen("http://127.0.0.1:8000/api/books/")
    data = json.loads(r.read())
    if data['results']:
        id = data['results'][0]['id']
        try:
            r2 = urllib.request.urlopen(f"http://127.0.0.1:8000/api/books/{id}/")
            print(r2.read().decode())
        except Exception as e:
            print(e.read().decode())
except Exception as e:
    print(e)
