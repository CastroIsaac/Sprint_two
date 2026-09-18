
from datetime import datetime

DEFAULT_MAINTENANCE = 2.50

def calcular_rateio(energia_kwh: float, tarifa_kwh: float, taxa_manutencao: float = DEFAULT_MAINTENANCE):
    custo_energia = round(energia_kwh * tarifa_kwh, 2)
    custo_total = round(custo_energia + taxa_manutencao, 2)
    return {"energia_kwh": energia_kwh, "tarifa_kwh": tarifa_kwh,
            "custo_energia": custo_energia, "taxa_manutencao": taxa_manutencao,
            "custo_total": custo_total}

def calcular_duracao_min(inicio: str, fim: str):
    a=datetime.fromisoformat(inicio); b=datetime.fromisoformat(fim)
    return max(0, int((b-a).total_seconds()/60))
