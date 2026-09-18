
from pathlib import Path
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

from .database import get_connection

class ChargeOpsAI:
    """Módulo estrutural: previsão de consumo, perfil de uso e anomalias."""
    def __init__(self):
        self.model = LinearRegression()
        self.cluster = None
        self.anomaly = None
        self.trained = False

    def _dataset(self):
        conn=get_connection()
        rows=conn.execute("""SELECT energia_kwh, tarifa_kwh, custo_total,
                                    CAST(strftime('%H', inicio) AS INTEGER) hora,
                                    CAST((julianday(fim)-julianday(inicio))*24*60 AS REAL) duracao
                             FROM sessoes""").fetchall()
        conn.close()
        X=np.array([[r["hora"], r["duracao"], r["tarifa_kwh"]] for r in rows], dtype=float)
        y=np.array([r["energia_kwh"] for r in rows], dtype=float)
        return X,y

    def treinar(self):
        X,y=self._dataset()
        if len(X)<2: return {"status":"dados insuficientes"}
        self.model.fit(X,y)
        n_clusters=min(2,len(X))
        self.cluster=KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(X)
        self.anomaly=IsolationForest(contamination=0.2, random_state=42).fit(X)
        self.trained=True
        return {"status":"treinado","amostras":len(X),"r2_treino":round(float(self.model.score(X,y)),4)}

    def prever(self, hora: int, duracao_min: float, tarifa_kwh: float):
        if not self.trained: self.treinar()
        pred=float(self.model.predict([[hora,duracao_min,tarifa_kwh]])[0])
        return max(0,round(pred,2))

    def diagnostico(self):
        X,y=self._dataset()
        if len(X)<2: return {"status":"dados insuficientes"}
        if not self.trained: self.treinar()
        labels=self.anomaly.predict(X)
        return {"total_sessoes":len(X),"anomalias":int(np.sum(labels==-1)),
                "energia_media_kwh":round(float(np.mean(y)),2)}
