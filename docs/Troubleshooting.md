
## Solução de Problemas (Troubleshooting)

### 1. Celular não consegue se conectar ao servidor

Este é o problema mais comum e geralmente está relacionado ao endereço IP ou à configuração da rede.

**Causa Principal: Endereço de IP Incorreto**

O servidor (`server.js`) possui uma lógica para detectar automaticamente o endereço IP correto da sua máquina na rede Wi-Fi. No entanto, se o seu computador estiver conectado a múltiplas redes (ex: Wi-Fi e uma VPN, ou adaptadores de máquinas virtuais), o IP errado pode ser selecionado.

**Como Verificar e Resolver:**
1.  Ao iniciar o servidor com `npm start`, observe o endereço IP exibido no console.
2.  Verifique se este IP corresponde ao endereço IP "IPv4" da sua conexão Wi-Fi. Você pode descobrir o IP do seu computador no Windows indo em `Configurações > Rede e Internet > Wi-Fi > Propriedades`.
3.  Se o IP exibido no console for diferente, significa que a detecção automática falhou. O QR Code e os links usarão o IP errado, e a conexão será recusada.
4.  **Solução:** A forma mais simples de resolver é **desativar temporariamente outras interfaces de rede** (como VPNs ou adaptadores virtuais) e reiniciar o servidor.

Se você utiliza algum serviço de VPN, como o Cloudflare WARP, é muito provável que ele bloqueie as conexões da sua rede local por padrão, impedindo o celular de se conectar ao servidor.

**Solução Principal (Recomendada):**
A alternativa mais simples e garantida é **desativar temporariamente a VPN** enquanto utiliza o media player. Como a aplicação funciona apenas na sua rede local, é seguro fazer isso.

**Solução Avançada (se disponível):**
Algumas versões do Cloudflare WARP (geralmente as pagas) oferecem um recurso chamado **"Split Tunneling"**. Se você encontrar essa opção (geralmente em `Configurações > Preferências > Configurações avançadas`), você pode usá-la para excluir o `node.exe` do túnel da VPN. Se não encontrar essa opção, siga a solução principal.