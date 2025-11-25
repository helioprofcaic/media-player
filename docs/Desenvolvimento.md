# Guia de Desenvolvimento

Este documento detalha a arquitetura técnica e o fluxo de dados do projeto Media Player, servindo como um guia para futuros desenvolvedores.

## 1. Backend (`server.js`)

O servidor é o coração da aplicação, responsável por coordenar a comunicação entre a tela de exibição e os controles remotos.

### Inicialização
-   **Express.js:** Utilizado para servir os arquivos estáticos da pasta `public` e as mídias das pastas `musicas` e `imagens`.
-   **Socket.IO:** Acoplado ao servidor HTTP para permitir comunicação bidirecional em tempo real.
-   **open:** Utilizado para abrir automaticamente o navegador na tela principal após o servidor iniciar, melhorando a usabilidade.
-   **Leitura de Arquivos:** Ao iniciar, o servidor usa o módulo `fs` para ler o conteúdo das pastas `/musicas` e `/imagens`, montando as listas de reprodução (`playlist` e `imageList`) que serão enviadas aos clientes.

### Lógica de Rede
-   **Detecção de IP (`getLocalIpAddress`)**: Uma função customizada foi criada para encontrar o endereço IP correto da máquina na rede local (Wi-Fi). Ela é projetada para ignorar adaptadores de rede virtuais (como os do VirtualBox ou WSL) e priorizar o IP da rede `192.168.0.x`, garantindo que o QR Code e os links gerados funcionem corretamente.
-   **Binding (`server.listen`):** O servidor escuta em `0.0.0.0`, o que o torna acessível a partir de qualquer dispositivo na rede, não apenas `localhost`.

### Eventos do Socket.IO (Lado do Servidor)

O servidor atua como um grande "roteador" de eventos.

-   `io.on('connection', ...)`: Disparado quando um novo cliente (tela ou controle) se conecta.
    -   `socket.emit('update-lists', ...)`: Envia as listas de músicas e imagens para o cliente que acabou de se conectar.

-   `socket.on('control-action', ...)`: Ouve um comando do controle remoto (`play`, `pause`, `next`, `previous`).
    -   `io.emit('playback-control', ...)`: Retransmite o comando para **todos** os clientes (especialmente para a tela de exibição).

-   `socket.on('now-playing', ...)`: Ouve da tela principal qual música está tocando.
    -   `io.emit('now-playing-update', ...)`: Retransmite o nome da música para **todos** os clientes (especialmente para o controle remoto).

-   `socket.on('current-image', ...)`: Ouve da tela principal qual imagem está sendo exibida.
    -   `io.emit('background-image-update', ...)`: Retransmite o nome da imagem para **todos** os clientes (especialmente para o controle remoto).

-   `socket.on('volume-change', ...)`: Ouve do controle remoto uma alteração de volume.
    -   `io.emit('volume-update', ...)`: Retransmite o novo valor de volume para **todos** os clientes (especialmente para a tela de exibição).

-   `socket.on('launch-downloader', ...)`: Ouve um comando do controle remoto para iniciar o downloader.
    -   Usa a função `spawn` do Node.js para executar um script Python (`download_playlist_360p.py`) que abre sua própria interface gráfica no servidor.
    -   `pythonProcess.on('close', ...)`: Quando a aplicação Python é fechada pelo usuário, este evento é disparado, e o servidor chama a função `updateMediaLists()` para recarregar a lista de músicas e notificar todos os clientes.

---

## 2. Frontend - Tela de Exibição (`public/js/main.js`)

Este script controla toda a lógica da tela principal (`index.html`).

### Lógica de Reprodução
-   **Slideshow:** Um `setInterval` é responsável por trocar as imagens. A cada 10 segundos, ele:
    1.  Define a opacidade da imagem atual para `0` (iniciando o *fade-out*).
    2.  Usa um `setTimeout` de 1 segundo para esperar a transição terminar.
    3.  Troca o `src` da imagem e define a opacidade de volta para `1` (iniciando o *fade-in*).
    4.  Chama a função `notifyCurrentImage()` para avisar o servidor da nova imagem.
-   **Player de Áudio:** Um `event listener` no evento `ended` do player de áudio detecta quando uma música termina e automaticamente avança para a próxima da lista.

### Comunicação
-   O script se conecta ao servidor via Socket.IO e ouve por eventos como `playback-control` e `volume-update` para manipular o player de áudio.
-   Ele também envia eventos para o servidor (`now-playing`, `current-image`) sempre que o estado da mídia local é alterado, mantendo os controles remotos sincronizados.

### Interface (UI)
-   **QR Code:** Utiliza a biblioteca `qrcode.js` para gerar dinamicamente o QR Code com a URL de controle correta.
-   **Painel de Controle Ocultável:** Um botão principal (`#toggle-controls-btn`) alterna a classe `.hidden` nos contêineres do player e do QR Code. O painel de controle local contém:
    -   **Tela Cheia:** Um botão que utiliza a API `Fullscreen` do navegador para entrar e sair do modo de tela cheia.
    -   **Intervalo do Slideshow:** Um `input type="range"` que permite ao usuário alterar o tempo de exibição das imagens. Ele atualiza uma variável e reinicia o `setInterval` do slideshow com o novo valor.
    -   **Ajuste de Imagem:** Um `select` que altera a propriedade `object-fit` do elemento `#slideshow`, permitindo ao usuário escolher entre `cover` (padrão), `contain` e `fill`.
-   **Nome da Música na Tela:** Uma `div` (`#main-now-playing`) exibe o nome da música atual. Uma função `updateMainDisplaySong` é chamada sempre que a música muda, exibindo o nome e iniciando um `setTimeout` de 30 segundos para ocultá-lo novamente, mantendo a tela limpa.
---

## 3. Frontend - Controle Remoto (`public/controle.html`)

A página de controle é uma interface simples, mas poderosa, para interagir com a tela principal.

### Lógica
-   O script está embutido no HTML para simplicidade.
-   **Envio de Ações:** Cada botão (`Play`, `Pause`, etc.) e o slider de volume chamam funções JavaScript que emitem o evento correspondente para o servidor (`control-action`, `volume-change`).
-   **Recebimento de Estado:** O script ouve por eventos do servidor para se manter atualizado:
    -   `now-playing-update`: Recebe o nome da música atual e o exibe na tela.
    -   `background-image-update`: Recebe a URL da imagem atual e a aplica como imagem de fundo do `body`, criando uma experiência visualmente conectada.

### Estilo (`public/css/controle.css`)
-   O design é focado em "mobile-first", com botões grandes e circulares para facilitar o toque.
-   Um pseudo-elemento `body::before` é usado para criar um *overlay* escuro sobre a imagem de fundo, garantindo que o texto e os controles permaneçam legíveis e com bom contraste.