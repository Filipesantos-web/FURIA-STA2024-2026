import matplotlib
matplotlib.use("Agg")

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path.cwd()
mapas = pd.read_csv(BASE / "mapas_jogados.csv", parse_dates=["data"])
partidas = pd.read_csv(BASE / "partidas.csv", parse_dates=["data"])
jogadores = pd.read_csv(BASE / "jogadores_mapas.csv", parse_dates=["data"])
lados = pd.read_csv(BASE / "jogadores_lados.csv", parse_dates=["data"])
vetos = pd.read_csv(BASE / "vetos.csv")
mapas_anuais = pd.read_csv(BASE / "mapas_anuais.csv")
furia = jogadores.query('equipe == "FURIA"').copy()
SAIDA = BASE / "resultados"
SAIDA.mkdir(exist_ok=True)
print({"series": len(partidas), "mapas": len(mapas), "jogador_mapa_furia": len(furia)})


assert mapas["mapstats_id"].is_unique
assert partidas["match_id"].is_unique
assert not jogadores.duplicated(["mapstats_id", "equipe", "jogador"]).any()
assert len(mapas) == 553 and len(furia) == 2765
assert set(mapas["match_id"]) == set(partidas["match_id"])
conferencia = pd.read_csv(BASE / "conferencia.csv")
assert conferencia["diferenca"].eq(0).all()
por_lado = lados.groupby(["mapstats_id", "equipe", "jogador"])[["kills", "deaths", "assists"]].sum()
total = jogadores.set_index(["mapstats_id", "equipe", "jogador"])[["kills", "deaths", "assists"]]
pd.testing.assert_frame_equal(por_lado.sort_index(), total.sort_index(), check_dtype=False)
print(jogadores.isna().sum().loc[lambda s: s.gt(0)])


anual_mapas = mapas.groupby("ano").agg(
    mapas=("mapstats_id", "count"), mapas_vencidos=("vitoria", "sum"),
    rounds_ganhos=("rounds_furia", "sum"), rounds_jogados=("rounds_total", "sum"))
anual_mapas["map_winrate"] = anual_mapas["mapas_vencidos"] / anual_mapas["mapas"]
anual_mapas["round_winrate"] = anual_mapas["rounds_ganhos"] / anual_mapas["rounds_jogados"]
anual_series = partidas.groupby("ano").agg(series=("match_id", "count"), series_vencidas=("vitoria", "sum"))
anual_series["series_winrate"] = anual_series["series_vencidas"] / anual_series["series"]
anual = anual_series.join(anual_mapas)
anual.to_csv(SAIDA / "comparacao_anual.csv")
print(anual.round(4))
ax = anual[["series_winrate", "map_winrate", "round_winrate"]].plot.bar(figsize=(8, 4), ylim=(0, 1))
ax.set_ylabel("Taxa de vitória")
ax.set_title("FURIA: séries, mapas e rounds")
plt.tight_layout()
plt.savefig(SAIDA / "winrates_anuais.png", dpi=180)
plt.show()


individual = furia.groupby("jogador").agg(
    mapas=("mapstats_id", "count"), kills=("kills", "sum"), deaths=("deaths", "sum"),
    assists=("assists", "sum"), rounds=("rounds_mapa", "sum"))
den = individual["deaths"].where(individual["deaths"].ne(0))
individual["kd_ratio"] = individual["kills"] / den
individual["kda_ratio"] = (individual["kills"] + individual["assists"]) / den
individual["kpr"] = individual["kills"] / individual["rounds"]
individual.sort_values("kda_ratio", ascending=False).to_csv(SAIDA / "jogadores.csv")
print(individual.sort_values("kda_ratio", ascending=False).round(3))


map_pool = mapas.groupby("mapa").agg(mapas=("mapstats_id", "count"),
    vitorias=("vitoria", "sum"), rounds_ganhos=("rounds_furia", "sum"), rounds_jogados=("rounds_total", "sum"))
map_pool["map_winrate"] = map_pool["vitorias"] / map_pool["mapas"]
map_pool["round_winrate"] = map_pool["rounds_ganhos"] / map_pool["rounds_jogados"]
side = mapas_anuais.groupby("ano")[["rounds_ct", "rounds_tr", "rounds_ganhos_ct", "rounds_ganhos_tr"]].sum()
side["ct_winrate"] = side["rounds_ganhos_ct"] / side["rounds_ct"]
side["tr_winrate"] = side["rounds_ganhos_tr"] / side["rounds_tr"]
print(map_pool.sort_values("map_winrate", ascending=False).round(3))
print(side.round(3))
side.to_csv(SAIDA / "lados_por_ano.csv")


vetos_com_data = vetos.merge(partidas[["match_id", "ano", "data", "adversario"]], on="match_id", validate="many_to_one")
vetos_furia = vetos_com_data.query('equipe == "FURIA"')
escolhas = vetos_furia.groupby(["ano", "mapa", "acao"]).size().unstack("acao", fill_value=0)
print(escolhas)
escolhas.to_csv(SAIDA / "picks_bans_por_ano.csv")
mapas["origem_mapa"] = "pick_adversario"
mapas.loc[mapas["equipe_pick"].eq("FURIA"), "origem_mapa"] = "pick_furia"
mapas.loc[mapas["tipo_escolha"].eq("decider"), "origem_mapa"] = "decider"
mapas.loc[mapas["tipo_escolha"].isna(), "origem_mapa"] = "nao_determinado"
print(mapas.groupby("origem_mapa").agg(mapas=("mapstats_id", "count"), winrate=("vitoria", "mean")).round(3))


adversarios = pd.read_csv(BASE / "adversarios.csv")
MIN_SERIES = 5
comparaveis = adversarios.loc[adversarios["series"].ge(MIN_SERIES)].copy()
colunas = ["adversario", "series", "series_winrate", "map_winrate", "round_winrate", "wilson95_inferior_series", "wilson95_superior_series"]
print("Melhor histórico:")
print(comparaveis.sort_values(["series_winrate", "round_winrate"], ascending=False)[colunas].head(10).round(3))
print("Pior histórico:")
print(comparaveis.sort_values(["series_winrate", "round_winrate"])[colunas].head(10).round(3))


mensal = mapas.assign(mes=mapas["data"].dt.to_period("M").astype(str)).groupby("mes").agg(
    mapas=("mapstats_id", "count"), vitorias=("vitoria", "sum"))
mensal["winrate"] = mensal["vitorias"] / mensal["mapas"]
ax = mensal["winrate"].plot(figsize=(11, 4), marker="o", ylim=(0, 1), title="Winrate mensal de mapas")
ax.set_ylabel("Taxa de vitória")
plt.tight_layout()
plt.savefig(SAIDA / "winrate_mensal.png", dpi=180)
plt.show()
stats_time = furia.groupby("mapstats_id").agg(adr_medio=("adr", "mean"), kast_medio=("kast", "mean"), opening_kills=("opening_kills", "sum"))
completo = mapas.merge(stats_time, on="mapstats_id", validate="one_to_one")
print(completo[["vitoria", "round_winrate", "adr_medio", "kast_medio", "opening_kills"]].corr().round(3))
