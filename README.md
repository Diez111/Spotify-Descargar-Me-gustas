# Spotify-Descargar-Me-gustas
Con la api de spotify busco la lista de me gustas, me quedo con el nombre de las canciones y las descargo mediante youtube 


```markdown
# Spotify-Descargar-Me-gustas 🎵

Descarga tus canciones guardadas de Spotify en formato MP3 usando YouTube como fuente.  
*Optimizado para rendimiento y manejo de recursos.*

---

## 📚 Requisitos Previos
- **Python 3.8+**
- **FFmpeg** (para procesamiento de audio):  
  [Guía de instalación](https://ffmpeg.org/download.html)  
  *Asegúrate de agregarlo al PATH.*

---

## 📦 Dependencias
Instala las librerías necesarias:
```bash
pip install spotipy yt-dlp tqdm colorama psutil
```

---

## 🔧 Configuración Inicial

### 1. Registra una App en Spotify
1. Ve al [Dashboard de Spotify for Developers](https://developer.spotify.com/dashboard).
2. Crea una nueva aplicación y obtén:
   - **Client ID**
   - **Client Secret**

### 2. Configura el Archivo `spot-download.py`
Reemplaza las credenciales en el código:
```python
CLIENT_ID = 'tu_client_id'  # 🛠️ Modifica aquí
CLIENT_SECRET = 'tu_client_secret'  # 🛠️ Modifica aquí
```

### 3. Archivo de Cookies (Opcional pero recomendado)
- Coloca el archivo `cookies.txt` en la raíz del proyecto para evitar límites de YouTube.  
  *Puedes generarlo usando extensiones como [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid).*

---

## 🚀 Uso

1. **Ejecuta el script:**
   ```bash
   python spot-download.py
   ```

2. **Autenticación:**
   - Se abrirá una ventana en tu navegador para autorizar el acceso a tu cuenta de Spotify.

3. **Descarga:**
   - Las canciones se descargan en la carpeta `Descargas_Megustas` en formato MP3 (320kbps).  
   - Metadatos incluidos: título, artista, álbum y posición en tu biblioteca.

---

## 🛠️ Funcionamiento Técnico

### Flujo del Programa:
1. **Autenticación con Spotify:**  
   Usa OAuth2 para acceder a tu biblioteca de canciones guardadas.

2. **Obtención de Canciones:**  
   - Consulta todas las canciones en tu biblioteca usando paralelismo (hasta 4x más rápido).  
   - Filtra canciones ya descargadas mediante un sistema de caché (24 horas).

3. **Búsqueda en YouTube:**  
   - Busca cada canción con el formato: `{título} {artista} audio`.  
   - Prioriza resultados exactos (`ytsearch1`).

4. **Descarga y Conversión:**  
   - Usa `yt-dlp` para obtener el audio.  
   - Convierte a MP3 con FFmpeg y añade metadatos.

5. **Gestión de Recursos:**  
   - Limita el uso de CPU y memoria (70% CPU / 75% RAM máximo).  
   - Reintentos automáticos en fallos (hasta 3 veces).

---

## 📂 Estructura de Archivos
```
.
├── Descargas_Megustas/       # Canciones descargadas
├── spot-download.py          # Script principal
├── cookies.txt               # Cookies de YouTube (opcional)
└── .spotify_cache.pkl        # Cache de canciones descargadas
```

---

## ⚠️ Consideraciones Legales
- Este proyecto es para fines educativos.  
- Respeta los derechos de autor y las políticas de las plataformas.  
- Descarga solo contenido que tengas permiso para usar.

