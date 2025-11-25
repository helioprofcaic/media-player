const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process'); // Importa a função 'spawn'
const open = require('open');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const musicDir = path.join(__dirname, 'musicas');
const imageDir = path.join(__dirname, 'imagens');

app.use(express.static('public'));
app.use('/musicas', express.static(musicDir));
app.use('/imagens', express.static(imageDir));

let playlist = [];
let imageList = [];

// Função para ler as mídias e atualizar as listas
function updateMediaLists() {
    fs.readdir(musicDir, (err, files) => {
        if (err) return console.log('Erro ao ler pasta de músicas:', err);
        playlist = files.filter(file => file.endsWith('.mp3'));
        // Notifica todos os clientes sobre a nova lista de músicas
        io.emit('update-lists', { playlist, imageList });
    });

    fs.readdir(imageDir, (err, files) => {
        if (err) return console.log('Erro ao ler pasta de imagens:', err);
        imageList = files.filter(file => file.endsWith('.png') || file.endsWith('.jpg'));
    });
}

// Lê as mídias na inicialização
updateMediaLists();

// Comunicação via WebSocket
io.on('connection', (socket) => {
    console.log('Um cliente se conectou');

    // Envia as listas de mídia para os clientes
    socket.emit('update-lists', { playlist, imageList });

    // Ouve por comandos do controle remoto e os retransmite para todos
    socket.on('control-action', (data) => {
        io.emit('playback-control', data);
        console.log('Comando recebido:', data);
    });

    // Ouve da tela qual música está tocando e retransmite para todos
    socket.on('now-playing', (data) => {
        // Retransmite para todos os clientes, incluindo o controle
        io.emit('now-playing-update', data);
    });

    // Ouve por mudanças no volume e retransmite para todos
    socket.on('volume-change', (data) => {
        io.emit('volume-update', data);
    });

    // Ouve da tela qual imagem está sendo exibida e retransmite para todos os controles
    socket.on('current-image', (data) => {
        io.emit('background-image-update', data);
    });

    // Ouve pelo evento de download da playlist
    socket.on('launch-downloader', () => {
        console.log(`Iniciando o script de download do Python...`);

        // Executa o seu script Python.
        // Substitua 'seu_script.py' pelo nome real do seu script.
        // O primeiro argumento é 'python' ou 'python3', dependendo da sua instalação.
        const pythonProcess = spawn('python', ['download_playlist_360p.py']);

        // Ouve a saída padrão do script (para logs e status)
        pythonProcess.stdout.on('data', (output) => {
            console.log(`[Python Script]: ${output}`);
        });

        // Ouve por erros
        pythonProcess.stderr.on('data', (output) => {
            console.error(`[Python Script Error]: ${output}`);
        });

        // Quando o script terminar de executar
        pythonProcess.on('close', (code) => {
            console.log(`Script Python finalizado com código ${code}.`);
            // Atualiza a lista de músicas e envia para todos os clientes
            updateMediaLists();
        });
    });
});

const PORT = 5000;

// Função para encontrar o endereço IP local na rede
function getLocalIpAddress() {
    const interfaces = os.networkInterfaces();
    let localIp = null;
    let fallbackIp = null; // Para guardar o primeiro IP válido encontrado

    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            // Pula endereços que não são IPv4 ou são internos (ex: 127.0.0.1)
            if (iface.family === 'IPv4' && !iface.internal) {
                // Prioridade 1: Encontrar o IP da rede Wi-Fi local (192.168.0.x)
                if (iface.address.startsWith('192.168.0.')) {
                    localIp = iface.address;
                    break; // Encontrou o melhor IP, pode parar de procurar nesta interface
                }
                // Prioridade 2: Guardar o primeiro IP válido como um plano B
                if (!fallbackIp) {
                    fallbackIp = iface.address;
                }
            }
        }
        if (localIp) break; // Encontrou o melhor IP, pode parar de procurar em outras interfaces
    }
    return localIp || fallbackIp || 'localhost';
}

const localIp = getLocalIpAddress();

server.listen(PORT, '0.0.0.0', () => {
    console.log(`\nServidor rodando! Acesse de outros dispositivos na mesma rede:`);
    console.log(`- Tela (TV):      http://${localIp}:${PORT}`);
    console.log(`- Controle (Celular): http://${localIp}:${PORT}/controle.html`);
    console.log(`\nOu use o QR Code que aparece na tela da TV.`);

    // Abre o navegador na tela principal automaticamente
    open(`http://localhost:${PORT}`);
});
