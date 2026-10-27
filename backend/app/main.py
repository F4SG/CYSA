from datetime import datetime,timedelta,timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends,HTTPException,Query
from cysa.contracts import Timed
from app.auth import read_access,admin_access
from app.repository import Repository
from cysa_inventory.router import build_router

def create_app(repository=None):
    repo=repository or Repository()
    @asynccontextmanager
    async def lifespan(app):
        repo.ready()
        yield
    app=FastAPI(title='CYSA S1 — solo monitoreo',version='1.1.0',lifespan=lifespan)
    @app.get('/health',include_in_schema=False)
    def health():return {'status':'ok','activacion_planes':False}
    @app.get('/api/conteos',dependencies=[Depends(read_access)])
    def counts(desde:datetime|None=None,hasta:datetime|None=None,interseccion:str|None=None,
               carril:str|None=None,prueba:bool|None=None,limit:int=Query(200,ge=1,le=1000),offset:int=Query(0,ge=0)):
        end=hasta or datetime.now(timezone.utc);start=desde or end-timedelta(hours=1)
        try:start,end=Timed.utc(start),Timed.utc(end)
        except ValueError:raise HTTPException(422,'Fechas con zona horaria requeridas') from None
        if start>=end or end-start>timedelta(days=31):raise HTTPException(422,'Rango válido: mayor a 0 y hasta 31 días')
        rows=repo.counts(start,end,interseccion,carril,prueba,limit,offset)
        return {'items':rows,'limit':limit,'offset':offset,'desde':start,'hasta':end}
    @app.get('/api/estados',dependencies=[Depends(read_access)])
    def states():return {'items':repo.states()}
    app.include_router(build_router(repo,read_access,admin_access))
    return app
app=create_app()
