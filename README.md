# 🤖 Jarvis

The original `jarvis_mvp.py` is preserved unchanged as the first working MVP.
The new modular implementation starts in `app.py` and is intentionally being
built alongside it.

## New modular version

From the project directory on Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

The first version uses a lightweight console to validate the command engine:

```text
abre Spotify
modo gaming
voces
voz 1
salir
```

Applications and routines are configured in `config/jarvis.json`. The console
is temporary; wake-word detection, speech recognition and the visual interface
will be connected to the same core services in later steps.

`voces` lists the voices installed in Windows through SAPI. Use `voz 1`,
`voz 2`, etc. to select one and hear the confirmation. The available voices
depend on the language packs installed in Windows.

## Legacy MVP

The clap-activated implementation remains in `jarvis_mvp.py` and is not used
by the new application.

Asistente personal estilo Jarvis activado por **doble aplauso**. Al detectarlo, saluda con voz, abre YouTube en la TV (monitor secundario vía HDMI) y lanza AntiGravity en el monitor principal.

---

## ✨ Funcionalidades

- 👏 **Activación por doble aplauso** — detección robusta con calibración automática del ruido de fondo
- 🗣️ **Saludo por voz** — texto a voz en español con `edge-tts` (voz Álvaro, España)
- 📺 **YouTube en la TV** — abre Opera GX en el monitor secundario (HDMI) con la ventana posicionada exactamente en esa pantalla, incluso con coordenadas negativas
- 🖥️ **AntiGravity en el principal** — lanza la app de escritorio en paralelo mientras suena la voz
- 🔇 **Sin solapamiento de audio** — la voz termina antes de que YouTube empiece a sonar

---

## 📦 Requisitos

- Python 3.10+
- Windows 10/11
- Opera GX instalado
- Micrófono funcional

### Instalar dependencias

```bash
pip install numpy sounddevice edge-tts pygame
```

---

## ⚙️ Configuración

Antes de correr, ajusta estas variables al inicio de `jarvis_mvp.py`:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DEVICE_ID` | ID de tu micrófono (ver abajo) | `1` |
| `MIC_CHANNELS` | Canales del micrófono (`1` mono, `2` estéreo) | `2` |
| `YOUTUBE_URL` | Video que se abre al activar | `"https://youtube.com/..."` |
| `ANTIGRAVITY_EXE` | Ruta completa al exe de AntiGravity | `r"C:\Users\...\Antigravity.exe"` |
| `WELCOME_TEXT` | Texto que dice Jarvis al activarse | `"Bienvenido a casa."` |
| `VOICE` | Voz de edge-tts | `"es-ES-AlvaroNeural"` |

### Encontrar tu DEVICE_ID

```python
import sounddevice as sd
print(sd.query_devices())
```

Busca tu micrófono en la lista y usa su número. Si tiene `2 in`, usa `MIC_CHANNELS = 2`.

### Encontrar la ruta de AntiGravity

Abre AntiGravity, luego en PowerShell:

```powershell
Get-Process | Where-Object {$_.Path} | Select-Object Name, Path | Sort-Object Name | Out-File "$env:USERPROFILE\Desktop\procesos.txt"
```

Busca el exe en `procesos.txt`.

---

## 🚀 Uso

```bash
python jarvis_mvp.py
```

1. El script calibra el ruido de fondo durante 3 segundos — **mantente en silencio**
2. Cuando diga `Esperando doble aplauso...`, ya está listo
3. Da **dos aplausos** con menos de 0.9 segundos entre ellos
4. Jarvis saluda, abre YouTube en la TV y AntiGravity en el principal

---

## 🔧 Ajuste fino de detección

Si se activa con ruido falso o cuesta activarlo, modifica estas constantes:

| Constante | Default | Efecto |
|---|---|---|
| `MIN_CLAP_GAP` | `0.15s` | Tiempo mínimo entre aplausos (antirebote) |
| `MAX_CLAP_GAP` | `0.9s` | Tiempo máximo entre dos aplausos válidos |
| `DOUBLE_WINDOW` | `1.5s` | Ventana total para completar el doble aplauso |
| `COOLDOWN` | `5.0s` | Espera mínima entre activaciones |

---

## 🗂️ Estructura

```
jarvis-mvp/
├── jarvis_mvp.py   # Script principal
└── README.md
```

---

## 📝 Notas técnicas

- La detección de aplausos usa la relación `peak / RMS` para distinguir sonidos impulsivos (aplausos) de ruido sostenido (voz, música)
- La ventana de Opera GX se mueve al monitor secundario usando `SetWindowPos` de la API Win32 vía `ctypes`, lo que permite coordenadas negativas (TV a la izquierda del monitor principal)
- Opera GX reutiliza el mismo proceso para todas las ventanas, por lo que la detección de la ventana nueva se hace por snapshot de `hwnd` antes/después de lanzarla