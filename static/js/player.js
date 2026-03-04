document.addEventListener('DOMContentLoaded', function() {
    // Verifica se está na página de player
    const video = document.getElementById('player');
    if (!video) return;

    const videoId = video.dataset.id;
    const tipo = video.dataset.tipo;
    const temporada = video.dataset.temporada;
    const episodio = video.dataset.episodio;

    // Carregar progresso salvo
    const params = new URLSearchParams({ tipo, id: videoId });
    if (temporada) params.append('temporada', temporada);
    if (episodio) params.append('episodio', episodio);

    fetch(`/api/progresso?${params}`)
        .then(res => res.json())
        .then(data => {
            if (data.tempo) {
                video.currentTime = data.tempo;
            }
        });

    // Salvar progresso a cada 30 segundos
    let saveInterval = setInterval(() => {
        if (!video.paused && !video.ended) {
            salvarProgresso();
        }
    }, 30000);

    // Salvar ao sair da página
    window.addEventListener('beforeunload', function() {
        clearInterval(saveInterval);
        salvarProgressoBeacon();
    });

    function salvarProgresso() {
        const tempo = Math.floor(video.currentTime);
        const duracao = Math.floor(video.duration);
        fetch('/api/salvar_progresso', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: videoId,
                tipo: tipo,
                temporada: temporada,
                episodio: episodio,
                tempo_assistido: tempo,
                duracao_total: duracao
            })
        });
    }

    function salvarProgressoBeacon() {
        const tempo = Math.floor(video.currentTime);
        const duracao = Math.floor(video.duration);
        const data = JSON.stringify({
            id: videoId,
            tipo: tipo,
            temporada: temporada,
            episodio: episodio,
            tempo_assistido: tempo,
            duracao_total: duracao
        });
        navigator.sendBeacon('/api/salvar_progresso', data);
    }
});