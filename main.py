from fastapi import FastAPI, Request
# from fastapi.testclient import TestClient
from pydantic import BaseModel

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

# Wykład 1 - Zadanie 3
class Patient(BaseModel):
    name: str
    surename: str

class PatientsPopulation(object):
    count = 0

    @staticmethod
    def have_new_patient():
        __class__.count += 1

    @staticmethod
    def no_of_patients():
        return __class__.count


@app.post("/patient")
# request object is automagicaly casted by FastApi to 'Patient'
# (contribution of BaseModel)
def patient(request: Patient):
    PatientsPopulation.have_new_patient()
    return {"id": PatientsPopulation.no_of_patients(),
            "patient": {
                        "name": request.name,
                        "surename": request.surename
                        }
            }


@app.post('/patient')
def read_method(request: Request):
    return {'method': request.method}