"""Consulta somente leitura e exportação para análise com Pandas."""
from pathlib import Path
import json
from urllib.request import Request, urlopen
import pandas as pd

URL = "https://adkzpzaogrtgiwzhuksy.supabase.co"
PUBLISHABLE_KEY = "sb_publishable_bPf7T0dgMYix5UCPVGgbvQ_4yFs1Tg0"
SAIDA = Path(__file__).resolve().parents[1] / "dados_supabase"


def consultar(tabela, ordem):
    linhas = []
    total = None
    while total is None or len(linhas) < total:
        endpoint = (f"{URL}/rest/v1/{tabela}?select=*&order={ordem}"
                    f"&offset={len(linhas)}&limit=500")
        req = Request(endpoint, headers={"apikey": PUBLISHABLE_KEY,
                                        "Prefer": "count=exact"})
        with urlopen(req, timeout=30) as resposta:
            contagem = int(resposta.headers["Content-Range"].split("/")[1])
            if total is not None and contagem != total:
                raise RuntimeError("Base alterada durante a consulta. Execute novamente.")
            total = contagem
            lote = json.load(resposta)
        if not lote and len(linhas) < total:
            raise RuntimeError(f"Consulta incompleta: {tabela}")
        linhas.extend(lote)
    if not linhas:
        raise RuntimeError(f"{tabela}: tabela vazia ou leitura não liberada")
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    for tabela, ordem in [("furia_partidas", "match_id.asc"),
                           ("furia_mapas_jogados", "mapstats_id.asc"),
                           ("furia_jogadores_mapas", "mapstats_id.asc,jogador.asc")]:
        df = consultar(tabela, ordem)
        df.to_csv(SAIDA / f"{tabela}.csv", index=False)
        print(f"{tabela}: {len(df)} registros exportados")
