# Media Player para Feira de Profissões ✨

<!-- Sugestão: Adicione aqui uma imagem ou GIF do media player em funcionamento. -->
![Demonstração do Media Player](docs/player-demo.gif) 

## ✨ 1. Visão Geral

Este projeto é um media player com controle remoto via celular, ideal para a recepção de eventos como feiras de profissões. Ele reproduz uma lista de músicas e um slideshow de imagens em uma tela principal (como uma Smart TV), enquanto o controle total da reprodução é feito por uma interface web acessível pelo navegador de qualquer celular na mesma rede Wi-Fi.

A arquitetura é baseada em Node.js, garantindo comunicação em tempo real entre o "controle remoto" (celular) e a "tela" (TV).

## 🚀 2. Principais Funcionalidades

#### Tela de Exibição (TV / Monitor)
- Exibição de slideshow de imagens em tela cheia.
- Reprodução de playlist de músicas em MP3.
- Nome da música atual aparece no canto da tela e some após 30 segundos.
- Painel de controle local (ocultável) para:
  - Ativar modo de tela cheia.
  - Ajustar o intervalo do slideshow (5 a 20 segundos).
  - Alterar o modo de ajuste da imagem (Preencher, Ajustar, Esticar).
- Geração de QR Code para acesso rápido do controle remoto.
 
#### Controle Remoto (Celular)
- Controles básicos de reprodução (Play, Pause, Próxima, Anterior).
- Ajuste de volume com um slider.
- Exibição do nome da música que está tocando.
- Sincronização visual: a imagem do slideshow aparece como fundo de tela no celular.
- Botão para iniciar uma interface no servidor que permite baixar músicas de playlists do YouTube.

## 📁 3. Estrutura de Pastas

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

## ️ 4. Guia de Instalação e Execução

1.  **✅ Pré-requisitos:** É necessário ter o [Node.js](https://nodejs.org/) e o [Python](https://www.python.org/) instalados.
    -   Para a funcionalidade de download de músicas, é necessário ter o **yt-dlp** e o **ffmpeg**. A forma mais fácil de instalá-los no Windows é usando os seguintes comandos no seu terminal (PowerShell ou CMD) para garantir que estejam no PATH:
        -   **Para instalar/atualizar o yt-dlp:**
            ```bash
            python -m pip install -U "yt-dlp[default]"
            ```
        -   **Para instalar o ffmpeg (usando o Gerenciador de Pacotes do Windows):**
            ```bash
            winget install "FFmpeg (Essentials Build)"
            ```
    -   Após a instalação, reinicie o terminal para garantir que os programas sejam reconhecidos pelo sistema.

2.  **📦 Instalação:** Clone o repositório e, na pasta raiz do projeto, instale as dependências do Node.js com o comando:
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

4.  **▶️ Execução:** Para iniciar o servidor Node.js, execute:
    ```bash
    npm start
    ```
    O console exibirá os endereços IP corretos para acesso.

5.  **📡 Acesso:** Conecte seus dispositivos:
    -   Certifique-se de que o computador, a TV e o celular estejam na **mesma rede Wi-Fi**.
    -   **Na TV:** Abra o navegador e acesse o endereço fornecido no console (ex: `http://<IP_DO_COMPUTADOR>:5000`). Um QR Code aparecerá na tela.
    -   **No Celular:** Use a câmera para escanear o QR Code na tela da TV. Ele o levará diretamente para a página de controle (ex: `http://<IP_DO_COMPUTADOR>:5000/controle.html`).

6.  **🔊 Saída de Áudio:**
    O som das músicas será reproduzido pelo dispositivo que está exibindo a tela principal (`index.html`). Para garantir a melhor experiência:
    -   **Se a tela for uma Smart TV:** O som sairá pelos alto-falantes da TV.
    -   **Se a tela for o próprio notebook servidor:** O som sairá pelo dispositivo de áudio padrão do notebook. Isso permite que você conecte caixas de som externas, fones de ouvido ou uma **caixa de som via Bluetooth** para ter um som de melhor qualidade no ambiente.

    Basta configurar o dispositivo de áudio desejado como o padrão no sistema operacional antes de abrir o navegador na tela principal.

## Documentação Destalhada:
 - ### [1. Apresentação do Projeto](docs/Apresentação.md)
- ### [2. Detatlhes Técincos](docs/Documentação.md)
- ### [3. Solução de Problemas (Troubleshooting)](docs/Troubleshooting.md)


----
## Sobre o Autor

Helio Lima

Professor dos cursos Técnicos em Desenvolvimento de Sistemas e Técnico em Desenvolvimento de Jogos Digitais.

**Contato:** raimundo.helio@professor.edu.pi.gov.br
