# Plan de evolución de Jarvis

## Visión

Convertir Jarvis en un asistente personal para Windows, gratuito y
preferentemente open source, que funcione de forma nativa en la laptop:

```text
Micrófono
  ↓
Palabra de activación: “Jarvis”
  ↓
Reconocimiento de voz
  ↓
Comprensión de la intención
  ├─ Ejecutar una acción
  ├─ Usar una integración
  └─ Mantener una conversación
  ↓
Respuesta hablada + interfaz visual
  ↓
Memoria controlable por el usuario
```

Jarvis debe poder entender frases naturales, no depender de una lista rígida
de `if/else` y nunca afirmar que hizo algo si la acción falló.

## Principios del proyecto

- Mantener el sistema gratuito y con alternativas locales.
- Priorizar bajo consumo mientras se juega.
- Mantener el micrófono y la activación por “Jarvis” como funciones centrales.
- Conservar todas las voces hasta elegir una definitivamente.
- Ejecutar comandos conocidos de forma rápida y determinista.
- Usar IA para conversación, interpretación y consultas ambiguas.
- Pedir confirmación antes de acciones peligrosas.
- Guardar memoria solo de forma explícita y permitir borrarla.
- Mantener `jarvis_mvp.py` intacto como referencia histórica.
- Crear un commit cuando cada fase quede estable.

## Estado actual

- Base modular separada del MVP original.
- Configuración externa para aplicaciones y rutinas.
- Activación experimental por voz con “Jarvis”.
- Reconocimiento de voz pulsado como respaldo.
- Respuestas mediante Edge TTS y voces alternativas de Windows.
- Selector de voces conservado para pruebas futuras.
- Apertura y cierre inicial de aplicaciones.
- Rutinas iniciales, incluido modo gaming.
- Integración inicial con Spotify.
- Interfaz visual experimental con orbe animado.
- Base de conversación local con Ollama y memoria SQLite.

## Fase 0 — Base y entorno

### Objetivos

- Mantener el proyecto ejecutable en Windows con Python.
- Usar un entorno virtual reproducible.
- Separar configuración, acciones, interfaz y servicios.
- Documentar comandos de instalación y ejecución.

### Terminado cuando

- `python app.py` inicia Jarvis.
- `python app.py --console` permite probar sin interfaz.
- Las dependencias se instalan desde `requirements.txt`.
- El MVP original sigue sin modificaciones.

## Fase 1 — Interfaz de aplicación real

### Objetivos

- Reemplazar la figura flotante por una ventana real.
- Incluir bordes, título, minimizar, cerrar y bandeja del sistema.
- Mantener un diseño oscuro, tecnológico y anaranjado.
- Mostrar un núcleo central con ondas, partículas y visualización de audio.
- Representar claramente los estados:
  - Standby.
  - Wake word detectada.
  - Escuchando.
  - Procesando.
  - Ejecutando.
  - Hablando.
  - Error.
- Poder cerrar Jarvis sin cerrar el IDE.

### Terminado cuando

- Jarvis se puede minimizar, restaurar y cerrar desde la propia aplicación.
- La interfaz no depende de la terminal para detenerse.
- El núcleo permanece dentro de una ventana visual coherente.
- Las animaciones no consumen recursos excesivos.

## Fase 2 — Micrófono y activación por voz

### Objetivos

- Escuchar continuamente una palabra de activación de bajo consumo.
- Reconocer:

  ```text
  “Jarvis, abre Spotify”
  “Jarvis, pon música”
  ```

- Permitir también una pausa:

  ```text
  “Jarvis”
  “Abre Spotify”
  ```

- Mantener el botón de escucha como respaldo.
- Calibrar ruido y elegir el micrófono correcto.
- Evitar que Jarvis procese conversaciones que no comiencen con su nombre.

### Tecnología prevista

- Wake word local: `openWakeWord` o Porcupine.
- Reconocimiento: `faster-whisper` local o alternativa ligera.
- Fallback temporal: reconocimiento de Google.

### Terminado cuando

- La activación funciona de forma estable en la laptop.
- El consumo en espera es bajo.
- El reconocimiento tolera acentos y frases naturales.
- Jarvis no se activa constantemente por ruido de fondo.

## Fase 3 — Voz y respuesta

### Objetivos

- Mantener todas las voces disponibles hasta elegir una.
- Probar voces masculinas y femeninas sin borrar opciones.
- Separar motor de voz, velocidad, tono y volumen.
- Sincronizar la animación con el estado de habla.
- Permitir cambiar de voz desde configuración o comando.

### Opciones

- Edge TTS para voces neurales fluidas.
- Piper para una alternativa local.
- SAPI como fallback sin internet.

### Terminado cuando

- La voz seleccionada se aplica realmente a cada respuesta.
- Los errores del motor se muestran claramente.
- Se puede cambiar de voz sin modificar código.

## Fase 4 — Router de intenciones

### Objetivos

- Reemplazar respuestas rígidas por intenciones estructuradas.
- Entender sinónimos y variaciones:

  ```text
  “abre Spotify”
  “abrime Spotify”
  “quiero escuchar música”
  “lanza Spotify, por favor”
  ```

- Mantener acciones conocidas rápidas y seguras.
- Usar IA solo cuando las reglas no sean suficientes.

### Ejemplo

```json
{
  "intent": "open_application",
  "target": "spotify",
  "confidence": 0.96
}
```

### Terminado cuando

- Los comandos no dependen de coincidencias exactas.
- Las intenciones inválidas no ejecutan acciones.
- Una acción fallida genera una explicación real.

## Fase 5 — Aplicaciones, sistema y rutinas

### Objetivos

- Abrir, cerrar y enfocar aplicaciones.
- Abrir juegos de Steam, Epic y accesos directos.
- Controlar volumen, reproducción, ventanas y monitores.
- Crear rutinas configurables:

  ```text
  “Jarvis, modo gaming”
  “Jarvis, modo trabajo”
  “Jarvis, modo música”
  ```

- Detectar juegos y activar modo ahorro.
- Mantener compatibilidad con anti-cheat: no modificar ni inyectar procesos.

### Terminado cuando

- Las rutinas están definidas en configuración.
- Se pueden agregar aplicaciones sin cambiar el router.
- Jarvis puede suspender servicios pesados al iniciar un juego.

## Fase 6 — Música

### Objetivos

- Reproducir canciones por artista y título:

  ```text
  “Jarvis, reproduce Entrégate de Luis Miguel”
  ```

- Buscar, reproducir, pausar, continuar, saltar y controlar volumen.
- Soportar Spotify como primera integración.
- Dejar preparados YouTube Music y Apple Music.
- Informar si no hay cuenta, credenciales o dispositivo activo.

### Dependencias externas

- Spotify Web API.
- Cuenta Premium para controlar reproducción.
- Credenciales guardadas únicamente en `.env`.

### Terminado cuando

- Se selecciona la pista correcta y comienza la reproducción.
- Se detectan dispositivos disponibles.
- Se informa la causa exacta si Spotify no puede reproducir.

## Fase 7 — Conversación local

### Objetivos

- Conversar sin responder siempre con un mensaje predeterminado.
- Usar Ollama solo cuando una orden necesite comprensión o conversación.
- Mantener comandos básicos sin IA para ahorrar recursos.
- Descargar el modelo de memoria cuando no se use.

### Modelo inicial

- `qwen2.5:3b` o equivalente pequeño.
- Aumentar el modelo solo si la laptop lo soporta.

### Terminado cuando

- Jarvis responde preguntas generales en español.
- Puede mantener contexto breve.
- No confunde conversación con una orden ejecutable.
- Nunca inventa que abrió o modificó algo.

## Fase 8 — Búsqueda y ayuda diaria

### Objetivos

- Buscar información actual en internet.
- Resumir resultados y mostrar fuentes.
- Consultar clima, horarios y datos útiles.
- Ayudar con errores técnicos y explicaciones.
- Crear temporizadores, notas y recordatorios.

### Regla

Las respuestas actuales o verificables deben incluir fuentes cuando sea
posible. La búsqueda web será una herramienta separada del modelo.

## Fase 9 — Memoria y chats

### Objetivos

- Separar conversación temporal de memoria permanente.
- Crear chats independientes:
  - General.
  - Gaming.
  - Trabajo.
  - Proyecto Jarvis.
- Guardar preferencias solo cuando el usuario lo solicite.
- Consultar, editar y borrar memoria.
- Borrar un chat completo o toda la base.
- Permitir exportar la información antes de eliminarla.

### Datos previstos

```text
conversaciones
preferencias
tareas
recordatorios
rutinas
configuración
```

## Fase 10 — Funcionamiento nativo y bajo consumo

### Objetivos

- Iniciar Jarvis con Windows.
- Ejecutarse minimizado en la bandeja.
- Mantener solo el detector ligero en espera.
- Activar voz, transcripción e IA bajo demanda.
- Suspender Ollama durante Fortnite, GTA V o EA FC.
- Mostrar consumo aproximado y estado de los servicios.

### Criterio de rendimiento

Jarvis no debe competir innecesariamente con los juegos por CPU, RAM, GPU o
temperatura. La IA local pesada nunca debe permanecer activa sin necesidad.

## Fase 11 — Automatización avanzada

### Objetivos

- Crear rutinas con condiciones y horarios.
- Ejecutar secuencias con confirmación.
- Integrar calendario, tareas, Discord, Telegram o Home Assistant.
- Automatizar luces y dispositivos compatibles.
- Crear perfiles personales y permisos.

## Arquitectura objetivo

```text
jarvis/
├── core/
│   ├── wake_word.py
│   ├── speech_to_text.py
│   ├── text_to_speech.py
│   ├── command_router.py
│   ├── conversation.py
│   ├── memory.py
│   └── permissions.py
├── actions/
│   ├── applications.py
│   ├── music.py
│   ├── system.py
│   ├── routines.py
│   └── web.py
├── ui/
│   ├── window.py
│   ├── visualizer.py
│   └── tray.py
├── config/
├── data/
└── app.py
```

## Orden de prioridad

1. Interfaz real, cerrable y estable.
2. Micrófono y activación confiable por “Jarvis”.
3. Voz seleccionable y respuesta fluida.
4. Comandos naturales para aplicaciones.
5. Spotify con reproducción real.
6. Rutinas y modo gaming.
7. Conversación local con Ollama.
8. Búsqueda web y ayuda diaria.
9. Memoria editable y chats separados.
10. Inicio automático, optimización y automatizaciones.

Cada fase debe terminar con pruebas, documentación y un commit antes de
comenzar la siguiente.
