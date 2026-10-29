// Cliente REST somente leitura: não depende de pacotes ou CDN.
(function (root) {
  'use strict';
  const TABLES = {
    partidas: { table: 'furia_partidas', order: 'match_id.asc', columns: 'match_id,data,ano,evento,adversario,vitoria,mapas_furia,mapas_adversario,fonte_url' },
    mapas_jogados: { table: 'furia_mapas_jogados', order: 'mapstats_id.asc', columns: 'mapstats_id,match_id,data,ano,evento,adversario,mapa,rounds_furia,rounds_adversario,rounds_total,vitoria,lan,fonte_url' },
    jogadores_mapas: { table: 'furia_jogadores_mapas', order: 'mapstats_id.asc,jogador.asc', columns: 'mapstats_id,ano,jogador,kills,deaths,assists,rounds_mapa,adr,kast,rating' }
  };
  async function readTable(spec, config, fetcher) {
    const all = []; let offset = 0; let expected = null;
    while (true) {
      const url = new URL(config.url.replace(/\/$/, '') + '/rest/v1/' + spec.table);
      url.search = new URLSearchParams({select: spec.columns, order: spec.order, offset: String(offset), limit: '500'});
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 20000);
      let response;
      try { response = await fetcher(url.toString(), {headers: {apikey: config.publishableKey, Prefer: 'count=exact'}, signal: controller.signal, cache: 'no-store'}); }
      finally { clearTimeout(timeout); }
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(`${spec.table}: ${error.code || response.status}. ${error.message || 'Falha na consulta.'}`);
      }
      const chunk = await response.json();
      if (!Array.isArray(chunk)) throw new Error('Resposta inválida para ' + spec.table);
      const range = response.headers.get('content-range');
      const total = range && Number(range.split('/')[1]);
      if (!range || !Number.isInteger(total) || total < 0) throw new Error('Contagem de registros indisponível em ' + spec.table);
      if (expected !== null && total !== expected) throw new Error('Os dados mudaram durante a consulta. Atualize o painel.');
      expected = total;
      all.push(...chunk); offset += chunk.length;
      if (offset >= total) break;
      if (!chunk.length) throw new Error('Consulta incompleta em ' + spec.table);
    }
    if (all.length !== expected) throw new Error('Quantidade incompleta em ' + spec.table);
    if (!all.length) throw new Error(spec.table + ': tabela vazia ou leitura não liberada.');
    return all;
  }
  function validate(data) {
    const p = data.partidas, m = data.mapas_jogados, j = data.jogadores_mapas;
    const series = new Set(p.map(r => r.match_id));
    const maps = new Set(m.map(r => r.mapstats_id));
    if (series.size !== p.length || maps.size !== m.length) throw new Error('IDs duplicados na base.');
    if (m.some(r => !series.has(r.match_id))) throw new Error('Mapas sem série correspondente.');
    const unique = new Set(); const playersPerMap = new Map();
    for (const r of j) {
      const key = `${r.mapstats_id}:${r.jogador}`;
      if (unique.has(key) || !maps.has(r.mapstats_id)) throw new Error('Registros de jogadores inconsistentes.');
      unique.add(key); playersPerMap.set(r.mapstats_id, (playersPerMap.get(r.mapstats_id) || 0) + 1);
      for (const k of ['kills','deaths','assists','rounds_mapa','adr','kast','rating']) {
        if (typeof r[k] !== 'number' || !Number.isFinite(r[k])) throw new Error('Estatística inválida: ' + k);
      }
    }
    if (m.some(r => playersPerMap.get(r.mapstats_id) !== 5)) throw new Error('A importação deve conter os cinco jogadores da FURIA por mapa.');
    for (const r of [...m, ...p]) {
      if (![0,1].includes(r.vitoria) || !Number.isInteger(r.ano) || !/^\d{4}-\d{2}-\d{2}$/.test(r.data)) throw new Error('Data ou resultado inválido.');
    }
    if (m.some(r => r.rounds_total <= 0 || r.rounds_furia + r.rounds_adversario !== r.rounds_total)) throw new Error('Rounds inconsistentes.');
    return data;
  }
  root.FuriaDB = {
    async load(config, fetcher = fetch) {
      if (!config?.publishableKey?.startsWith('sb_publishable_')) throw new Error('Informe apenas a chave pública publishable.');
      const entries = await Promise.all(Object.entries(TABLES).map(async ([name, spec]) => [name, await readTable(spec, config, fetcher)]));
      return validate(Object.fromEntries(entries));
    },
    validate
  };
})(typeof window === 'undefined' ? globalThis : window);
