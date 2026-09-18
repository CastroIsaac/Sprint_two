
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chargeops.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        apartamento TEXT NOT NULL,
        email TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS carregadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        status TEXT NOT NULL,
        localizacao TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        carregador_id INTEGER NOT NULL,
        inicio TEXT NOT NULL,
        fim TEXT NOT NULL,
        energia_kwh REAL NOT NULL,
        tarifa_kwh REAL NOT NULL,
        custo_energia REAL NOT NULL,
        taxa_manutencao REAL NOT NULL,
        custo_total REAL NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(carregador_id) REFERENCES carregadores(id)
    );
    """)
    conn.commit()
    conn.close()

def seed_db():
    conn=get_connection(); cur=conn.cursor()
    if cur.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        cur.executemany("INSERT INTO usuarios(nome,apartamento,email) VALUES(?,?,?)", [
            ("Ana Souza","Apto 101","ana@example.com"),
            ("Bruno Lima","Apto 202","bruno@example.com"),
            ("Carla Mendes","Apto 303","carla@example.com"),
            ("Diego Alves","Apto 404","diego@example.com"),
        ])
    if cur.execute("SELECT COUNT(*) FROM carregadores").fetchone()[0] == 0:
        cur.executemany("INSERT INTO carregadores(modelo,status,localizacao) VALUES(?,?,?)", [
            ("GoodWe HCA G2","disponível","Garagem A"),
            ("GoodWe HCA G2","ocupado","Garagem B"),
            ("GoodWe HCA G2","disponível","Garagem C"),
        ])
    if cur.execute("SELECT COUNT(*) FROM sessoes").fetchone()[0] == 0:
        rows=[
            (1,1,"2026-09-10T18:00:00","2026-09-10T19:30:00",12.4,0.82,10.168,2.50,12.668),
            (2,2,"2026-09-11T07:10:00","2026-09-11T08:25:00",9.8,0.82,8.036,2.50,10.536),
            (3,1,"2026-09-11T19:00:00","2026-09-11T20:40:00",14.7,0.89,13.083,2.50,15.583),
            (1,3,"2026-09-12T12:15:00","2026-09-12T13:00:00",6.2,0.82,5.084,2.50,7.584),
            (4,2,"2026-09-13T20:00:00","2026-09-13T21:50:00",16.3,0.89,14.507,2.50,17.007),
            (2,1,"2026-09-14T06:45:00","2026-09-14T07:55:00",8.9,0.82,7.298,2.50,9.798),
        ]
        cur.executemany("""INSERT INTO sessoes
        (usuario_id,carregador_id,inicio,fim,energia_kwh,tarifa_kwh,custo_energia,taxa_manutencao,custo_total)
        VALUES(?,?,?,?,?,?,?,?,?)""",rows)
    conn.commit(); conn.close()
