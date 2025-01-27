import os
import re
import time
import gc
import psutil
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp
from tqdm.auto import tqdm
from colorama import Fore, Style, init
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache, partial
import pickle
import signal

# ======================================================================
# CONFIGURACIÓN GLOBAL OPTIMIZADA
# ======================================================================
init(autoreset=True)
VERSION = "8.0"
CARPETA_DESCARGAS = "Descargas_Megustas"
MAX_CPU = 70
MAX_MEM = 75
MAX_WORKERS = os.cpu_count() * 2  # Ajuste dinámico
RETRY_LIMIT = 3
REQUEST_TIMEOUT = 15
CACHE_FILE = '.spotify_cache.pkl'
COOKIES_FILE = 'cookies.txt'

# Configuración Spotify
CLIENT_ID = 'e31407ac283d4f689877b11389f4c6ea'
CLIENT_SECRET = '69ae537afe8a438eb91fa1163bc0a5f8'
REDIRECT_URI = 'http://localhost:8888/callback'

# Optimización de yt-dlp
YTDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': f"{CARPETA_DESCARGAS}/%(title)s [SPOTIFY_ID=%(meta_id)s].%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'quiet': True,
    'no_warnings': True,
    'socket_timeout': REQUEST_TIMEOUT,
    'ignoreerrors': True,
    'retries': RETRY_LIMIT,
    'cookiefile': COOKIES_FILE,
    'postprocessor_args': [
        '-metadata', 'artist=%(meta_artist)s',
        '-metadata', 'album=%(meta_album)s',
        '-metadata', 'title=%(meta_title)s',
        '-metadata', 'track=%(meta_track)s'
    ]
}

# ======================================================================
# FUNCIONES DE INTERFAZ MEJORADAS
# ======================================================================
def mostrar_encabezado():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + f"""
    ███╗   ███╗███████╗ ██████╗ ██╗   ██╗███████╗████████╗ █████╗ 
    ████╗ ████║██╔════╝██╔════╝ ██║   ██║██╔════╝╚══██╔══╝██╔══██╗
    ██╔████╔██║█████╗  ██║  ███╗██║   ██║███████╗   ██║   ███████║
    ██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║╚════██║   ██║   ██╔══██║
    ██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝███████║   ██║   ██║  ██║
    ╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝
    {Fore.YELLOW}v{VERSION} | {Fore.GREEN}Descargas: {CARPETA_DESCARGAS}
    {Fore.MAGENTA}Hilos: {MAX_WORKERS} | Retries: {RETRY_LIMIT}
    """)

# ======================================================================
# GESTIÓN DE RECURSOS AVANZADA
# ======================================================================
class GestorRecursos:
    _ultima_lectura = 0
    _cache_recursos = {}
    
    @classmethod
    @lru_cache(maxsize=1)
    def sistema_estable(cls):
        ahora = time.time()
        if ahora - cls._ultima_lectura > 2:  # Cache de 2 segundos
            try:
                cls._cache_recursos = {
                    'cpu': psutil.cpu_percent(),
                    'mem': psutil.virtual_memory().percent
                }
                cls._ultima_lectura = ahora
            except Exception:
                return True
        return (cls._cache_recursos['cpu'] < MAX_CPU and 
                cls._cache_recursos['mem'] < MAX_MEM)

    @classmethod
    def optimizar_carga(cls):
        while not cls.sistema_estable():
            time.sleep(2)

# ======================================================================
# AUTENTICACIÓN SPOTIFY CON CACHÉ
# ======================================================================
@lru_cache(maxsize=1)
def autenticar_spotify():
    try:
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope='user-library-read',
            cache_path='.spotify_cache'
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"{Fore.RED}🚨 Error de autenticación: {e}")
        exit()

# ======================================================================
# GESTIÓN DE CACHÉ DE CANCIONES
# ======================================================================
class CacheCanciones:
    @staticmethod
    def guardar(canciones):
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump({
                'ids': {c['id'] for c in canciones},
                'timestamp': time.time()
            }, f)

    @staticmethod
    def cargar():
        try:
            with open(CACHE_FILE, 'rb') as f:
                data = pickle.load(f)
                if time.time() - data['timestamp'] < 86400:  # 24 horas
                    return data['ids']
        except:
            return set()
        return set()

# ======================================================================
# PROCESAMIENTO PARALELO MEJORADO
# ======================================================================
def procesar_lote(sp, offset):
    GestorRecursos.optimizar_carga()
    resultados = sp.current_user_saved_tracks(limit=50, offset=offset)
    return [
        {
            'id': track['id'],
            'posicion': offset + idx + 1,
            'titulo': track['name'],
            'artista': track['artists'][0]['name'],
            'album': track['album']['name'],
            'busqueda': f"{track['name']} {track['artists'][0]['name']} audio"
        }
        for idx, item in enumerate(resultados['items'])
        if (track := item.get('track'))
    ]

def obtener_canciones_paralelo(sp):
    try:
        total = sp.current_user_saved_tracks(limit=1)['total']
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(procesar_lote, sp, offset)
                for offset in range(0, total, 50)
            ]
            
            return [
                cancion
                for future in tqdm(as_completed(futures), total=len(futures), desc="Obteniendo canciones")
                for cancion in future.result()
            ]
    except Exception as e:
        print(f"{Fore.RED}🚨 Error crítico: {e}")
        exit()

# ======================================================================
# DESCARGAS OPTIMIZADAS
# ======================================================================
def descargar_worker(cancion):
    try:
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            ydl.download([
                f"ytsearch1:{cancion['busqueda']}"
            ])
        return True
    except Exception as e:
        return False

# ======================================================================
# MANEJO DE SEÑALES
# ======================================================================
def manejar_senal(signum, frame):
    print(f"\n{Fore.YELLOW}⏸️  Proceso pausado. Presiona Ctrl+C nuevamente para salir.")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
signal.signal(signal.SIGINT, manejar_senal)

# ======================================================================
# EJECUCIÓN PRINCIPAL OPTIMIZADA
# ======================================================================
if __name__ == "__main__":
    try:
        mostrar_encabezado()
        sp = autenticar_spotify()
        
        print(f"{Fore.WHITE}⏳ Optimizando recursos...")
        ids_descargados = CacheCanciones.cargar()
        canciones = obtener_canciones_paralelo(sp)
        
        seleccion = [idx for idx in range(len(canciones)) 
                    if canciones[idx]['id'] not in ids_descargados]
        
        print(f"\n{Fore.CYAN}🎯 Canciones a descargar: {len(seleccion)}")
        
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            list(tqdm(
                executor.map(descargar_worker, canciones),
                total=len(seleccion),
                desc=f"{Fore.GREEN}⬇️  Progreso",
                unit="canción"
            ))
        
        CacheCanciones.guardar(canciones)
        print(f"\n{Fore.GREEN}✅ ¡Proceso completado exitosamente!")

    except Exception as e:
        print(f"{Fore.RED}🚨 Error fatal: {str(e)}")
        exit(1)