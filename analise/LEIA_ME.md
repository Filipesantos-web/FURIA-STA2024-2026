# FURIA CS2 — base para análise com pandas

Período: 01/01/2024 a 09/10/2026. Último mapa concluído: 07/10/2026.
Fonte: HLTV, equipe masculina 8297. As consultas incluem todos os eventos, LAN e online.

## Arquivos
O Excel organiza 243 séries, 553 mapas, 1.701 ações de veto, 5.530 observações
jogador-mapa (2.765 da FURIA), e 11.060 observações jogador-mapa-lado.
Os CSVs replicam as tabelas em UTF-8, com cabeçalho na primeira linha.
`Analise_FURIA.ipynb` contém exemplos executáveis e perguntas de pesquisa.
`analise_furia.py` executa a análise pelo terminal e grava tabelas e gráficos.
`requirements.txt` lista dependências comuns; não é necessário acessar a internet para analisar os dados.
`metodologia.csv`, `dicionario.csv` e `conferencia.csv` documentam o significado,
as transformações e a conciliação dos dados.

## Como começar
1. Extraia este ZIP e abra o notebook na pasta extraída, usando Jupyter ou VS Code.
2. Instale as dependências, se necessário: `pip install -r requirements.txt`.
3. Execute as células em ordem. Alternativamente: `python analise_furia.py`.
4. Para ler diretamente o Excel: `pd.read_excel("FURIA_CS2_2024_2026.xlsx", sheet_name="mapas_jogados")`.

## Cuidados com a análise
- Filtre `equipe == "FURIA"` antes de agregar as estatísticas do time.
- `jogadores_mapas` contém TOTAL; `jogadores_lados` contém CT/TR. Não some as três categorias.
- A chave de jogador-mapa é `(mapstats_id, equipe, jogador)`.
- K/D = kills / deaths. KDA = (kills + assists) / deaths. Zero mortes gera valor ausente.
- As taxas são números de 0 a 1; 0.55 representa 55%.
- Round winrate usa soma dos rounds ganhos / soma dos rounds jogados.
- `rating_media_mapas` é uma média de ratings de mapas, não o rating agregado oficial HLTV.
- ADR/KAST agregados usam os valores arredondados publicados; admitem pequena diferença de arredondamento.
- `rounds_lado` foi reconstruído por KAST, mortes e opening kills com solução inteira única,
  e conciliado contra os denominadores CT oficiais: 1691 (2024), 2331 (2025), 1843 (2026).
- Rounds ganhos CT/TR anuais por mapa foram reconstruídos das taxas HLTV e do denominador exato,
  exclusivamente quando a solução inteira foi única. CT + TR foi conciliado com os rounds ganhos.
- Não trate uma vitória em um único confronto como prova de que o adversário é fácil.
- O histórico cobre mapas com estatísticas. Não é auditoria de Results para jogos sem estatísticas,
  walkovers, cancelamentos, partidas futuras ou eventos exibidos apenas no perfil do time.
- Não foram extraídos demos, VODs, heatmaps, coordenadas, armas, economia, ranking histórico,
  nem detalhamento de clutches por tamanho. A base não representa literalmente todos os campos da HLTV.

## Ideias para o trabalho
1. O desempenho em séries, mapas e rounds mudou entre 2024, 2025 e 2026?
2. Quais mapas favorecem mais a FURIA e qual o efeito de CT e TR?
3. O time ganha mais nos mapas que escolhe ou nos escolhidos pelo adversário?
4. Picks e bans mudaram ao longo do tempo?
5. Quais adversários têm melhor e pior histórico, considerando o tamanho da amostra?
6. Qual a associação de ADR, KAST e opening kills com vitória no mapa?
7. Como mudanças de elenco se associam ao desempenho, sem atribuir causalidade automaticamente?

Data de coleta: 09/10/2026. Cada tabela original contém a URL correspondente.
Os scripts de extração presentes em `tratamento/` operam sobre a coleta intermediária da sessão;
não são um crawler independente. A coleta foi realizada pela leitura de páginas públicas.
