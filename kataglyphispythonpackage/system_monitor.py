"""System monitoring module for CPU, GPU, RAM usage tracking and visualization."""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import json

import psutil
import pandas as pd
from loguru import logger

try:
    import pynvml  # nvidia-ml-py package

    GPU_AVAILABLE = True
    # Initialize NVML
    pynvml.nvmlInit()
except (ImportError, Exception) as e:
    GPU_AVAILABLE = False
    logger.warning(
        f"nvidia-ml-py not available or initialization failed. GPU monitoring will be disabled. Error: {e}"
    )


class SystemMonitor:
    """Monitor system resources (CPU, GPU, RAM) and save data for later visualization."""

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the system monitor.

        Args:
            output_dir: Directory to save monitoring data. Defaults to './output/monitoring'
        """
        if output_dir is None:
            output_dir = Path("output/monitoring")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.monitoring_data: List[Dict] = []
        self.start_time: Optional[float] = None
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"SystemMonitor initialized. Output directory: {self.output_dir}")
        logger.info(f"Session ID: {self.session_id}")

    def get_cpu_info(self) -> Dict[str, float]:
        """Get current CPU usage information."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else 0.0,
        }

    def get_memory_info(self) -> Dict[str, float]:
        """Get current RAM usage information."""
        mem = psutil.virtual_memory()
        return {
            "ram_total_gb": mem.total / (1024**3),
            "ram_used_gb": mem.used / (1024**3),
            "ram_available_gb": mem.available / (1024**3),
            "ram_percent": mem.percent,
        }

    def get_gpu_info(self) -> List[Dict[str, float]]:
        """Get current GPU usage information using pynvml."""
        if not GPU_AVAILABLE:
            return []

        try:
            device_count = pynvml.nvmlDeviceGetCount()
            gpu_data = []

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)

                # Get GPU info
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")

                # Get utilization rates
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                # Get memory info
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_used_mb = memory.used / (1024**2)
                memory_total_mb = memory.total / (1024**2)
                memory_percent = (
                    (memory.used / memory.total * 100) if memory.total > 0 else 0
                )

                # Get temperature
                try:
                    temperature = pynvml.nvmlDeviceGetTemperature(
                        handle, pynvml.NVML_TEMPERATURE_GPU
                    )
                except pynvml.NVMLError:
                    temperature = 0.0

                gpu_data.append(
                    {
                        "gpu_id": i,
                        "gpu_name": name,
                        "gpu_load": float(utilization.gpu),  # Already in percentage
                        "gpu_memory_used_mb": memory_used_mb,
                        "gpu_memory_total_mb": memory_total_mb,
                        "gpu_memory_percent": memory_percent,
                        "gpu_temperature": float(temperature),
                    }
                )
            return gpu_data
        except Exception as e:
            logger.warning(f"Failed to get GPU info: {e}")
            return []

    def sample(self) -> Dict:
        """Take a single sample of all system metrics."""
        if self.start_time is None:
            self.start_time = time.time()

        timestamp = time.time()
        elapsed_time = timestamp - self.start_time

        sample_data = {
            "timestamp": timestamp,
            "elapsed_seconds": elapsed_time,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
        }

        # Add CPU info
        sample_data.update(self.get_cpu_info())

        # Add memory info
        sample_data.update(self.get_memory_info())

        # Add GPU info
        gpu_data = self.get_gpu_info()
        if gpu_data:
            # For simplicity, we'll track the first GPU primarily
            sample_data.update(
                {
                    f"gpu_{i}_{key}": value
                    for i, gpu in enumerate(gpu_data)
                    for key, value in gpu.items()
                }
            )

        self.monitoring_data.append(sample_data)
        return sample_data

    def start_monitoring(self, interval: float = 1.0, duration: Optional[float] = None):
        """
        Start continuous monitoring.

        Args:
            interval: Time between samples in seconds
            duration: Total monitoring duration in seconds. None for infinite
        """
        logger.info(
            f"Starting monitoring with interval={interval}s, duration={duration}s"
        )
        self.start_time = time.time()

        try:
            while True:
                sample = self.sample()
                logger.debug(
                    f"Sample: CPU={sample['cpu_percent']:.1f}%, RAM={sample['ram_percent']:.1f}%"
                )

                if duration and (time.time() - self.start_time) >= duration:
                    logger.info("Monitoring duration reached.")
                    break

                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user.")

    def save_data(self, filename: Optional[str] = None) -> Path:
        """
        Save monitoring data to CSV file.

        Args:
            filename: Output filename. Defaults to 'monitoring_{session_id}.csv'

        Returns:
            Path to saved file
        """
        if not self.monitoring_data:
            logger.warning("No monitoring data to save.")
            return None

        if filename is None:
            filename = f"monitoring_{self.session_id}.csv"

        output_path = self.output_dir / filename
        df = pd.DataFrame(self.monitoring_data)
        df.to_csv(output_path, index=False)

        logger.info(f"Monitoring data saved to {output_path}")
        logger.info(f"Total samples: {len(self.monitoring_data)}")

        return output_path

    def save_metadata(self, filename: Optional[str] = None) -> Path:
        """
        Save monitoring session metadata.

        Args:
            filename: Output filename. Defaults to 'monitoring_{session_id}_metadata.json'

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"monitoring_{self.session_id}_metadata.json"

        metadata = {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "sample_count": len(self.monitoring_data),
            "cpu_count": psutil.cpu_count(),
            "total_ram_gb": psutil.virtual_memory().total / (1024**3),
            "gpu_available": GPU_AVAILABLE,
        }

        if GPU_AVAILABLE:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                metadata["gpus"] = []
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode("utf-8")
                    metadata["gpus"].append({"id": i, "name": name})
            except Exception:
                pass

        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to {output_path}")
        return output_path

    def reset(self):
        """Reset monitoring data for a new session."""
        self.monitoring_data = []
        self.start_time = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Monitor reset. New session ID: {self.session_id}")


def monitor_function(func):
    """
    Decorator to monitor a function's execution.

    Example:
        @monitor_function
        def my_heavy_computation():
            # ... code ...
            pass
    """

    def wrapper(*args, **kwargs):
        monitor = SystemMonitor()
        logger.info(f"Starting monitoring for function: {func.__name__}")

        # Take a sample before
        monitor.sample()

        try:
            result = func(*args, **kwargs)
        finally:
            # Take a sample after
            monitor.sample()
            csv_path = monitor.save_data(
                f"monitor_{func.__name__}_{monitor.session_id}.csv"
            )
            monitor.save_metadata(
                f"monitor_{func.__name__}_{monitor.session_id}_metadata.json"
            )

        return result

    return wrapper
