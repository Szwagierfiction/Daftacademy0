from fastapi import FastAPI, HTTPException, status
import aiosqlite

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
async def read_track(composer_name: str):
    cursor = await app.db_connection.execute(f'''
    SELECT Name FROM Tracks WHERE Tracks.Composer = "{composer_name}" ORDER BY Tracks.name''')
    #data = map(lambda x: x[0], await cursor.fetchall())
    data = await cursor.fetchall()
    if (len(data) == 0):
        raise HTTPException(detail={"error": f"{composer_name} nie istnieje"}, status_code=status.HTTP_404_NOT_FOUND)
    data = no_more_list(data)
    return data

"""import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""