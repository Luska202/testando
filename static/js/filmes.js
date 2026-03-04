document.addEventListener('DOMContentLoaded', function() {
    const grid = document.getElementById('filmes-grid');
    const search = document.getElementById('search');
    const categoria = document.getElementById('categoria');
    const ordenar = document.getElementById('ordenar');

    function carregarFilmes() {
        const params = new URLSearchParams({
            search: search.value,
            categoria: categoria.value,
            order: ordenar.value
        });
        fetch(`/api/filmes?${params}`)
            .then(res => res.json())
            .then(filmes => {
                grid.innerHTML = filmes.map(f => `
                    <div class="card" data-id="${f.id}" data-tipo="filme">
                        <img src="${f.logo_url}" alt="${f.titulo}">
                        <h3>${f.titulo}</h3>
                    </div>
                `).join('');
                document.querySelectorAll('.card').forEach(card => {
                    card.addEventListener('click', () => {
                        window.location.href = `/filme/${card.dataset.id}`;
                    });
                });
            });
    }

    search.addEventListener('input', carregarFilmes);
    categoria.addEventListener('change', carregarFilmes);
    ordenar.addEventListener('change', carregarFilmes);
    carregarFilmes();
});