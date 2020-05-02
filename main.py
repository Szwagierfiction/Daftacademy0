from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel
import aiosqlite
from fastapi.encoders import jsonable_encoder

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.db_connection = await aiosqlite.connect('chinook.db')

@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()

@app.get('/tracks')
async def read_track(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = aiosqlite.Row
    cursor = await app.db_connection.execute(f'''
    SELECT tracks.TrackId as TrackId, tracks.name as Name, tracks.albumid as AlbumId, tracks.MediaTypeId as MediaTypeId,
    tracks.GenreId as GenreId, tracks.Composer as Composer, tracks.Milliseconds as Milliseconds, tracks.Bytes as Bytes, 
    tracks.UnitPrice as UnitPrice FROM tracks WHERE TrackId >= {page*per_page}''')
    data = await cursor.fetchmany(per_page)
    return data

def no_more_list(data):
    data2 = []
    for i in data:
        data2.append(i[0])
    return data2

@app.get('/tracks/composers')
async def composer(composer_name: str):
    cursor = await app.db_connection.execute(f'''
    SELECT Name FROM Tracks WHERE Tracks.Composer = "{composer_name}" ORDER BY Tracks.name''')
    #data = map(lambda x: x[0], await cursor.fetchall())
    data = await cursor.fetchall()
    if (len(data) == 0):
        raise HTTPException(detail={"error": f"{composer_name} nie istnieje"}, status_code=status.HTTP_404_NOT_FOUND)
    data = no_more_list(data)
    return data

class Album(BaseModel):
    title: str
    artist_id: int

@app.post('/albums', status_code=201)
async def albums(request: Album):
    cursor = await app.db_connection.execute(f'''
    SELECT COUNT(*) FROM artists WHERE artists.ArtistId = {request.artist_id}''')
    existance = await cursor.fetchone()
    if (existance[0] == 0):
        raise HTTPException(detail={"error": f"Artysta o numerze {request.artist_id} nie istnieje"},
                            status_code=status.HTTP_404_NOT_FOUND)

    cursor = await app.db_connection.execute(f'''
    INSERT INTO albums (Title, ArtistId) VALUES("{request.title}", {request.artist_id});''')
    await app.db_connection.commit()

    cursor = await app.db_connection.execute(f'''
    SELECT AlbumId FROM albums WHERE Albums.Title = "{request.title}" ORDER BY AlbumId DESC LIMIT 1;''')
    albums = await cursor.fetchone()
    AlbumId = albums[0]
    return {
            "AlbumId": AlbumId,
            "Title": request.title,
            "ArtistId": request.artist_id
            }

@app.get('/albums/{album_id}')
async def get_album(request: Request, album_id: int):

    cursor = await app.db_connection.execute(f'''
    SELECT AlbumId, Title, ArtistId FROM albums WHERE albums.AlbumId = {album_id}''')
    album = await cursor.fetchone()

    return {
            "AlbumId": album[0],
            "Title": album[1],
            "ArtistId": album[2]
            }
# zad4
class Customer(BaseModel):
        company: str = None
        address: str = None
        city: str = None
        state: str = None
        country: str = None
        postalcode: str = None
        fax: str = None

        def __getitem__(self, key):
            return getattr(self, key)

        @staticmethod
        def translate(nazwa):
            if nazwa == "company":
                nazwa = "Company"
            if nazwa == "address":
                nazwa = "Address"
            if nazwa == "city":
                nazwa = "City"
            if nazwa == "state":
                nazwa = "State"
            if nazwa == "postalcode":
                nazwa = "PostalCode"
            if nazwa == "fax":
                nazwa = "Fax"
            return nazwa


@app.put('/customers/{customer_id}')
async def put_customers(request: Customer, customer_id: int):
    # 404
    cursor = await app.db_connection.execute(f'''
    SELECT COUNT(*) FROM customers WHERE customers.CustomerId = {customer_id}''')
    existance = await cursor.fetchone()
    if (existance[0] == 0):
        raise HTTPException(detail={"error": f"Klient o numerze {customer_id} nie istnieje"},
                            status_code=status.HTTP_404_NOT_FOUND)

    # update
    request = jsonable_encoder(request)
    sqlUpdate = []

    for idx in request:
        if request[idx] != None:
            sqlUpdate.append(f'''{Customer.translate(idx)} = "{request[idx]}"''')
    sql_text = "UPDATE customers SET " + ", ".join(sqlUpdate) + "WHERE customers.CustomerId = " + str(customer_id) + ";"
    cursor = await app.db_connection.execute(sql_text)
    await app.db_connection.commit()

    # dict
    cursor = await app.db_connection.execute(f'''
    SELECT * FROM customers WHERE customers.CustomerId = {customer_id}''')
    values = await cursor.fetchone()
    cursor = await app.db_connection.execute(f'''
    SELECT * FROM customers''')
    names = [description[0] for description in cursor.description]
    data = dict(zip(names, values))
    return data

def takeSecond(elem):
    return elem[1]

@app.get('/sales')
async def sales(category: str):

    if category not in ['customers', 'genres']:
        raise HTTPException(detail={"error": f'''Kategoria '{category}' nie istnieje'''},
                            status_code=status.HTTP_404_NOT_FOUND)

    if category == 'customers':
        valuesList = []
        valuesList.append((0,0))
        for i in range(59):
            cursor = await app.db_connection.execute(f'''
            SELECT SUM(CASE WHEN invoices.CustomerId = {i+1} THEN invoices.total ELSE 0 END) FROM invoices''')
            totalSum = await cursor.fetchone()
            totalSum = round(totalSum[0], 2)
            customerIdWithValue = (i+1, totalSum)
            valuesList.append(customerIdWithValue)
        valuesList.sort(key=takeSecond, reverse=True)
        valuesList.pop()

        # dict
        data = []
        for customerId, totalSum in valuesList:
            cursor = await app.db_connection.execute(f'''
                    SELECT Email, Phone FROM customers WHERE customers.CustomerId = {customerId}''')
            customerData = await cursor.fetchone()

            data.append({
                        "CustomerId": customerId,
                        "Email": customerData[0],
                        "Phone": customerData[1],
                        "Sum": totalSum
                        })

    if category == 'genres':
        valuesList = []
        valuesList.append((0,0))
        for i in range(24):
            cursor = await app.db_connection.execute(f'''
            SELECT COUNT(GenreId) FROM invoice_items JOIN tracks ON tracks.TrackId = invoice_items.TrackId 
            WHERE GenreId = {i+1}''')
            totalSum = await cursor.fetchone()
            totalSum = totalSum[0]
            genreIdWithValue = (i+1, totalSum)
            valuesList.append(genreIdWithValue)

        valuesList.sort(key=takeSecond, reverse=True)
        valuesList.pop()

        # dict
        data = []
        for genreId, totalSum in valuesList:
            cursor = await app.db_connection.execute(f'''
                            SELECT Name FROM genres WHERE genres.GenreId = {genreId}''')
            genreData = await cursor.fetchone()

            data.append({
                "Name": genreData[0],
                "Sum": totalSum
            })

    return data


import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)