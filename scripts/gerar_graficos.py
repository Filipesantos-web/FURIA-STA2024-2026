"""Gera os gráficos Python do dashboard a partir de uma consulta ao Supabase.
Execute na raiz: py scripts/gerar_graficos.py
Requer pandas, numpy, matplotlib, seaborn e wordcloud.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from wordcloud import WordCloud
from consultar_supabase import consultar
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist' / 'graficos'
OUT.mkdir(parents=True, exist_ok=True)
ACCENT, GRAY, LIGHT, DARK = '#f3f3ef', '#929aa1', '#c2c7cb', '#66707a'
sns.set_theme(style='darkgrid')
plt.rcParams.update({'figure.facecolor':'#141618','axes.facecolor':'#141618',
    'savefig.facecolor':'#141618','text.color':'#edf0ef','axes.labelcolor':'#b8c1c9',
    'xtick.color':'#a8b2bd','ytick.color':'#a8b2bd','axes.edgecolor':'#333940',
    'grid.color':'#282d32','grid.alpha':0.6,'font.size':10,'axes.titlesize':13,
    'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False})

p = consultar('furia_partidas','match_id.asc')
m = consultar('furia_mapas_jogados','mapstats_id.asc')
j = consultar('furia_jogadores_mapas','mapstats_id.asc,jogador.asc')
assert p.match_id.is_unique and m.mapstats_id.is_unique
assert not j.duplicated(['mapstats_id','jogador']).any()
assert set(m.match_id).issubset(set(p.match_id))
assert j.groupby('mapstats_id').size().eq(5).all() and set(j.mapstats_id)==set(m.mapstats_id)
m['data'] = pd.to_datetime(m['data'])
manifest = {'source':'Supabase', 'generated_at':datetime.now(timezone.utc).isoformat(),
    'counts':{'partidas':len(p),'mapas':len(m),'jogadores':len(j)},
    'last_map':str(m['data'].max().date()), 'periods':{},
    'libraries':{x:__import__(x).__version__ for x in ['pandas','numpy','matplotlib','seaborn','wordcloud']}}


def save(fig, period, name):
    fig.tight_layout(pad=1.8)
    path = OUT / f'{period}_{name}.png'
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


for period in ['all'] + [str(a) for a in sorted(m.ano.unique())]:
    mm = m if period=='all' else m[m.ano==int(period)]
    pp = p if period=='all' else p[p.ano==int(period)]
    jj = j if period=='all' else j[j.ano==int(period)]
    paths = []
    # 1. Comparação anual de séries, mapas e rounds
    bymap = mm.groupby('ano').agg(mapas=('vitoria','mean'),wins=('rounds_furia','sum'),rounds=('rounds_total','sum'))
    bymap['rounds'] = bymap['wins']/bymap['rounds']
    bymap['series'] = pp.groupby('ano')['vitoria'].mean()
    long = bymap[['series','mapas','rounds']].rename(columns={'series':'Séries','mapas':'Mapas','rounds':'Rounds'}).mul(100).reset_index().melt(id_vars='ano',var_name='Unidade',value_name='Vitórias (%)')
    fig,ax=plt.subplots(figsize=(8,4.8))
    sns.barplot(data=long,x='ano',y='Vitórias (%)',hue='Unidade',palette=[ACCENT,LIGHT,GRAY],ax=ax)
    ax.set(ylim=(0,100),xlabel='Ano',ylabel='Vitórias (%)',title='Vitórias por unidade de análise')
    for c in ax.containers: ax.bar_label(c,fmt='%.1f',padding=3,fontsize=8,color='#d8dfdf')
    ax.legend(title=None,frameon=False,loc='upper right',labelcolor='#d8dfdf')
    paths.append(save(fig,period,'anual'))
    # 2. Série mensal (meses sem dados aparecem como lacunas)
    monthly=mm.set_index('data').resample('MS')['vitoria'].agg(['mean','count'])
    x=np.arange(len(monthly))
    fig,ax=plt.subplots(figsize=(8,4.8))
    ax.plot(x,monthly['mean']*100,color=ACCENT,marker='o',markersize=4,linewidth=1.7)
    ax.fill_between(x,monthly['mean']*100,alpha=.10,color=ACCENT)
    ticks=np.unique(np.linspace(0,len(monthly)-1,min(7,len(monthly))).astype(int))
    ax.set_xticks(ticks,monthly.index[ticks].strftime('%m/%Y'),rotation=25)
    ax.set(ylim=(0,100),ylabel='Vitórias em mapas (%)',xlabel='Mês',title='Evolução mensal da taxa de vitória')
    paths.append(save(fig,period,'mensal'))
    # 3. Taxas de mapas e intervalos Wilson 95% (descritivos)
    pool=mm.groupby('mapa').vitoria.agg(['mean','count']).sort_values('mean')
    n=pool['count'].to_numpy(); rate=pool['mean'].to_numpy(); z=1.96
    center=(rate+z*z/(2*n))/(1+z*z/n)
    half=z*np.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/(1+z*z/n)
    fig,ax=plt.subplots(figsize=(8,4.8)); pos=np.arange(len(pool))
    ax.barh(pos,rate*100,color=ACCENT,alpha=.82)
    ax.errorbar(rate*100,pos,xerr=np.maximum(0,np.vstack([rate-(center-half),(center+half)-rate]))*100,fmt='none',ecolor='#eeeeec',capsize=3,lw=1)
    ax.set_yticks(pos,[f'{a} (n={int(c)})' for a,c in zip(pool.index,n)])
    ax.set(xlim=(0,100),xlabel='Vitórias em mapas (%) · intervalo Wilson 95%',title='Desempenho por mapa e tamanho da amostra')
    paths.append(save(fig,period,'mapas'))
    # 4. Distribuição de ADR de observações jogador-mapa
    fig,ax=plt.subplots(figsize=(8,4.8))
    sns.histplot(data=jj,x='adr',bins=np.arange(0,max(181,int(jj.adr.max())+11),10),color=ACCENT,edgecolor='#141618',ax=ax)
    median=float(np.median(jj.adr)); ax.axvline(median,color=LIGHT,ls='--',label=f'Mediana: {median:.1f}')
    ax.set(xlabel='ADR (dano médio por round)',ylabel='Registros jogador-mapa',title='Distribuição de ADR dos jogadores da FURIA')
    ax.legend(frameon=False,labelcolor='#d8dfdf')
    paths.append(save(fig,period,'adr'))
    # 5. Correlação com uma linha por mapa: evita replicar o resultado por jogador
    team=jj.groupby('mapstats_id').agg(ADR=('adr','mean'),KAST=('kast','mean'),Kills=('kills','sum'),Deaths=('deaths','sum'))
    team['K/D']=team.Kills/team.Deaths.replace(0,np.nan)
    joined=mm.set_index('mapstats_id')[['vitoria','rounds_furia','rounds_total']].join(team)
    joined['Rounds (%)']=joined.rounds_furia/joined.rounds_total
    corr=joined.rename(columns={'vitoria':'Vitória'})[['Vitória','Rounds (%)','ADR','KAST','K/D']].corr()
    fig,ax=plt.subplots(figsize=(8,4.8))
    sns.heatmap(corr,annot=True,fmt='.2f',vmin=-1,vmax=1,center=0,cmap=LinearSegmentedColormap.from_list('furia',[DARK,'#252528',ACCENT]),square=True,ax=ax,cbar_kws={'shrink':.8})
    ax.set_title('Associação entre resultado e estatísticas por mapa',pad=15)
    paths.append(save(fig,period,'correlacao'))
    # 6. Jogadores: ADR simples vs K/D agregado, tamanhos proporcionais à amostra
    players=jj.groupby('jogador').agg(ADR=('adr','mean'),kills=('kills','sum'),deaths=('deaths','sum'),mapas=('mapstats_id','count'))
    players['KD']=players.kills/players.deaths.replace(0,np.nan)
    fig,ax=plt.subplots(figsize=(8,4.8))
    sizes=80+players.mapas/players.mapas.max()*300
    ax.scatter(players.ADR,players.KD,s=sizes,c=ACCENT,alpha=.78,edgecolors='#eeeeec',linewidths=.7)
    ax.axhline(1,ls='--',color=GRAY,linewidth=.9)
    for i,(name,r) in enumerate(players.iterrows()):
        ax.annotate(f'{name} · {int(r.mapas)}', (r.ADR,r.KD),xytext=(5,7 if i%2 else -15),textcoords='offset points',fontsize=8)
    ax.margins(x=.24,y=.25)
    ax.set(xlabel='ADR médio por mapa',ylabel='K/D agregado',title='Jogadores: dano, eficiência e participação')
    paths.append(save(fig,period,'jogadores'))
    # 7. Saldo de rounds: bins de largura fixa e referência no zero
    diff=mm.rounds_furia-mm.rounds_adversario
    edges=np.arange(np.floor(diff.min()/2)*2-1,np.ceil(diff.max()/2)*2+3,2)
    fig,ax=plt.subplots(figsize=(8,4.8))
    counts,bins,patches=ax.hist(diff,bins=edges,edgecolor='#141618')
    for patch,left in zip(patches,bins):patch.set_facecolor(LIGHT if left+1>0 else DARK)
    ax.axvline(0,color='#e7eacc',ls='--',lw=1)
    ax.set(xlabel='Rounds FURIA − rounds adversário',ylabel='Quantidade de mapas',title='Margem dos resultados por mapa')
    paths.append(save(fig,period,'rounds'))
    # 8. Nuvem: nomes completos preservados, frequência medida por série
    freq=pp.adversario.value_counts().to_dict()
    cloud=WordCloud(width=1300,height=650,background_color='#141618',random_state=42,collocations=False,prefer_horizontal=.9,margin=8)
    cloud.generate_from_frequencies(freq)
    cloud.recolor(color_func=lambda word,**kwargs:[ACCENT,'#d7d7db',LIGHT,GRAY][int(hashlib.sha256(word.encode()).hexdigest()[:4],16)%4],random_state=42)
    fig,ax=plt.subplots(figsize=(8,4.8));ax.imshow(cloud,interpolation='bilinear');ax.axis('off');ax.set_title('Adversários mais frequentes em séries',pad=12)
    paths.append(save(fig,period,'nuvem'))
    manifest['periods'][period]={'series':len(pp),'maps':len(mm),'players_rows':len(jj),'images':[f.name for f in paths]}

(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'meta.js').write_text('window.PYTHON_META='+json.dumps(manifest,ensure_ascii=False)+';')
code_dir = ROOT/'dist/python'
code_dir.mkdir(exist_ok=True)
with ZipFile(code_dir/'codigo-graficos.zip','w',ZIP_DEFLATED) as archive:
    for relative in ['scripts/gerar_graficos.py','scripts/consultar_supabase.py','requirements.txt','dist/config.js']:
        archive.write(ROOT/relative,relative)
    archive.writestr('COMO_EXECUTAR.txt','Extraia na raiz do projeto. Execute: py -m pip install -r requirements.txt. Depois: py scripts/gerar_graficos.py. Publique novamente dist para atualizar o site online.')
print(json.dumps({'periodos':list(manifest['periods']),'graficos':sum(len(x['images']) for x in manifest['periods'].values()),'origem':'Supabase'},ensure_ascii=False))
