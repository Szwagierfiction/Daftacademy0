from fastapi import FastAPI
import aiosqlite
import sqlite3

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.db_connection = await aiosqlite.connect('chinook.db')

@app.get('/tracks')
async def read_track(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = sqlite3.Row
    cursor = await app.db_connection.execute(f'''
    SELECT tracks.TrackId as TrackId, tracks.name as Name, tracks.albumid as AlbumId, tracks.MediaTypeId as MediaTypeId,
    tracks.GenreId as GenreId, tracks.Composer as Composer, tracks.Milliseconds as Milliseconds, tracks.Bytes as Bytes, 
    tracks.UnitPrice as UnitPrice FROM tracks WHERE TrackId >= {page}''')
    data = await cursor.fetchmany(per_page)
    return data

"""
import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""