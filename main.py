from fastapi import FastAPI, Request

app = FastAPI()

# Wyklad 1 - Zadanie 1
@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}

# Wykład 1 - Zadanie 2
@app.get('/method')
def read_method(request: Request):
    return {'method': request.method}

@app.post('/method')
def read_method(request: Request):
    return {'method': request.method}

@app.put('/method')
def read_method(request: Request):
    return {'method': request.method}

@app.delete('/method')
def read_method(request: Request):
    return {'method': request.method}