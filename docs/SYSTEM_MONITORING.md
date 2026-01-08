# System Monitoring

Dieses Modul ermöglicht das Monitoring von System-Ressourcen (CPU, GPU, RAM) und die spätere Visualisierung der gesammelten Daten.

## Features

- **CPU-Monitoring**: Prozessorauslastung in Prozent
- **RAM-Monitoring**: Speicherauslastung (absolut und prozentual)
- **GPU-Monitoring**: GPU-Last und Speicher (wenn GPU verfügbar)
- **Automatisches Speichern**: Daten werden als CSV gespeichert
- **Visualisierung**: Erstellt Plots für alle gesammelten Metriken
- **Decorator-Support**: Einfaches Monitoring von Funktionen

## Installation

Installieren Sie die zusätzlichen Abhängigkeiten:

```bash
pip install psutil nvidia-ml-py matplotlib pandas
```

Oder installieren Sie das gesamte Paket mit:

```bash
pip install -e .
```

## Verwendung

### 1. Einfaches manuelles Monitoring

```python
from kataglyphispythonpackage.system_monitor import SystemMonitor
from kataglyphispythonpackage.visualize_monitor import visualize_monitoring_file

# Monitor erstellen
monitor = SystemMonitor(output_dir="output/monitoring")

# Samples manuell nehmen
for i in range(10):
    sample = monitor.sample()
    print(f"CPU: {sample['cpu_percent']:.1f}%, RAM: {sample['ram_percent']:.1f}%")
    time.sleep(1)

# Daten speichern
csv_path = monitor.save_data()
monitor.save_metadata()

# Visualisieren
visualize_monitoring_file(csv_path)
```

### 2. Kontinuierliches Monitoring

```python
monitor = SystemMonitor()

# Monitoring für 60 Sekunden mit 1s Intervall
monitor.start_monitoring(interval=1.0, duration=60)

# Daten speichern und visualisieren
csv_path = monitor.save_data()
visualize_monitoring_file(csv_path)
```

### 3. Monitoring mit Decorator

```python
from kataglyphispythonpackage.system_monitor import monitor_function

@monitor_function
def meine_rechenintensive_funktion():
    # Ihr Code hier
    result = sum(i**2 for i in range(1_000_000))
    return result

# Automatisch wird beim Aufruf überwacht
result = meine_rechenintensive_funktion()
# Daten werden automatisch gespeichert in output/monitoring/
```

### 4. Visualisierung existierender Daten

```python
from kataglyphispythonpackage.visualize_monitor import MonitoringVisualizer

# Visualizer erstellen
vis = MonitoringVisualizer("output/monitoring/monitoring_20260107_120000.csv")

# Statistiken anzeigen
vis.print_summary()

# Einzelne Plots erstellen
vis.plot_cpu(show=True)
vis.plot_memory(show=True)
vis.plot_gpu(gpu_id=0, show=True)

# Oder alle Plots zusammen
vis.plot_all(output_path="monitoring_results.png", show=True)

# Statistiken programmatisch abrufen
stats = vis.get_statistics()
print(f"Durchschnittliche CPU-Last: {stats['cpu']['mean']:.2f}%")
```

## Demo ausführen

Ein vollständiges Demo-Skript ist verfügbar:

```bash
python examples/demo_system_monitoring.py
```

Das Demo zeigt:
1. Grundlegendes manuelles Monitoring
2. Monitoring während einer Berechnung
3. Decorator-basiertes Monitoring
4. Kontinuierliches Monitoring

## Output-Struktur

Die Monitoring-Daten werden standardmäßig in `output/monitoring/` gespeichert:

```
output/monitoring/
├── monitoring_20260107_120000.csv          # Zeitreihen-Daten
├── monitoring_20260107_120000_metadata.json # Session-Metadaten
└── monitoring_20260107_120000_visualization.png # Grafiken
```

### CSV-Format

Die CSV-Datei enthält folgende Spalten:

- `timestamp`: Unix-Timestamp
- `elapsed_seconds`: Verstrichene Zeit seit Start
- `datetime`: ISO-formatiertes Datum/Uhrzeit
- `cpu_percent`: CPU-Auslastung (%)
- `cpu_count`: Anzahl CPU-Kerne
- `cpu_freq_current`: Aktuelle CPU-Frequenz (MHz)
- `ram_total_gb`: Gesamter RAM (GB)
- `ram_used_gb`: Verwendeter RAM (GB)
- `ram_available_gb`: Verfügbarer RAM (GB)
- `ram_percent`: RAM-Auslastung (%)
- `gpu_0_gpu_id`: GPU-ID (wenn vorhanden)
- `gpu_0_gpu_name`: GPU-Name
- `gpu_0_gpu_load`: GPU-Last (%)
- `gpu_0_gpu_memory_used_mb`: GPU-Speicher verwendet (MB)
- `gpu_0_gpu_memory_total_mb`: GPU-Gesamtspeicher (MB)
- `gpu_0_gpu_memory_percent`: GPU-Speicher (%)
- `gpu_0_gpu_temperature`: GPU-Temperatur (°C)

## Anwendungsfälle

- **Performance-Tests**: Überwachen Sie Ressourcennutzung während Tests
- **Benchmarking**: Vergleichen Sie verschiedene Implementierungen
- **Debugging**: Identifizieren Sie Speicherlecks oder CPU-Spitzen
- **Profiling**: Langzeit-Monitoring von Produktionsanwendungen
- **Dokumentation**: Erstellen Sie Visualisierungen für Reports

## Erweiterte Nutzung

### Eigene Metriken hinzufügen

Sie können die `SystemMonitor`-Klasse erweitern:

```python
class CustomMonitor(SystemMonitor):
    def sample(self):
        data = super().sample()
        # Fügen Sie eigene Metriken hinzu
        data['custom_metric'] = self.get_custom_metric()
        return data
    
    def get_custom_metric(self):
        # Ihre eigene Metrik-Logik
        return 42.0
```

### Integration in Tests

```python
import pytest
from kataglyphispythonpackage.system_monitor import SystemMonitor

@pytest.fixture
def monitor():
    m = SystemMonitor(output_dir="output/test_monitoring")
    yield m
    m.save_data()

def test_heavy_operation(monitor):
    monitor.sample()  # Vor dem Test
    
    # Ihr Test
    heavy_computation()
    
    monitor.sample()  # Nach dem Test
```

## Troubleshooting

### GPU-Monitoring funktioniert nicht

Wenn GPU-Monitoring nicht funktioniert:
- Stellen Sie sicher, dass NVIDIA-GPU vorhanden ist
- Installieren Sie `nvidia-ml-py`: `pip install nvidia-ml-py`
- Überprüfen Sie NVIDIA-Treiber: `nvidia-smi`
- nvidia-ml-py ist die offizielle NVIDIA Management Library und funktioniert nur mit NVIDIA-GPUs

### Fehlende Berechtigungen

Unter Linux können einige Metriken Root-Rechte benötigen. Führen Sie ggf. mit `sudo` aus.

### Hoher Overhead

Wenn das Monitoring selbst zu viele Ressourcen verbraucht:
- Erhöhen Sie das Sampling-Intervall (`interval=2.0` statt `1.0`)
- Deaktivieren Sie GPU-Monitoring wenn nicht benötigt
- Verwenden Sie `cpu_percent(interval=None)` für schnelleres Polling

## Lizenz

Siehe Haupt-README des Projekts.
