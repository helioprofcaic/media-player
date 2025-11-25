# Media Player para Feira de Profissões

## 1. Visão Geral

Este projeto é um media player desenvolvido para ser usado na recepção de eventos, como a feira de profissões. Ele toca uma lista de músicas (arquivos MP3) enquanto exibe um slideshow de imagens (arquivos PNG/JPG) em uma tela principal, como uma Smart TV.

O grande diferencial é o controle total da reprodução através de uma interface web simples, acessível pelo navegador de um celular, que funciona como um controle remoto.

## 2. Arquitetura

A aplicação é construída sobre uma arquitetura cliente-servidor, utilizando Node.js no backend.

-   **Servidor (Computador/Notebook Windows):**
    -   Tecnologia: **Node.js** com a biblioteca **Express.js**.
    -   Responsabilidades:
        -   Servir os arquivos estáticos (HTML, CSS, JS) para os clientes.
        -   Ler as pastas `musicas` e `imagens` para criar as playlists dinamicamente.
        -   Gerenciar a comunicação em tempo real entre o controle remoto e a tela de exibição usando **Socket.IO**.

-   **Cliente de Exibição (Navegador da Smart TV):**
    -   Acessa a página principal (`index.html`).
    -   Exibe o slideshow de imagens e contém o player de áudio.
    -   Recebe comandos do servidor (via Socket.IO) para tocar, pausar ou pular músicas.
    -   **Funcionalidades da Interface:**
        -   Exibe o nome da música atual no canto da tela, desaparecendo após 30 segundos.
        -   Um painel de controle ocultável permite:
            -   Controle de áudio local.
            -   Ativar o modo de tela cheia.
            -   Ajustar o intervalo do slideshow (5 a 20 segundos).
            -   Alterar o modo de ajuste da imagem (Preencher, Ajustar ou Esticar).
    -   **Observação:** Devido às políticas de autoplay dos navegadores, a música só começará a tocar após uma interação do usuário (ex: clique no botão Play do controle remoto).

-   **Cliente de Controle (Navegador do Celular):**
    -   Acessa a página de controle (`controle.html`).
    -   Exibe botões de ação (Play, Pause, Próxima, Anterior).
    -   Envia comandos para o servidor (via Socket.IO) quando um botão é pressionado.
    -   **Nova Funcionalidade:** Exibe o nome da música que está tocando.
    -   **Nova Funcionalidade:** Permite o controle de volume através de um slider.
    -   **Nova Funcionalidade:** Exibe a imagem do slideshow atual como um fundo escurecido, sincronizando a experiência visual.

## 3. Estrutura de Pastas

```
/media-player
|-- /docs               # Documentação do projeto
|-- /musicas            # Onde os arquivos MP3 devem ser colocados
|-- /imagens            # Onde os arquivos de imagem (PNG, JPG) devem ser colocados
|-- /node_modules       # Dependências do Node.js (gerenciado pelo npm)
|-- /public             # Arquivos acessíveis pelo navegador
|   |-- /css
|   |-- /js
|   |-- index.html      # Tela de exibição (para a TV)
|   `-- controle.html   # Interface de controle (para o celular)
|-- .gitignore          # Arquivos a serem ignorados pelo Git
|-- package.json        # Define o projeto e suas dependências
|-- package-lock.json   # Grava as versões exatas das dependências
`-- server.js           # Lógica principal do servidor
```

## 4. Guia de Instalação e Execução

1.  **Pré-requisitos:** É necessário ter o [Node.js](https://nodejs.org/) e o [Python](https://www.python.org/) instalados.
    -   Para a funcionalidade de download de músicas, é necessário ter o **yt-dlp** e o **ffmpeg**. A forma mais fácil de instalá-los no Windows é usando os seguintes comandos no seu terminal (PowerShell ou CMD):
        -   **Para instalar/atualizar o yt-dlp:**
            ```bash
            python -m pip install -U "yt-dlp[default]"
            ```
        -   **Para instalar o ffmpeg (usando o Gerenciador de Pacotes do Windows):**
            ```bash
            winget install "FFmpeg (Essentials Build)"
            ```
    -   Após a instalação, reinicie o terminal para garantir que os programas sejam reconhecidos pelo sistema.

2.  **Instalação:** Clone o repositório e, na pasta raiz do projeto, instale as dependências com o comando:
    ```bash
    npm install
    ```
3.  **Configuração do Firewall (Windows):**
    Para que o celular possa se conectar ao computador, é necessário permitir a porta `5000` no Firewall do Windows.
    -   Abra o "Windows Defender Firewall com Segurança Avançada".
    -   Crie uma "Nova Regra de Entrada" para "Porta".
    -   Selecione "TCP" e digite `5000` como "Portas locais específicas".
    -   Permita a conexão para todos os perfis (Domínio, Particular, Público).
    -   Dê um nome à regra (ex: "Media Player Feira - Porta 5000").

4.  **Execução:** Para iniciar o servidor, execute:
    ```bash
    npm start
    ```
    O console exibirá os endereços IP corretos para acesso.

5.  **Acesso:**
    -   Certifique-se de que o computador, a TV e o celular estejam na **mesma rede Wi-Fi**.
    -   **Na TV:** Abra o navegador e acesse o endereço fornecido no console (ex: `http://<IP_DO_COMPUTADOR>:5000`). Um QR Code aparecerá na tela.
    -   **No Celular:** Use a câmera para escanear o QR Code na tela da TV. Ele o levará diretamente para a página de controle (ex: `http://<IP_DO_COMPUTADOR>:5000/controle.html`).

6.  **Saída de Áudio:**
    O som das músicas será reproduzido pelo dispositivo que está exibindo a tela principal (`index.html`).
    -   **Se a tela for uma Smart TV:** O som sairá pelos alto-falantes da TV.
    -   **Se a tela for o próprio notebook servidor:** O som sairá pelo dispositivo de áudio padrão do notebook. Isso permite que você conecte caixas de som externas, fones de ouvido ou uma **caixa de som via Bluetooth** para ter um som de melhor qualidade no ambiente.

    Basta configurar o dispositivo de áudio desejado como o padrão no sistema operacional antes de abrir o navegador na tela principal.

## 5. Solução de Problemas (Troubleshooting)
