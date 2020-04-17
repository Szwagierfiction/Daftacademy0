from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
# comment5
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
    Patients.have_new_patient(request)
    return {"id": Patients.no_of_patients(),
            "patient": {
                        "name": request.name,
                        "surename": request.surename
                        }
            }


# Wykład 1 - Zadanie 4
class PatientWithId(object):
    def __init__(self, patient, id):
        self.patient = patient
        self.id = id

class Patients(object):
    count = 0
    collectionById = {}
    collectionByName = {}

    @staticmethod
    def find_patient_by_id(id):
        if id in __class__.collectionById.keys():
            return __class__.collectionById[id]
        else:
            return None

    @staticmethod
    def find_patient_by_name(patient: Patient):
        key = patient.name + ";" + patient.surename
        if key in __class__.collectionByName.keys():
            return __class__.collectionByName[key]
        else:
            return None

    @staticmethod
    def have_new_patient(patient: Patient):
        if not __class__.find_patient_by_name(patient):
            p = PatientWithId(patient, __class__.count)
            __class__.collectionById[__class__.count] = p
            __class__.collectionByName[patient.name + ";" + patient.surename] = p
            __class__.count += 1


    @staticmethod
    def no_of_patients():
        return __class__.count

@app.get('/patient/{pk}')
def read_patient(pk: int):
    p = Patients.find_patient_by_id(pk)
    if not p:
        return JSONResponse(status_code=204, content={})
    return p