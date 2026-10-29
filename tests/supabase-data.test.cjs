const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
require('../dist/supabase-data.js');
const ctx = {window:{}};
vm.runInNewContext(fs.readFileSync(require.resolve('../dist/data.js'),'utf8'), ctx);
const sample = JSON.parse(JSON.stringify(ctx.window.DATA));
const config = {url:'https://example.supabase.co',publishableKey:'sb_publishable_test'};
let calls = 0;
const mock = async url => {
  calls++;
  const u = new URL(url), name = u.pathname.split('/').at(-1).replace(/^furia_/, '');
  const all = sample[name], offset = +u.searchParams.get('offset');
  // Simula limite do servidor menor que o solicitado: 200 registros por página.
  return {ok:true, headers:{get:()=>`${offset}-${Math.min(offset+199,all.length-1)}/${all.length}`},json:async()=>all.slice(offset,offset+200)};
};
(async()=>{
  const loaded = await FuriaDB.load(config,mock);
  assert.deepEqual(loaded,sample);
  assert.ok(calls>15, 'Deve paginar os 2.765 registros de jogadores');
  await assert.rejects(()=>FuriaDB.load(config,async()=>({ok:true,headers:{get:()=> '*/0'},json:async()=>[]})),/vazia/);
  await assert.rejects(()=>FuriaDB.load(config,async()=>({ok:false,status:404,json:async()=>({code:'PGRST205',message:'table missing'})})),/PGRST205/);
  await assert.rejects(()=>FuriaDB.load(config,async()=>({ok:true,headers:{get:()=> '*/100'},json:async()=>[]})),/incompleta/);
  const incomplete = structuredClone(sample); incomplete.jogadores_mapas.pop();
  assert.throws(()=>FuriaDB.validate(incomplete),/cinco jogadores/);
  console.log('OK: paginação, base completa, tabela ausente, acesso vazio e importação incompleta.');
})().catch(e=>{console.error(e);process.exitCode=1});
