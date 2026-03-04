const video = document.getElementById('meuVideo');
const videoId = video.dataset.id;
const tipo = video.dataset.tipo;
let temporada = video.dataset.temporada; // para séries
let episodio = video.dataset.episodio;

// Recuperar progresso salvo
fetch(`/api/progresso?tipo=${tipo}&id=${videoId}&temp=${temporada}&ep=${episodio}`)
    .then(res => res.json())
    .then(data => {
        if (data.tempo) {
            video.currentTime = data.tempo;
        }
    });

// Salvar progresso a cada 30 segundos
setInterval(() => {
    const tempo = video.currentTime;
    const duracao = video.duration;
    fetch('/api/salvar_progresso', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            tipo, id: videoId, temporada, episodio,
            tempo_assistido: Math.floor(tempo),
            duracao_total: Math.floor(duracao)
        })
    });
}, 30000);

// Ao fechar a página, salvar uma última vez
window.addEventListener('beforeunload', () => {
    // Síncrono não é possível, mas podemos usar beacon
    navigator.sendBeacon('/api/salvar_progresso', JSON.stringify({...}));
});