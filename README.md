# FURIA Performance Lab — Big Data em Python

<p align="center">
  <img src="imagens/furia-logo.png" alt="Símbolo da FURIA presente no relatório" width="180">
</p>

<p align="center"><em>Análise exploratória de desempenho no Counter-Strike 2</em></p>

> Análise exploratória de desempenho da equipe masculina da FURIA no Counter-Strike 2 (CS2), com base nos dados fornecidos para o período de 2024 a 2026.

**Relatório técnico:** 29/10/2026  
**Origem declarada dos dados:** HLTV — equipe FURIA, ID 8297  
**Projeto acadêmico independente, sem vínculo oficial com a FURIA.**

---

## 📌 Sobre o projeto

O projeto aplica técnicas de importação, limpeza, validação, exploração e visualização de dados com Python para transformar estatísticas competitivas de CS2 em informações úteis.

A análise investiga:

- Evolução temporal do desempenho da equipe;
- Desempenho por mapa/cenário;
- Participação e estatísticas individuais dos jogadores;
- Histórico de confrontos por adversário;
- Comparação descritiva entre partidas LAN e online;
- Relação entre estatísticas do time e resultados dos mapas;
- Apresentação dos resultados em dashboard e gráficos exploratórios.

## 🎯 Objetivos

1. Importar e organizar os arquivos de dados fornecidos.
2. Identificar e tratar duplicidades, valores ausentes e inconsistências.
3. Validar datas, tipos, resultados, estatísticas e relacionamentos entre tabelas.
4. Calcular indicadores de desempenho por série, mapa, round e jogador.
5. Criar gráficos e tabelas para apoiar a interpretação dos resultados.
6. Disponibilizar um dashboard para explorar os dados e comunicar as conclusões.

## 📊 Visão geral da base

| Indicador | Quantidade |
|---|---:|
| Séries completas | 243 |
| Mapas | 553 |
| Registros jogador-mapa da FURIA | 2.765 |
| Registros individuais originais das duas equipes | 5.530 |
| Rounds contabilizados | 11.935 |

A tabela individual original contém 5.530 registros das duas equipes. Após o filtro `equipe = FURIA`, permanecem 2.765 registros de jogador-mapa.

### Principais resultados

- **Mapas vencidos:** 312 de 553 (**56,42%**).
- **Séries vencidas:** 143 de 243 (**58,85%**).
- **Proporção de rounds vencidos:** **51,96%**, em 11.935 rounds.
- **Melhor taxa anual de vitória em mapas:** 2025, com **60,19%**.

> **Atenção:** 2026 é um ano parcial na base analisada. Os resultados representam os arquivos fornecidos e não uma coleta ou auditoria independente de todos os confrontos.

## 🗓️ Recorte e origem dos dados

A origem declarada nos arquivos é a [HLTV — FURIA](https://www.hltv.org/team/8297/furia), equipe masculina, ID 8297. A coleta informada nos arquivos ocorreu em **09/10/2026**, e o último mapa presente na base é de **07/10/2026**. As páginas específicas de origem estão registradas na coluna `fonte_url` dos CSVs.

Não foi realizada nova coleta nem revalidação externa de cada confronto nesta entrega.

## 🧹 Tratamento e qualidade dos dados

A análise trabalha com três níveis:

- **Série completa**;
- **Mapa**;
- **Jogador-mapa**.

| Verificação | Resultado | Tratamento |
|---|---|---|
| Duplicatas nas chaves | Nenhuma nas três tabelas | As chaves usam `match_id`, `mapstats_id` e jogador-mapa-equipe. Duplicatas exatas são removidas pelo script; conflitos interrompem a análise. |
| Evento ausente | 4 séries e 10 mapas | O valor `NULL` é preservado no campo de evento; uma coluna separada apresenta um rótulo explicativo. |
| Demais campos opcionais ausentes | Documentados por coluna | Os valores são preservados e não são usados como campos obrigatórios dos indicadores. |
| Datas e números obrigatórios | Validação concluída | Conversão de tipos, compatibilidade entre ano e data, resultado 0/1 e estatísticas não negativas. |
| Relacionamentos e rounds | Validação concluída | Mapas vinculados às séries, cinco jogadores da FURIA por mapa e soma dos rounds conciliada. |

Os dados esportivos não são preenchidos com valores inventados. Os CSVs originais permanecem em `analise/`, permitindo rastrear o processamento.

## 📈 Desempenho anual

![Gráfico de taxa de vitória em séries, mapas e rounds por ano](imagens/desempenho-anual.png)


| Ano | Séries | Mapas | Taxa de vitória em mapas | Taxa de vitória em séries |
|---|---:|---:|---:|---:|
| 2024 | 85 | 164 | 53,66% | 54,12% |
| 2025 | 90 | 216 | 60,19% | 63,33% |
| 2026* | 68 | 173 | 54,34% | 58,82% |

\* **2026 é parcial.**

Em 2025, a FURIA apresentou a maior taxa de vitória em mapas no conjunto analisado. A comparação é descritiva: não controla diferenças entre adversários, elenco ou torneios. Os denominadores variam conforme o indicador (séries, mapas ou rounds).

## 🗺️ Desempenho por mapa

| Mapa | Mapas disputados | Mapas vencidos | Taxa de vitória |
|---|---:|---:|---:|
| Overpass | 40 | 26 | 65,00% |
| Nuke | 90 | 57 | 63,33% |
| Train | 27 | 17 | 62,96% |
| Dust2 | 96 | 57 | 59,38% |
| Inferno | 91 | 54 | 59,34% |
| Mirage | 113 | — | 50,44% |

Overpass apresentou a maior taxa entre os cenários listados (65,00%), com 40 mapas. Nuke teve 63,33% em uma amostra de 90 mapas. Mirage foi o mapa mais frequente, com 113 mapas e taxa de vitória de 50,44%.

**Como interpretar:** percentuais devem ser avaliados junto com o tamanho da amostra. O desempenho em um mapa pode indicar onde investigar, mas não identifica sozinho as causas táticas dos resultados.

## 👥 Estatísticas individuais

![Gráfico de abates, mortes e assistências por jogador](imagens/estatisticas-jogadores.png)


Abates, mortes e assistências são comparados por mapa para reduzir o efeito de diferenças no tempo de participação. Essa normalização, porém, não controla a duração do mapa, a função tática nem a força dos adversários.

| Medida | Definição utilizada |
|---|---|
| ADR | Dano médio causado por round. Na comparação entre jogadores, é calculada a média simples do ADR publicado para cada mapa. |
| K/D agregado | Soma dos abates dividida pela soma das mortes. Divisão por zero resulta em valor ausente. |
| KAST | Percentual de rounds com abate, assistência, sobrevivência ou morte trocada por um companheiro. |
| Registro jogador-mapa | Uma observação de um jogador em um mapa. Os cinco registros de um mesmo mapa compartilham o contexto da partida. |

Exemplos destacados no relatório:

- **molodoy:** K/D de 1,29 em 335 mapas.
- **KSCERATO:** K/D de 1,19 em 553 mapas.

Esses números correspondem a funções e períodos de participação diferentes e não constituem, isoladamente, um ranking definitivo de qualidade individual.

## 🆚 Adversários e tipo de partida

As análises exploratórias incluem a frequência e os resultados dos confrontos por adversário, além de uma comparação descritiva entre partidas LAN e online. O histórico pode apoiar a preparação para confrontos recorrentes, mas é recomendável evitar conclusões baseadas em uma única série.

## 📉 Dashboard e visualizações

![Captura de tela do dashboard FURIA Performance Lab](imagens/dashboard.png)


O dashboard organiza as informações em áreas de:

- Visão geral;
- Mapas;
- Jogadores;
- Adversários;
- Partidas;
- Gráficos Python;
- Análises.

A visão geral apresenta quatro gráficos e quatro indicadores principais:

1. Taxa de vitória em mapas;
2. Séries disputadas;
3. Mapas jogados;
4. Proporção de rounds vencidos.

A galeria de visualizações possui **11 tipos de gráficos**, com versões para 2024, 2025, 2026 e todos os anos, totalizando **44 imagens e 44 tabelas CSV**. Os gráficos incluem títulos, eixos, unidades, tamanhos de amostra e orientações de leitura.

Entre as visualizações estão distribuição de ADR, KAST por jogador, saldo de rounds, nuvem de adversários e matriz de correlação.

### Correlação entre estatísticas e vitória

![Matriz de correlação entre resultado e estatísticas do time](imagens/matriz-correlacao.png)


A matriz usa uma linha por mapa e correlação de Pearson. ADR médio e KAST médio apresentam associação positiva com a vitória, aproximadamente **0,71** na base completa.

**Correlação não significa causalidade.** O resultado e as estatísticas são observados na mesma partida; portanto, essa associação não demonstra que aumentar isoladamente uma medida causará uma vitória.

Na nuvem de adversários, o tamanho do nome representa a quantidade de séries disputadas contra aquele adversário, não a dificuldade do rival.

## 🧰 Tecnologias e bibliotecas

| Tecnologia | Uso no projeto |
|---|---|
| Python | Linguagem utilizada no processamento e na análise. |
| Pandas | Importação, limpeza, filtros, agrupamentos e correlação. |
| NumPy | Medianas, intervalos, divisões e faixas de histogramas. |
| Matplotlib | Construção e exportação de gráficos com legendas e eixos. |
| Seaborn | Histogramas, gráficos de barras, boxplots e matriz de correlação. |
| WordCloud | Nuvem de palavras ponderada pela frequência de séries. |
| Supabase | Fonte de dados utilizada pelo dashboard quando disponível. |
| HTML/JavaScript do dashboard | Interface de exploração dos resultados distribuída em `dist/`. |

## 📁 Organização dos arquivos

A estrutura mencionada no relatório inclui os seguintes diretórios e arquivos:

```text
.
├── README.md
├── requirements.txt
├── analise/
│   └── CSVs originais fornecidos
├── scripts/
│   ├── tratar_e_analisar.py
│   └── gerar_graficos.py
├── dados_tratados/
├── resultados/
│   ├── qualidade_dados.json
│   ├── indicadores.json
│   ├── tabelas exploratórias
│   ├── gráficos exportados
│   └── tabelas CSV dos gráficos
└── dist/
    └── arquivos do dashboard
```

> A árvore acima resume os caminhos citados no relatório. Os nomes exatos de todos os arquivos podem variar conforme o conteúdo publicado no repositório.

## ▶️ Como executar

### 1. Pré-requisitos

- Python instalado;
- Repositório clonado ou arquivos do projeto baixados;
- Arquivos CSV originais disponíveis em `analise/`.

### 2. Instalar as dependências

Na raiz do projeto, execute:

```bash
pip install -r requirements.txt
```

### 3. Tratar os dados e gerar indicadores

```bash
python scripts/tratar_e_analisar.py
```

O script lê os CSVs locais por padrão, realiza as validações e o tratamento e gera dados em `dados_tratados/`, tabelas exploratórias e os arquivos `qualidade_dados.json` e `indicadores.json` em `resultados/`.

### 4. Gerar os gráficos

```bash
python scripts/gerar_graficos.py
```

O script exporta os gráficos e as tabelas CSV correspondentes.

### 5. Abrir o dashboard local

Conforme o relatório, execute:

```bash
python -m http.server 5500 --directory dist
```

Depois, abra no navegador:

```text
http://localhost:5500
```

O relatório registra uma execução local do dashboard com leitura do Supabase confirmada. Também existe uma cópia local em modo de prévia para quando o banco não estiver disponível. A disponibilidade do dashboard conectado depende da configuração do ambiente.

## 💡 Conclusões e possíveis aplicações

A análise aponta algumas linhas de investigação:

- **Revisar mapas de grande exposição e desempenho próximo de 50%, como Mirage.** Os dados ajudam a identificar onde investigar; a causa exige revisão tática adicional.
- **Considerar percentual e tamanho da amostra em conjunto.** Overpass apresenta percentual superior, enquanto Nuke oferece uma amostra maior.
- **Comparar jogadores usando médias por mapa e número de observações.** Função tática e mudanças de elenco devem ser consideradas.
- **Usar o histórico de adversários para preparar confrontos frequentes**, evitando conclusões baseadas em apenas uma série.
- **Acompanhar a evolução temporal**, lembrando que o recorte de 2026 está incompleto e que os volumes de mapas e séries variam entre anos.

## ⚠️ Limitações

- O ano de 2026 é parcial.
- As amostras anuais são diferentes.
- Mapas de uma mesma série não são independentes; intervalos de Wilson não corrigem esse agrupamento.
- A metodologia cobre mapas com estatísticas e não equivale a auditar W/O, cancelamentos ou jogos sem estatísticas.
- Médias de rating por mapa não são ratings agregados oficiais.
- A base foi fornecida com origem declarada; não houve coleta independente nesta etapa.
- A análise é exploratória e descritiva: correlações não demonstram causalidade.
- O volume de dados é de milhares de registros. Esse volume permite praticar análise de dados com Python, mas não exige computação distribuída e, por si só, não caracteriza um sistema de Big Data em produção.

## 📚 Referências

- [HLTV — FURIA](https://www.hltv.org/team/8297/furia) — origem declarada dos dados; consulte também os endereços registrados na coluna `fonte_url` dos CSVs.
- [Documentação do Pandas](https://pandas.pydata.org/docs/)
- [Documentação do NumPy](https://numpy.org/doc/)
- [Documentação do Matplotlib](https://matplotlib.org/stable/)
- [Documentação do Seaborn](https://seaborn.pydata.org/)
- [WordCloud](https://amueller.github.io/word_cloud/)
- [Documentação do Supabase](https://supabase.com/docs)

## 🎓 Considerações finais

Este projeto acadêmico aplica técnicas de análise de dados com Python a uma base de milhares de registros de partidas de Counter-Strike 2 da FURIA, com foco em qualidade dos dados, indicadores de desempenho, visualizações e comunicação dos resultados.

O código, os dados, as tabelas de resultados e as imagens acompanham o projeto conforme os arquivos disponibilizados no repositório. Os resultados e as conclusões devem ser interpretados dentro do recorte e das limitações descritos neste documento.
