"""Unit tests for system monitoring module."""

import time
from pathlib import Path
import pytest
import pandas as pd

from kataglyphispythonpackage.system_monitor import SystemMonitor, monitor_function


class TestSystemMonitor:
    """Test cases for SystemMonitor class."""

    @pytest.fixture
    def monitor(self, tmp_path):
        """Create a SystemMonitor instance with temporary output directory."""
        return SystemMonitor(output_dir=tmp_path)

    def test_initialization(self, monitor, tmp_path):
        """Test that monitor initializes correctly."""
        assert monitor.output_dir == tmp_path
        assert monitor.output_dir.exists()
        assert monitor.monitoring_data == []
        assert monitor.start_time is None
        assert monitor.session_id is not None

    def test_get_cpu_info(self, monitor):
        """Test CPU information retrieval."""
        cpu_info = monitor.get_cpu_info()
        assert "cpu_percent" in cpu_info
        assert "cpu_count" in cpu_info
        assert "cpu_freq_current" in cpu_info
        assert cpu_info["cpu_percent"] >= 0
        assert cpu_info["cpu_count"] > 0

    def test_get_memory_info(self, monitor):
        """Test memory information retrieval."""
        mem_info = monitor.get_memory_info()
        assert "ram_total_gb" in mem_info
        assert "ram_used_gb" in mem_info
        assert "ram_available_gb" in mem_info
        assert "ram_percent" in mem_info
        assert mem_info["ram_total_gb"] > 0
        assert mem_info["ram_percent"] >= 0
        assert mem_info["ram_percent"] <= 100

    def test_get_gpu_info(self, monitor):
        """Test GPU information retrieval."""
        gpu_info = monitor.get_gpu_info()
        # GPU info might be empty list if no GPU available
        assert isinstance(gpu_info, list)

    def test_sample(self, monitor):
        """Test taking a single sample."""
        sample = monitor.sample()

        # Check that sample contains expected keys
        assert "timestamp" in sample
        assert "elapsed_seconds" in sample
        assert "datetime" in sample
        assert "cpu_percent" in sample
        assert "ram_percent" in sample

        # Check that start_time was set
        assert monitor.start_time is not None

        # Check that sample was added to monitoring_data
        assert len(monitor.monitoring_data) == 1

    def test_multiple_samples(self, monitor):
        """Test taking multiple samples."""
        for _ in range(5):
            monitor.sample()
            time.sleep(0.1)

        assert len(monitor.monitoring_data) == 5

        # Check that elapsed_seconds increases
        assert (
            monitor.monitoring_data[1]["elapsed_seconds"]
            > monitor.monitoring_data[0]["elapsed_seconds"]
        )
        assert (
            monitor.monitoring_data[4]["elapsed_seconds"]
            > monitor.monitoring_data[0]["elapsed_seconds"]
        )

    def test_save_data(self, monitor, tmp_path):
        """Test saving monitoring data to CSV."""
        # Take some samples
        for _ in range(3):
            monitor.sample()

        # Save data
        csv_path = monitor.save_data(filename="test_monitoring.csv")

        # Check that file exists
        assert csv_path.exists()
        assert csv_path.parent == tmp_path

        # Check that CSV can be loaded
        df = pd.read_csv(csv_path)
        assert len(df) == 3
        assert "cpu_percent" in df.columns
        assert "ram_percent" in df.columns

    def test_save_data_no_samples(self, monitor):
        """Test saving data when no samples have been taken."""
        result = monitor.save_data()
        assert result is None

    def test_save_metadata(self, monitor, tmp_path):
        """Test saving metadata."""
        # Take a sample first
        monitor.sample()

        # Save metadata
        metadata_path = monitor.save_metadata(filename="test_metadata.json")

        # Check that file exists
        assert metadata_path.exists()
        assert metadata_path.parent == tmp_path

        # Check that file contains valid JSON
        import json

        with open(metadata_path) as f:
            metadata = json.load(f)

        assert "session_id" in metadata
        assert "sample_count" in metadata
        assert metadata["sample_count"] == 1

    def test_reset(self, monitor):
        """Test resetting the monitor."""
        # Take some samples
        monitor.sample()
        monitor.sample()
        old_session_id = monitor.session_id

        # Reset
        time.sleep(1)  # Ensure new timestamp
        monitor.reset()

        # Check that data was cleared
        assert len(monitor.monitoring_data) == 0
        assert monitor.start_time is None
        assert monitor.session_id != old_session_id

    def test_start_monitoring_with_duration(self, monitor):
        """Test continuous monitoring with duration limit."""
        duration = 2
        start = time.time()
        monitor.start_monitoring(interval=0.5, duration=duration)
        elapsed = time.time() - start

        # Should have stopped after duration
        assert elapsed >= duration
        assert elapsed < duration + 1  # Allow some overhead

        # Should have taken approximately duration/interval samples
        expected_samples = int(duration / 0.5)
        assert len(monitor.monitoring_data) >= expected_samples


class TestMonitorDecorator:
    """Test cases for monitor_function decorator."""

    def test_decorator_basic(self, tmp_path):
        """Test that decorator monitors function execution."""

        @monitor_function
        def test_function():
            time.sleep(0.1)
            return 42

        result = test_function()

        # Check that function returned correctly
        assert result == 42

        # Check that monitoring files were created
        monitoring_dir = Path("output/monitoring")
        assert monitoring_dir.exists()

        # Should have created CSV file
        csv_files = list(monitoring_dir.glob("monitor_test_function_*.csv"))
        assert len(csv_files) > 0

    def test_decorator_preserves_exceptions(self):
        """Test that decorator doesn't suppress exceptions."""

        @monitor_function
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()


class TestMonitoringIntegration:
    """Integration tests for complete monitoring workflow."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: monitor, save, load."""
        # Create monitor
        monitor = SystemMonitor(output_dir=tmp_path)

        # Take samples
        for _ in range(5):
            monitor.sample()
            time.sleep(0.1)

        # Save data
        csv_path = monitor.save_data()
        monitor.save_metadata()

        # Load and verify
        df = pd.read_csv(csv_path)
        assert len(df) == 5
        assert df["elapsed_seconds"].is_monotonic_increasing
        assert all(df["cpu_percent"] >= 0)
        assert all(df["ram_percent"] >= 0)
        assert all(df["ram_percent"] <= 100)
