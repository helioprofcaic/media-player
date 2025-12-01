// =================================================================
// INICIALIZAÇÃO E DEFINIÇÃO DE VARIÁVEIS
// =================================================================
const socket = io();
const player = document.getElementById('player');
const slideshow = document.getElementById('slideshow');
const toggleBtn = document.getElementById('toggle-controls-btn');
const playerContainer = document.getElementById('player-container');
const qrcodeContainer = document.getElementById('qrcode-container');
const mainNowPlayingContainer = document.getElementById('main-now-playing');
const mainSongTitle = document.getElementById('main-song-title');
const fullscreenBtn = document.getElementById('fullscreen-btn');
let currentTrack = 0;
let currentImage = 0;
let playlist = [];
let imageList = [];
let slideshowIntervalId; // Variável para armazenar o ID do setInterval do slideshow
let currentSlideshowInterval = 10000; // 10 segundos (padrão)

let songTitleTimeout; // Variável para controlar o temporizador

// Função para notificar o servidor sobre a música atual
function notifyNowPlaying() {
    if (playlist.length > 0) {
        socket.emit('now-playing', { song: playlist[currentTrack] });
    }
}

// Função para notificar o servidor sobre a imagem atual
function notifyCurrentImage() {
    if (imageList.length > 0) {
        socket.emit('current-image', { image: imageList[currentImage] });
    }
}

// Função para atualizar o nome da música na tela principal
function updateMainDisplaySong() {
    if (playlist.length > 0 && mainSongTitle) {
        const songName = playlist[currentTrack].replace('.mp3', '');
        mainSongTitle.textContent = songName;

        // Limpa qualquer temporizador anterior para garantir que o novo prevaleça
        clearTimeout(songTitleTimeout);

        // Mostra o nome da música
        mainNowPlayingContainer.style.opacity = 1; // Faz o nome aparecer

        // Define um temporizador para esconder o nome da música após 30 segundos
        songTitleTimeout = setTimeout(() => {
            mainNowPlayingContainer.style.opacity = 0;
        }, 30000); // 30000 milissegundos = 30 segundos
    } else if (mainNowPlayingContainer) {
        mainNowPlayingContainer.style.opacity = 0; // Esconde se não houver música
    }
}


// =================================================================
// COMUNICAÇÃO COM O SERVIDOR (Socket.IO)
// =================================================================

// Ouve o evento 'update-lists' para receber as listas de músicas e imagens do servidor.
socket.on('update-lists', (data) => {
    playlist = data.playlist;
    imageList = data.imageList;
    
    // Inicia a primeira música da playlist.
    // O .catch() previne um erro caso o navegador bloqueie o autoplay.
    if (playlist.length > 0) {
        player.src = '/musicas/' + playlist[currentTrack];
        player.play().catch(e => console.log("Autoplay bloqueado pelo navegador. Use o controle."));
        notifyNowPlaying(); // Notifica a primeira música
        updateMainDisplaySong(); // Atualiza a tela principal
    }

    // Exibe a primeira imagem do slideshow imediatamente.
    if (imageList.length > 0) slideshow.src = '/imagens/' + imageList[currentImage]; 
    notifyCurrentImage(); // Notifica a primeira imagem
});

// Ouve por comandos de controle ('play', 'pause', 'next') vindos do servidor.
socket.on('playback-control', (data) => {
    switch(data.action) {
        case 'play':
            player.play();
            break;
        case 'pause':
            player.pause();
            break;
        case 'previous':
            if (playlist.length > 0) {
                currentTrack = (currentTrack - 1 + playlist.length) % playlist.length;
                player.src = '/musicas/' + playlist[currentTrack];
                player.play();
                notifyNowPlaying(); // Notifica a nova música
                updateMainDisplaySong(); // Atualiza a tela principal
            }
            break;
        case 'next':
            currentTrack = (currentTrack + 1) % playlist.length;
            player.src = '/musicas/' + playlist[currentTrack];
            player.play();
            notifyNowPlaying(); // Notifica a nova música
            updateMainDisplaySong(); // Atualiza a tela principal
            break;
    }
});

// Ouve por atualizações de volume vindas do servidor.
socket.on('volume-update', (data) => {
    // O valor do slider vai de 0 a 100, mas o player.volume vai de 0.0 a 1.0.
    // Por isso, dividimos por 100.
    player.volume = data.volume / 100;
});

// Ouve as informações do servidor para gerar o QR Code corretamente
socket.on('server-info', (data) => {
    // Gera o QR Code para o controle remoto assim que receber o IP do servidor.
    const controlUrl = `http://${data.ip}:${data.port}/controle.html`;
    
    // Limpa qualquer QR Code antigo antes de gerar um novo
    document.getElementById("qrcode").innerHTML = '';

    new QRCode(document.getElementById("qrcode"), {
        text: controlUrl,
        width: 128,
        height: 128,
    });
});

// =================================================================
// LÓGICA DO SLIDESHOW E PLAYER
// =================================================================

// Configura o slideshow para trocar de imagem automaticamente a cada 5 segundos com efeito de fade.
function startSlideshow() {
    if (slideshowIntervalId) clearInterval(slideshowIntervalId); // Limpa o intervalo anterior
    slideshowIntervalId = setInterval(() => {
    // Só executa a troca se houver mais de uma imagem na lista.
    if (imageList.length > 1) {
        currentImage = (currentImage + 1) % imageList.length;

        // 1. Torna a imagem atual transparente (inicia o fade-out)
        slideshow.style.opacity = 0;

        // 2. Espera o fade-out terminar para trocar a imagem e iniciar o fade-in
        setTimeout(() => {
            slideshow.src = '/imagens/' + imageList[currentImage];
            // 3. Torna a nova imagem visível (inicia o fade-in)
            slideshow.style.opacity = 1;
            notifyCurrentImage(); // Notifica a nova imagem
        }, 1000); // Este tempo deve ser igual ao da transição no CSS
    }
}, currentSlideshowInterval); // <--- CORREÇÃO: Adicionado o tempo do intervalo aqui
}
startSlideshow(); // Inicia o slideshow ao carregar a página

// =================================================================
// Adiciona um listener que toca a próxima música quando a atual terminar.
player.addEventListener('ended', () => {
    if (playlist.length > 0) {
        currentTrack = (currentTrack + 1) % playlist.length;
        player.src = '/musicas/' + playlist[currentTrack];
        player.play();
        notifyNowPlaying(); // Notifica a nova música
        updateMainDisplaySong(); // Atualiza a tela principal
    }
});


// =================================================================
// FUNCIONALIDADES DA INTERFACE (UI)
// =================================================================

// Adiciona a lógica para o botão que mostra e oculta os painéis de controle.
toggleBtn.addEventListener('click', () => {
    const isHidden = playerContainer.classList.contains('hidden');
    // Limpa o temporizador de auto-ocultar se o usuário interagir com o botão
    if (autoHideTimeout) clearTimeout(autoHideTimeout);

    if (isHidden) {
        playerContainer.classList.remove('hidden');
        qrcodeContainer.classList.remove('hidden');
        toggleBtn.textContent = 'Ocultar Controles';
    } else {
        playerContainer.classList.add('hidden');
        qrcodeContainer.classList.add('hidden');
        toggleBtn.textContent = 'Mostrar Controles';
    }
});

// Lógica para auto-ocultar os controles após 30 segundos
let autoHideTimeout;

function autoHideControls() {
    // Oculta os painéis
    playerContainer.classList.add('hidden');
    qrcodeContainer.classList.add('hidden');
    // Atualiza o texto do botão
    toggleBtn.textContent = 'Mostrar Controles';
}

// Inicia o temporizador quando a página carrega
autoHideTimeout = setTimeout(autoHideControls, 30000); // 30 segundos

// Adiciona a lógica para o botão de tela cheia.
fullscreenBtn.addEventListener('click', () => {
    if (!document.fullscreenElement) {
        // Se não estiver em tela cheia, entra em tela cheia.
        document.documentElement.requestFullscreen().catch(err => {
            alert(`Erro ao tentar entrar em tela cheia: ${err.message} (${err.name})`);
        });
        fullscreenBtn.textContent = 'Sair da Tela Cheia';
    } else {
        // Se já estiver em tela cheia, sai.
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        fullscreenBtn.textContent = 'Tela Cheia';
    }
});

// Lógica para controle do intervalo do slideshow
document.addEventListener('DOMContentLoaded', () => {
    const intervalValueSpan = document.getElementById('interval-value');
    const increaseBtn = document.getElementById('interval-increase');
    const decreaseBtn = document.getElementById('interval-decrease');
    const minInterval = 5;
    const maxInterval = 20;

    // Função para atualizar a exibição e reiniciar o slideshow
    function updateInterval(newSeconds) {
        currentSlideshowInterval = newSeconds * 1000;
        intervalValueSpan.textContent = `${newSeconds}s`;
        startSlideshow();
    }

    // Define o valor inicial
    intervalValueSpan.textContent = `${currentSlideshowInterval / 1000}s`;

    increaseBtn.addEventListener('click', () => {
        let currentSeconds = currentSlideshowInterval / 1000;
        if (currentSeconds < maxInterval) updateInterval(currentSeconds + 1);
    });

    decreaseBtn.addEventListener('click', () => {
        let currentSeconds = currentSlideshowInterval / 1000;
        if (currentSeconds > minInterval) updateInterval(currentSeconds - 1);
    });
});

// Lógica para controle do ajuste da imagem (object-fit)
const imageFitSelect = document.getElementById('image-fit');

// Define o valor inicial do select com base no CSS (que é 'cover' por padrão)
imageFitSelect.value = slideshow.style.objectFit || 'cover';

imageFitSelect.addEventListener('change', (event) => {
    slideshow.style.objectFit = event.target.value;
});

// Garante que o object-fit inicial seja 'cover'
slideshow.style.objectFit = 'cover';