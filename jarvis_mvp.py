import time
import webbrowser
import numpy as np
import sounddevice as sd
import subprocess
import os
import asyncio
import edge_tts
import pygame
import threading
import ctypes
import ctypes.wintypes
import tempfile

# =========================
# CONFIG
# =========================
DEVICE_ID      = 1       # Microphone Array (AMD Audio Device)
MIC_CHANNELS   = 2       # estereo
BLOCKSIZE      = 1024
COOLDOWN       = 5.0     # segundos entre activaciones
DOUBLE_WINDOW  = 1.5     # ventana para detectar doble aplauso
MIN_CLAP_GAP   = 0.15    # minimo entre aplausos (antirebote)
MAX_CLAP_GAP   = 0.9     # maximo entre dos aplausos validos

YOUTUBE_URL    = "https://www.youtube.com/watch?v=hEIexwwiKKU"
ANTIGRAVITY_EXE = r"C:\Users\Juanda\AppData\Local\Programs\Antigravity\Antigravity.exe"
WELCOME_TEXT   = "Bienvenido a casa, senor Juanda."
VOICE          = "es-ES-AlvaroNeural"

def _find_opera():
    import glob
    local = os.environ.get('LOCALAPPDATA', '')
    candidates = glob.glob(os.path.join(local, 'Programs', 'Opera*', 'opera.exe'))
    candidates += [
        r"C:\Program Files\Opera GX\opera.exe",
        r"C:\Program Files\Opera\opera.exe",
        r"C:\Program Files (x86)\Opera\opera.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

OPERA_PATH = _find_opera()

pygame.mixer.init()

# =========================
# ESTADO GLOBAL
# =========================
is_running  = False
_speak_lock = threading.Lock()

# =========================
# TTS
# =========================
async def tts_edge(text, filepath):
    communicate = edge_tts.Communicate(text, voice=VOICE)
    await communicate.save(filepath)

def speak(text):
    with _speak_lock:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            asyncio.run(tts_edge(text, tmp_path))
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

# =========================
# MONITORES
# =========================
def get_screens():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    monitors = []
    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = lprcMonitor.contents
        monitors.append((r.left, r.top, r.right, r.bottom))
        return 1
    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
        ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double
    )
    user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(callback), 0)
    return monitors

def get_secondary_monitor():
    screens = get_screens()
    print(f"   Monitores: {len(screens)}")
    for i, s in enumerate(screens):
        print(f"   Monitor {i}: {s}")
    for (left, top, right, bottom) in screens:
        if left == 0 and top == 0:
            continue
        return (left, top, right - left, bottom - top)
    return None

# =========================
# MOVER VENTANA
# =========================
def _get_opera_pids():
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq opera.exe", "/FO", "CSV", "/NH"],
        capture_output=True, text=True
    )
    pids = set()
    for line in result.stdout.strip().splitlines():
        parts = line.strip('"').split('","')
        if len(parts) >= 2:
            try:
                pids.add(int(parts[1]))
            except ValueError:
                pass
    return pids

def _find_best_opera_hwnd(exclude_hwnds=set()):
    """Encuentra la ventana de Opera mas grande y visible, excluyendo hwnds conocidos."""
    opera_pids = _get_opera_pids()
    EnumWindows              = ctypes.windll.user32.EnumWindows
    EnumWindowsProc          = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_long)
    GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
    IsWindowVisible          = ctypes.windll.user32.IsWindowVisible
    GetWindowRect            = ctypes.windll.user32.GetWindowRect

    candidatos = []
    def cb(hwnd_c, _):
        if hwnd_c in exclude_hwnds:
            return True
        pid_buf = ctypes.c_ulong()
        GetWindowThreadProcessId(hwnd_c, ctypes.byref(pid_buf))
        if pid_buf.value in opera_pids and IsWindowVisible(hwnd_c):
            r = ctypes.wintypes.RECT()
            GetWindowRect(hwnd_c, ctypes.byref(r))
            w = r.right - r.left
            h = r.bottom - r.top
            if w > 600 and h > 400:
                candidatos.append((w * h, hwnd_c))
        return True
    EnumWindows(EnumWindowsProc(cb), 0)
    candidatos.sort(reverse=True)
    return candidatos[0][1] if candidatos else None

def move_hwnd_to(hwnd, left, top, width, height):
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    ctypes.windll.user32.SetWindowPos(
        hwnd, None, left, top, width, height,
        SWP_NOACTIVATE | SWP_SHOWWINDOW
    )

# =========================
# ABRIR YOUTUBE EN TV
# =========================
def open_youtube_on_tv(monitor):
    left, top, width, height = monitor

    if not OPERA_PATH:
        webbrowser.open(YOUTUBE_URL)
        return

    # Snapshot de ventanas Opera existentes ANTES de abrir
    hwnds_antes = set()
    opera_pids = _get_opera_pids()
    EnumWindows     = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_long)
    GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible
    GetWindowRect   = ctypes.windll.user32.GetWindowRect

    def snapshot_cb(hwnd_c, _):
        pid_buf = ctypes.c_ulong()
        GetWindowThreadProcessId(hwnd_c, ctypes.byref(pid_buf))
        if pid_buf.value in opera_pids and IsWindowVisible(hwnd_c):
            r = ctypes.wintypes.RECT()
            GetWindowRect(hwnd_c, ctypes.byref(r))
            if (r.right - r.left) > 600:
                hwnds_antes.add(hwnd_c)
        return True
    EnumWindows(EnumWindowsProc(snapshot_cb), 0)
    print(f"   Ventanas Opera antes: {hwnds_antes}")

    # Abrir nueva ventana de Opera con YouTube
    subprocess.Popen([OPERA_PATH, "--new-window", YOUTUBE_URL])

    # Esperar hasta que aparezca una ventana NUEVA (no estaba antes)
    hwnd_nuevo = None
    for _ in range(30):   # hasta 15 segundos
        candidatos = []
        opera_pids_now = _get_opera_pids()
        def search_cb(hwnd_c, _):
            if hwnd_c in hwnds_antes:
                return True
            pid_buf = ctypes.c_ulong()
            GetWindowThreadProcessId(hwnd_c, ctypes.byref(pid_buf))
            if pid_buf.value in opera_pids_now and IsWindowVisible(hwnd_c):
                r = ctypes.wintypes.RECT()
                GetWindowRect(hwnd_c, ctypes.byref(r))
                w = r.right - r.left
                h = r.bottom - r.top
                if w > 600 and h > 400:
                    candidatos.append((w * h, hwnd_c))
            return True
        EnumWindows(EnumWindowsProc(search_cb), 0)
        if candidatos:
            candidatos.sort(reverse=True)
            hwnd_nuevo = candidatos[0][1]
            break
        time.sleep(0.5)

    if hwnd_nuevo:
        move_hwnd_to(hwnd_nuevo, left, top, width, height)
        print(f"   YouTube movido a TV ({width}x{height} en {left},{top})")
    else:
        print("   No se encontro ventana nueva de Opera")

def open_youtube_main():
    webbrowser.open(YOUTUBE_URL)

# =========================
# ABRIR ANTIGRAVITY
# =========================
def open_antigravity():
    if os.path.exists(ANTIGRAVITY_EXE):
        subprocess.Popen([ANTIGRAVITY_EXE])
        print("   AntiGravity abierto")
    else:
        print(f"   AntiGravity no encontrado: {ANTIGRAVITY_EXE}")

# =========================
# SECUENCIA PRINCIPAL
# =========================
def ejecutar_jarvis():
    global is_running
    is_running = True
    print("\n ACTIVANDO JARVIS\n")

    secondary = get_secondary_monitor()

    # YouTube y AntiGravity arrancan en paralelo mientras suena la voz
    if secondary:
        threading.Thread(target=open_youtube_on_tv, args=(secondary,), daemon=True).start()
    else:
        threading.Thread(target=open_youtube_main, daemon=True).start()

    threading.Thread(target=open_antigravity, daemon=True).start()

    # Voz
    speak(WELCOME_TEXT)

    time.sleep(8)
    is_running = False

# =========================
# CALIBRACION
# =========================
def calibrate(device, sr, sec=3):
    rms_vals, peak_vals = [], []

    def cb(indata, frames, time_info, status):
        x = indata[:, 0]
        rms_vals.append(float(np.sqrt(np.mean(x**2))))
        peak_vals.append(float(np.max(np.abs(x))))

    print("\n Calibrando silencio... (mantente callado 3 segundos)")
    with sd.InputStream(device=device, channels=MIC_CHANNELS, samplerate=sr,
                        blocksize=BLOCKSIZE, callback=cb):
        time.sleep(sec)

    rms_base  = np.percentile(rms_vals,  95)
    peak_base = np.percentile(peak_vals, 95)

    rms_min  = max(0.015, rms_base  * 4)
    peak_thr = max(0.08,  peak_base * 5)

    print(f" Umbral listo — RMS_MIN={rms_min:.4f} PEAK_THR={peak_thr:.4f}")
    return rms_min, peak_thr

# =========================
# MAIN
# =========================
def run():
    sr = 48000
    print("Jarvis listo...")

    rms_min, peak_thr = calibrate(DEVICE_ID, sr)

    clap_times   = []
    last_trigger = 0.0

    def cb(indata, frames, time_info, status):
        nonlocal clap_times, last_trigger

        x    = indata[:, 0]
        rms  = float(np.sqrt(np.mean(x**2)))
        peak = float(np.max(np.abs(x)))
        now  = time.time()

        es_aplauso = (
            peak > peak_thr       # supera umbral calibrado
            and peak > rms * 2.5  # impulsivo (no ruido sostenido)
            and rms  < rms_min * 8
        )

        if es_aplauso:
            # antirebote
            if clap_times and (now - clap_times[-1]) < MIN_CLAP_GAP:
                return

            clap_times = [t for t in clap_times if now - t <= DOUBLE_WINDOW]
            clap_times.append(now)
            print(f"\n Aplauso {len(clap_times)}/2  (RMS={rms:.4f} PEAK={peak:.4f})")

            if len(clap_times) >= 2:
                gap = clap_times[-1] - clap_times[-2]
                if (MIN_CLAP_GAP < gap < MAX_CLAP_GAP
                        and (now - last_trigger) > COOLDOWN
                        and not is_running):
                    last_trigger = now
                    clap_times   = []
                    threading.Thread(target=ejecutar_jarvis, daemon=True).start()

    print("\n Esperando doble aplauso...\n")
    try:
        with sd.InputStream(device=DEVICE_ID, channels=MIC_CHANNELS, samplerate=sr,
                            blocksize=BLOCKSIZE, callback=cb):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n Jarvis apagado. Hasta luego, senor Juanda.\n")

if __name__ == "__main__":
    run()