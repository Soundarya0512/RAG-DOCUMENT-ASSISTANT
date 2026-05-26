from app.main import app 
from fastapi.testclient import TestClient 
client = TestClient(app) 
r = client.post('/query', json={'question': ''}) 
print('Status:', r.status_code) 
print('Body:', r.json()) 
