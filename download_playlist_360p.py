import subprocess
import os
import shutil # Adicionado para shutil.which()
import sys    # Adicionado para sys.platform

# Importações para a GUI
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import threading

# Sinalizador para subprocess.run, especialmente útil no Windows com GUIs
SUBPROCESS_CREATION_FLAGS = 0
if sys.platform == "win32":
    SUBPROCESS_CREATION_FLAGS = subprocess.CREATE_NO_WINDOW

class TextRedirector:
    """Redireciona chamadas de print para um widget Text do Tkinter."""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_output):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, str_output, (self.tag,))
        self.widget.see(tk.END)
        self.widget.configure(state='disabled')

    def flush(self):
        pass
def baixar_playlist_ou_video_mp3(url_conteudo, output_dir_base="."):
    """
    Baixa o áudio de uma playlist do YouTube (ou um vídeo individual) e o converte para MP3 usando yt-dlp.
    Os arquivos são salvos diretamente no diretório base.

    Args:
        url_conteudo (str): A URL da playlist do YouTube ou de um vídeo individual.
        output_dir_base (str): O diretório base onde a pasta da playlist/vídeo será criada.
    """
    print(f"Tentando baixar áudio de: {url_conteudo} como MP3")

    # Garante que o diretório base seja absoluto
    output_dir_base = os.path.abspath(output_dir_base)

    # O diretório final é o próprio diretório base
    diretorio_alvo_final = output_dir_base

    # Cria o diretório de destino se não existir
    os.makedirs(diretorio_alvo_final, exist_ok=True)
    print(f"Conteúdo será salvo em: '{diretorio_alvo_final}'")

    # Define o template do nome do arquivo de saída para yt-dlp
    # %(playlist_index)s - numeração do vídeo na playlist (ou '0' para vídeo individual se não em playlist)
    # %(title)s - título do vídeo
    # %(ext)s - extensão do arquivo (será mp3)
    output_template_filename = "%(playlist_index)02d - %(title)s.%(ext)s" # Adiciona padding ao index
    output_template_arg = os.path.normpath(os.path.join(diretorio_alvo_final, output_template_filename))

    yt_dlp_executable = shutil.which("yt-dlp")
    ffmpeg_executable = shutil.which("ffmpeg")

    # Comando yt-dlp
    # -x: extrai o áudio.
    # --audio-format mp3: define o formato de saída do áudio como MP3.
    # -f bestaudio/best: seleciona a melhor trilha de áudio disponível.
    # -o: especifica o template do nome do arquivo de saída (incluindo caminho).
    command = [
        yt_dlp_executable if yt_dlp_executable else "yt-dlp", # Usa path completo ou nome se não encontrado
        "--verbose",             # Adiciona saída detalhada para depuração
        "--no-warnings",         # Suprime avisos que podem não ser o erro principal
        "--ignore-config",       # Ignora arquivos de configuração do usuário (para descartar configs problemáticas)
        # "--no-check-certificate", # Descomente se suspeitar de problemas de SSL/TLS
    ]

    if not yt_dlp_executable:
        print("Aviso: yt-dlp não encontrado via shutil.which(). Tentando executar 'yt-dlp' diretamente.")

    if ffmpeg_executable:
        print(f"ffmpeg encontrado em: {ffmpeg_executable}")
        command.extend(["--ffmpeg-location", ffmpeg_executable])
    else:
        print("Aviso: ffmpeg não encontrado no PATH. A mesclagem de vídeo e áudio pode falhar ou usar alternativas.")

    # Adiciona opções de formato e saída
    command.extend(["-f", "bestaudio/best", # Baixa a melhor qualidade de áudio
                      "-x", # Extrai o áudio
                      "--audio-format", "mp3", # Converte para MP3
                      "--audio-quality", "0", # Melhor qualidade de áudio
                      "-o", output_template_arg]) # Define o nome do arquivo de saída

    # Verifica se é um arquivo de lote (batch file)
    if url_conteudo.startswith("bf:"):
        batch_file_path = url_conteudo[3:] # Remove o prefixo "bf:"
        command.extend(["--batch-file", batch_file_path])
    else: # É uma URL normal
        command.append(url_conteudo)

    # Prepara o ambiente para o subprocesso, especialmente para forçar UTF-8 no Windows
    proc_env = os.environ.copy()
    if sys.platform == "win32":
        proc_env["PYTHONIOENCODING"] = "utf-8"
        proc_env["PYTHONUTF8"] = "1" # Para Python 3.7+

    try:
        print(f"Executando comando: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=SUBPROCESS_CREATION_FLAGS, env=proc_env)
        print("Download(s) concluído(s) com sucesso!")
        print(f"Saída yt-dlp (stdout):\n{result.stdout}")
        if result.stderr:
            print(f"Saída yt-dlp (stderr):\n{result.stderr}")

        print(f"Verifique o diretório: {diretorio_alvo_final}")
        return True
    except subprocess.CalledProcessError as e:
        print("Erro durante o download:")
        print(f"Comando: {' '.join(e.cmd)}")
        print(f"Código de retorno: {e.returncode}")
        print(f"Stdout: {e.stdout or ''}")
        print(f"Stderr: {e.stderr or ''}")
        return False
    except FileNotFoundError:
        print("Erro: yt-dlp não encontrado. Certifique-se de que está instalado e no PATH do sistema.")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return False

def start_playlist_download_thread(url_entry, base_dir_entry, log_area, download_button):
    playlist_url = url_entry.get()
    output_dir_base = base_dir_entry.get()

    if not playlist_url:
        log_area.configure(state='normal')
        log_area.insert(tk.END, "Erro: A URL da playlist/vídeo não pode estar vazia.\n", ("stderr",))
        log_area.see(tk.END)
        log_area.configure(state='disabled')
        return

    download_button.config(state=tk.DISABLED)
    log_area.configure(state='normal')
    log_area.delete(1.0, tk.END) # Limpa logs anteriores
    log_area.insert(tk.END, f"Iniciando download para: {playlist_url}\n")
    log_area.configure(state='disabled')

    def run_download():
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = TextRedirector(log_area, "stdout")
        sys.stderr = TextRedirector(log_area, "stderr")

        try:
            success = baixar_playlist_ou_video_mp3(playlist_url, output_dir_base)
            final_message = "\n--- Download da Playlist/Vídeo Finalizado com Sucesso ---\n" if success else "\n--- Falha no Download da Playlist/Vídeo ---\n"
            print(final_message)
        except Exception as e:
            print(f"Erro inesperado na thread de download: {e}\n")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            log_area.master.after(0, lambda: download_button.config(state=tk.NORMAL))

    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()

def browse_base_directory(dir_entry):
    directory = filedialog.askdirectory()
    if directory:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory)

def load_m3u_file(url_entry_widget, log_area_widget):
    filepath = filedialog.askopenfilename(
        title="Carregar arquivo M3U",
        filetypes=(("Arquivos M3U", "*.m3u *.m3u8"), ("Todos os arquivos", "*.*"))
    )
    if filepath:
        url_entry_widget.delete(0, tk.END)
        # Prepend "bf:" to indicate a batch file for yt-dlp
        batch_file_uri = f"bf:{filepath}"
        url_entry_widget.insert(0, batch_file_uri)
        
        log_area_widget.configure(state='normal')
        log_area_widget.insert(tk.END, f"Arquivo M3U carregado: {batch_file_uri}\n"
                                       f"Clique em 'Baixar Playlist/Vídeo' para processar.\n", ("stdout",))
        log_area_widget.see(tk.END)
        log_area_widget.configure(state='disabled')

def _fetch_and_save_m3u_content(source_url, output_filepath, log_area_widget):
    """
    Busca o conteúdo (lista de vídeos de uma playlist ou título de vídeo único)
    e salva em um arquivo M3U. Executado em uma thread.
    """
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TextRedirector(log_area_widget, "stdout")
    sys.stderr = TextRedirector(log_area_widget, "stderr")

    proc_env = os.environ.copy()
    if sys.platform == "win32":
        proc_env["PYTHONIOENCODING"] = "utf-8"
        proc_env["PYTHONUTF8"] = "1"

    try:
        print(f"Processando URL para salvar em M3U: {source_url}")
        items_to_save = [] # Lista de tuplas ("#EXTINF...", "url")

        is_youtube_playlist = "youtube.com/" in source_url.lower() and "list=" in source_url.lower()

        if is_youtube_playlist:
            print("Detectada playlist do YouTube. Tentando obter lista de vídeos...")
            yt_dlp_executable = shutil.which("yt-dlp")
            if not yt_dlp_executable:
                print("Erro: yt-dlp não encontrado. Salvando URL da playlist original.")
                items_to_save.append((f"#EXTINF:-1,Playlist: {source_url}", source_url))
            else:
                command = [
                    yt_dlp_executable,
                    "--flat-playlist", # Mais rápido, não extrai metadados profundos
                    "--print", "%(title)s\n%(original_url)s", # Título na primeira linha, URL na segunda
                    source_url
                ]
                result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=SUBPROCESS_CREATION_FLAGS, env=proc_env)
                
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2 and len(lines) % 2 == 0: # Deve haver pares de título/URL
                        for i in range(0, len(lines), 2):
                            title = lines[i].strip()
                            url = lines[i+1].strip()
                            if title and url:
                                items_to_save.append((f"#EXTINF:-1,{title}", url))
                        print(f"Encontrados {len(items_to_save)} vídeos na playlist.")
                    else:
                        print("Não foi possível obter a lista de vídeos da playlist. Salvando URL original.")
                        items_to_save.append((f"#EXTINF:-1,Playlist: {source_url}", source_url))
                else:
                    print(f"Falha ao obter lista de vídeos. yt-dlp stderr: {result.stderr or 'Nenhum'}")
                    items_to_save.append((f"#EXTINF:-1,Playlist: {source_url}", source_url))
        else: # Não é uma playlist do YouTube ou é um arquivo local
            title_to_use = source_url # Default title é a própria URL
            is_youtube_video = "youtube.com/" in source_url.lower() and "watch?v=" in source_url.lower()
            if is_youtube_video: # Tenta obter título se for um vídeo único do YouTube
                yt_dlp_executable = shutil.which("yt-dlp")
                if yt_dlp_executable:
                    try:
                        title_cmd = [yt_dlp_executable, "--get-title", source_url]
                        title_process = subprocess.run(title_cmd, capture_output=True, text=True, check=False, encoding='utf-8', errors='replace', creationflags=SUBPROCESS_CREATION_FLAGS, env=proc_env)
                        if title_process.returncode == 0 and title_process.stdout.strip():
                            title_to_use = title_process.stdout.strip()
                    except Exception as e_title:
                        print(f"Não foi possível obter o título do vídeo individual: {e_title}")
            items_to_save.append((f"#EXTINF:-1,{title_to_use}", source_url))

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for extinf, url_item in items_to_save:
                f.write(extinf + "\n")
                f.write(url_item + "\n")
        print(f"Playlist/URL salva em: {output_filepath}")

    except Exception as e:
        print(f"Erro ao processar e salvar M3U: {e}")
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

def save_m3u_file(url_entry_widget, log_area_widget):
    current_url = url_entry_widget.get()
    if not current_url:
        log_area_widget.configure(state='normal')
        log_area_widget.insert(tk.END, "Nada para salvar: campo de URL está vazio.\n", ("stderr",))
        log_area_widget.see(tk.END)
        log_area_widget.configure(state='disabled')
        return

    filepath = filedialog.asksaveasfilename(
        title="Salvar como arquivo M3U",
        defaultextension=".m3u",
        filetypes=(("Arquivos M3U", "*.m3u"), ("Todos os arquivos", "*.*"))
    )
    if filepath:
        # Inicia a tarefa de busca e salvamento em uma nova thread
        save_thread = threading.Thread(
            target=_fetch_and_save_m3u_content,
            args=(current_url, filepath, log_area_widget),
            daemon=True)
        save_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Downloader de Músicas (MP3)")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # URL da Playlist/Vídeo
    ttk.Label(frame, text="URL/Arquivo M3U:").grid(row=0, column=0, sticky=tk.W, pady=2)
    url_entry = ttk.Entry(frame, width=50)
    url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
    url_entry.insert(0, "https://www.youtube.com/watch?v=CTvaEnGajQE&list=PLLHo4pVI8I_oYXbf2iEc53SGjQaAOdJ5L") # Exemplo

    # Botões M3U
    m3u_button_frame = ttk.Frame(frame)
    m3u_button_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=(0, 5))

    load_m3u_button = ttk.Button(m3u_button_frame, text="Carregar M3U", command=lambda: load_m3u_file(url_entry, log_area))
    load_m3u_button.pack(side=tk.LEFT, padx=(0,5))

    save_m3u_button = ttk.Button(m3u_button_frame, text="Salvar M3U", command=lambda: save_m3u_file(url_entry, log_area))
    save_m3u_button.pack(side=tk.LEFT)

    # Diretório Base de Saída
    ttk.Label(frame, text="Diretório Base de Saída:").grid(row=2, column=0, sticky=tk.W, pady=2)
    base_dir_entry = ttk.Entry(frame, width=40)
    base_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
    base_dir_entry.insert(0, "musicas")
    browse_button = ttk.Button(frame, text="Navegar...", command=lambda: browse_base_directory(base_dir_entry))
    browse_button.grid(row=2, column=2, sticky=tk.W, pady=2, padx=(5,0))

    # Botão de Download
    download_button = ttk.Button(frame, text="Baixar Músicas (MP3)")
    download_button.grid(row=4, column=0, columnspan=3, pady=10)
    download_button.config(command=lambda: start_playlist_download_thread(url_entry, base_dir_entry, log_area, download_button))

    # Área de Log
    log_area = scrolledtext.ScrolledText(frame, width=70, height=15, wrap=tk.WORD, state='disabled')
    log_area.grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
    log_area.tag_config("stdout", foreground="black")
    log_area.tag_config("stderr", foreground="red")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    root.mainloop()

    # O código de exemplo anterior para execução via linha de comando foi removido
    # pois agora a execução principal é através da GUI.
    # Se desejar manter a funcionalidade de linha de comando,
    # seria necessário adicionar um parser de argumentos (ex: argparse)
    # e condicionar a execução da GUI ou da lógica de linha de comando.