from fastapi import FastAPI

app = FastAPI()

# Wyklad 1 - Zadanie 1
@app.get('/')
def hello_world():
	return {"message": "Elo Hello World during the coronavirus pandemic!"}

@app.get('/hello/{name}')
def hello_name(name: str):
	return f"Hello {name}"

@app.get('/szwagier/{name}')
def szwagier_name(name: str):
	return f"Szwagier {name}"