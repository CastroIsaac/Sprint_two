
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .database import init_db, seed_db, get_connection
from .logic import calcular_rateio, calcular_duracao_min, DEFAULT_MAINTENANCE
from .ai import ChargeOpsAI

app=FastAPI(title="EV ChargeOps", version="2.0")
ai=ChargeOpsAI()

class SessionIn(BaseModel):
    usuario_id:int
    carregador_id:int
    inicio:str
    fim:str
    energia_kwh:float=Field(gt=0)
    tarifa_kwh:float=Field(gt=0)

@app.on_event("startup")
def startup():
    init_db(); seed_db()

@app.get("/")
def index():
    return FileResponse(Path(__file__).resolve().parent.parent/"static"/"index.html")

@app.get("/api/health")
def health(): return {"status":"ok","sistema":"EV ChargeOps","versao":"Sprint 02"}

@app.get("/api/usuarios")
def usuarios():
    c=get_connection(); rows=c.execute("SELECT * FROM usuarios ORDER BY id").fetchall(); c.close()
    return [dict(r) for r in rows]

@app.get("/api/carregadores")
def carregadores():
    c=get_connection(); rows=c.execute("SELECT * FROM carregadores ORDER BY id").fetchall(); c.close()
    return [dict(r) for r in rows]

@app.get("/api/sessoes")
def sessoes():
    c=get_connection(); rows=c.execute("""SELECT s.*,u.nome usuario,c.modelo carregador
        FROM sessoes s JOIN usuarios u ON u.id=s.usuario_id JOIN carregadores c ON c.id=s.carregador_id
        ORDER BY s.id DESC""").fetchall(); c.close()
    return [dict(r) for r in rows]

@app.post("/api/sessoes")
def criar_sessao(data:SessionIn):
    rateio=calcular_rateio(data.energia_kwh,data.tarifa_kwh)
    c=get_connection()
    c.execute("""INSERT INTO sessoes(usuario_id,carregador_id,inicio,fim,energia_kwh,tarifa_kwh,custo_energia,taxa_manutencao,custo_total)
                 VALUES(?,?,?,?,?,?,?,?,?)""",
              (data.usuario_id,data.carregador_id,data.inicio,data.fim,data.energia_kwh,data.tarifa_kwh,
               rateio["custo_energia"],rateio["taxa_manutencao"],rateio["custo_total"]))
    c.commit(); sid=c.execute("SELECT last_insert_rowid()").fetchone()[0]; c.close()
    return {"id":sid,"duracao_min":calcular_duracao_min(data.inicio,data.fim),**rateio}

@app.get("/api/resumo")
def resumo():
    c=get_connection()
    row=c.execute("""SELECT COUNT(*) sessoes,COALESCE(SUM(energia_kwh),0) energia,
                            COALESCE(SUM(custo_total),0) faturamento,
                            COALESCE(AVG(energia_kwh),0) media
                     FROM sessoes""").fetchone()
    c.close()
    return {"sessoes":row["sessoes"],"energia_kwh":round(row["energia"],2),
            "faturamento":round(row["faturamento"],2),"media_kwh_sessao":round(row["media"],2)}

@app.get("/api/ia/treinar")
def treinar_ia(): return ai.treinar()

@app.get("/api/ia/diagnostico")
def diagnostico(): return ai.diagnostico()

@app.get("/api/ia/prever")
def prever(hora:int=18,duracao_min:float=90,tarifa_kwh:float=0.89):
    return {"previsao_energia_kwh":ai.prever(hora,duracao_min,tarifa_kwh),
            "entrada":{"hora":hora,"duracao_min":duracao_min,"tarifa_kwh":tarifa_kwh}}

@app.get("/docs-sprint2")
def docs_sprint2():
    return {"objetivo":"Protótipo funcional do EV ChargeOps","central":"sessões + consumo + rateio",
            "ia":"previsão + clusterização + detecção de anomalias",
            "banco":"SQLite para protótipo local; arquitetura mantém separação para migração futura ao PostgreSQL"}
