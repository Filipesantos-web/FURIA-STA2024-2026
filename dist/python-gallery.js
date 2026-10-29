(function(){
const charts=[
['anual','Vitórias por ano','Matplotlib + Seaborn','Compara taxas em séries, mapas e rounds. O período de 2026 é parcial.'],
['mensal','Evolução mensal','Pandas + Matplotlib','Taxa de vitória em mapas por mês; meses sem partidas permanecem como lacunas.'],
['mapas','Desempenho por mapa','NumPy + Matplotlib','Taxa de vitória e intervalo Wilson de 95%. A amostra n aparece ao lado de cada mapa; o intervalo é descritivo e pressupõe observações independentes.'],
['adr','Distribuição de ADR','Seaborn + NumPy','Cada observação é um jogador em um mapa. A linha indica a mediana; os cinco jogadores do mesmo mapa não são observações independentes.'],
['correlacao','Matriz de correlação','Pandas + Seaborn','Correlação de Pearson entre estatísticas agregadas por mapa. Associação não demonstra causalidade; rounds vencidos também compõem o resultado.'],
['jogadores','Comparativo de jogadores','Pandas + Matplotlib','ADR médio versus K/D agregado. O tamanho dos pontos representa mapas disputados; nomes e amostras aparecem nas etiquetas.'],
['rounds','Saldo de rounds','NumPy + Matplotlib','Distribuição da diferença de rounds por mapa. Valores positivos representam vitórias e negativos, derrotas.'],
['nuvem','Nuvem de adversários','WordCloud + Pandas','O tamanho de cada nome representa a frequência de confrontos em séries, não a dificuldade do adversário nem a quantidade de vitórias.']
];
window.renderPythonGallery=function(year){
 const meta=window.PYTHON_META;const period=meta?.periods?.[year];
 if(!period)return '<div class="note">Não há gráficos Python gerados para este período.</div>';
 const label=year==='all'?'2024–2026':year;
 const generated=new Date(meta.generated_at).toLocaleString('pt-BR');
 return `<section class="python-intro"><div><span class="eyebrow">ANÁLISE EXPLORATÓRIA / PYTHON</span><h2>Mais perspectivas.<br>Mais contexto para o jogo<span>.</span></h2><p>Oito visualizações para explorar os dados da FURIA.</p></div><div class="python-tools">${['Pandas','NumPy','Matplotlib','Seaborn','WordCloud'].map(x=>`<span>${x}</span>`).join('')}</div></section>
 <div class="note"><strong>Gráficos gerados em Python · ${label}</strong><br>Retrato do Supabase gerado em ${generated}, com ${period.series} séries e ${period.maps} mapas. O filtro de ano seleciona imagens previamente geradas. Estes gráficos não mudam ao clicar em “Atualizar dados”; para atualizá-los, execute o script Python.<br><a href="python/codigo-graficos.zip" download>↓ Baixar código Python e dependências</a></div>
 <div class="python-grid">${charts.map(([id,title,lib,desc],i)=>`<article class="python-card"><div class="paneltop"><div><span class="eyebrow">${String(i+1).padStart(2,'0')} / ${label}</span><h3>${title}</h3></div><span class="tag">PYTHON</span></div><button class="chart-preview" data-python-chart="${id}" aria-label="Ampliar ${title}"><img src="graficos/${year}_${id}.png" alt="${title} da FURIA, período ${label}" loading="lazy"><span>Ampliar ↗</span></button><div class="python-caption"><span class="library-badge">${lib}</span><p>${desc}</p><a href="graficos/${year}_${id}.png" download>↓ Baixar PNG</a></div></article>`).join('')}</div>`;
};
document.addEventListener('click',e=>{
 const button=e.target.closest('[data-python-chart]');if(!button)return;
 const id=button.dataset.pythonChart;const image=button.querySelector('img');const info=charts.find(c=>c[0]===id);if(!info)return;
 let dialog=document.querySelector('#python-modal');if(!dialog){dialog=document.createElement('dialog');dialog.id='python-modal';document.body.append(dialog);dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()})}
 dialog.innerHTML=`<div class="modal-top"><h2>${info[1]}</h2><button class="export" id="close-chart">Fechar ×</button></div><img src="${image.getAttribute('src')}" alt="${image.alt}"><p>${info[3]}</p><a href="${image.getAttribute('src')}" download>↓ Baixar imagem PNG</a>`;
 dialog.querySelector('#close-chart').onclick=()=>dialog.close();dialog.showModal();
});
})();
