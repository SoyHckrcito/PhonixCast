# PhonixCast

Prototipo de app para compartir la pantalla de un teléfono Android a un PC por USB, con un enfoque tipo **scrcpy**, pero orientado a ser más simple de operar en campo.

## Objetivo

Permitir que una persona conecte un teléfono por USB y comience la transmisión de pantalla de forma rápida, con:

- Detección automática de dispositivos.
- Perfiles de baja latencia.
- Validaciones previas para evitar errores comunes.
- Atajos para tareas típicas (pantalla apagada en el teléfono, bitrate, FPS, etc.).

## Requisitos

- Python 3.10+
- `adb` disponible en `PATH`
- `scrcpy` disponible en `PATH`
- Android con Depuración USB habilitada

## Uso rápido

```bash
python3 app/main.py start --profile ultra-low-latency
```

Para listar dispositivos detectados:

```bash
python3 app/main.py devices
```

Para ver perfiles disponibles:

```bash
python3 app/main.py profiles
```

## Perfiles incluidos

- `balanced`: buena calidad general.
- `low-latency`: prioriza respuesta.
- `ultra-low-latency`: máxima prioridad a latencia mínima.

## Ejemplo completo

```bash
python3 app/main.py start \
  --profile low-latency \
  --max-size 1280 \
  --turn-screen-off \
  --stay-awake
```

## Roadmap sugerido

1. Interfaz gráfica (Qt/Tauri/Electron).
2. Modo “one-click” para usuarios no técnicos.
3. Diagnóstico en tiempo real (latencia estimada, bitrate efectivo, pérdida de frames).
4. Instalador para Windows/macOS/Linux.
