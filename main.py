from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import secrets

from fastapi import Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from hashlib import sha256
from fastapi.templating import Jinja2Templates

app = FastAPI()
# comment5
# Wyklad 1 - Zadanie 1
"""
@app.get('/')
def hello_world():
	return {"message": "Hello World during the coronavirus pandemic!"}
"""


# Wykład 1 - Zadanie 2
@app.get('/method')
def read_method(request: Request):
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {'method': request.method}


@app.post('/method')
def read_method(request: Request):
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {'method': request.method}


@app.put('/method')
def read_method(request: Request):
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {'method': request.method}


@app.delete('/method')
def read_method(request: Request):
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
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
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
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
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    p = Patients.find_patient_by_id(pk)
    if not p:
        return JSONResponse(status_code=204, content={})
    return p


# Wykład 3 - Zadanie 1
@app.get('/')
@app.post('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


#@app.get('/welcome')
#def welcome_world():
 #   return {"message": "Welcome during the coronavirus pandemic!"}


# Wykład 3 - Zadanie 2
security = HTTPBasic()


def session_token_func(username, password, secret_key):
    return sha256(bytes(f"{username}{password}{secret_key}", "utf-8")).hexdigest()


correctusername = 'trudnY'
correctpassword = 'PaC13Nt'
app.secret_key = "jfdjksf"

correct_session_token = session_token_func(correctusername, correctpassword, app.secret_key)
app.sessions = []

templates = Jinja2Templates(directory="./")

@app.get('/welcome')
def welcome_world(response: Response, request: Request, session_token: str = Cookie(None)):
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    response.set_cookie(key="session_token", value=session_token)
    return templates.TemplateResponse("welcome.html", {"request": request, "user" : correctusername})
    #return {"message": "Welcome during the coronavirus pandemic!"}

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, correctusername)
    is_correct_password = secrets.compare_digest(credentials.password, correctpassword)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    session_token = session_token_func(credentials.username, credentials.password, app.secret_key)

    if session_token not in app.sessions:
        app.sessions.append(session_token)

    return {"username": credentials.username, "password": credentials.password}

#@app.get("/login")
@app.post("/login")
def read_current_user(response: Response, userdata=Depends(get_current_username)):
    session_token = session_token_func(userdata['username'], userdata['password'], app.secret_key)
    response.set_cookie(key="session_token", value=session_token)
    return RedirectResponse(url='/welcome', status_code=status.HTTP_302_FOUND)

@app.post("/logout")
def logout(response: Response, session_token: str = Cookie(None)):
    if correct_session_token not in app.sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    app.sessions.pop()
    response.set_cookie(key="session_token", value="")
    return RedirectResponse(url='/')
"""
import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""