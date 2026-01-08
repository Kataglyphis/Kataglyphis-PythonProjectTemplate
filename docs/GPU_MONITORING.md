# GPU Monitoring with nvidia-ml-py

## Was ist nvidia-ml-py?

`nvidia-ml-py` ist die **offizielle NVIDIA Management Library** für Python. Es ist die moderne, aktiv gewartete Alternative zu `GPUtil` (das seit 2018 nicht mehr aktualisiert wurde).

## Installation

```bash
pip install nvidia-ml-py
```

## Warum die FutureWarning?

Wenn Sie beim Import eine Warnung sehen wie:
```
FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead.
```

**Das ist normal!** Das Paket `nvidia-ml-py` verwendet intern den Modul-Namen `pynvml` für Rückwärtskompatibilität. Die Warnung erscheint, weil das alte separate `pynvml`-Paket deprecated ist, aber `nvidia-ml-py` ist das richtige und aktuelle Paket.

**Lösung:** Einfach ignorieren oder mit dem folgenden Code unterdrücken:

```python
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="pynvml")
import pynvml  # nvidia-ml-py
```

## Vorteile gegenüber GPUtil

- ✅ **Aktiv gewartet** (letzte Version: 2024)
- ✅ **Offiziell von NVIDIA** unterstützt
- ✅ **Mehr Features**: detaillierte GPU-Metriken, Prozess-Monitoring, etc.
- ✅ **Bessere Performance**
- ✅ **Unterstützung für neue GPU-Modelle**

GPUtil wurde seit 2018 nicht mehr aktualisiert und fehlt Unterstützung für moderne GPUs (RTX 40xx Serie, H100, etc.).

## Kompatibilität

- Funktioniert nur mit **NVIDIA GPUs**
- Benötigt installierte **NVIDIA Treiber**
- Prüfen mit: `nvidia-smi`

## API-Unterschiede

### GPUtil (alt)
```python
import GPUtil
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(gpu.load, gpu.memoryUsed)
```

### nvidia-ml-py (neu)
```python
import pynvml
pynvml.nvmlInit()
count = pynvml.nvmlDeviceGetCount()
for i in range(count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(util.gpu, mem.used)
```

Die SystemMonitor-Klasse abstrahiert diese Details für Sie!
