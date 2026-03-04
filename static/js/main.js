document.addEventListener('click', function(e) {
    if (e.target.classList.contains('favorito-btn')) {
        const btn = e.target;
        const id = btn.dataset.id;
        const tipo = btn.dataset.tipo;
        const acao = btn.classList.contains('favorito-ativo') ? 'remove' : 'add';
        fetch('/favoritar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acao, id, tipo })
        }).then(() => {
            btn.classList.toggle('favorito-ativo');
        });
    }
});