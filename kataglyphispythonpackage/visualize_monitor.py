"""Visualization tools for system monitoring data."""

from pathlib import Path
from typing import Optional, Union, List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from loguru import logger


class MonitoringVisualizer:
    """Visualize system monitoring data from CSV files."""

    def __init__(self, csv_path: Union[str, Path]):
        """
        Initialize the visualizer with monitoring data.

        Args:
            csv_path: Path to the monitoring CSV file
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Monitoring data file not found: {self.csv_path}")

        self.df = pd.read_csv(self.csv_path)
        logger.info(
            f"Loaded monitoring data: {len(self.df)} samples from {self.csv_path}"
        )

    def plot_cpu(self, ax: Optional[plt.Axes] = None, show: bool = False) -> plt.Axes:
        """
        Plot CPU usage over time.

        Args:
            ax: Matplotlib axes to plot on. Creates new if None
            show: Whether to display the plot immediately

        Returns:
            The axes object with the plot
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 4))

        ax.plot(
            self.df["elapsed_seconds"],
            self.df["cpu_percent"],
            label="CPU Usage",
            color="blue",
            linewidth=2,
        )
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("CPU Usage (%)")
        ax.set_title("CPU Usage Over Time")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 100)

        if show:
            plt.tight_layout()
            plt.show()

        return ax

    def plot_memory(
        self, ax: Optional[plt.Axes] = None, show: bool = False
    ) -> plt.Axes:
        """
        Plot RAM usage over time.

        Args:
            ax: Matplotlib axes to plot on. Creates new if None
            show: Whether to display the plot immediately

        Returns:
            The axes object with the plot
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 4))

        ax.plot(
            self.df["elapsed_seconds"],
            self.df["ram_percent"],
            label="RAM Usage",
            color="green",
            linewidth=2,
        )
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("RAM Usage (%)")
        ax.set_title("RAM Usage Over Time")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 100)

        # Add secondary y-axis for absolute values
        ax2 = ax.twinx()
        ax2.plot(
            self.df["elapsed_seconds"],
            self.df["ram_used_gb"],
            label="RAM Used (GB)",
            color="darkgreen",
            linewidth=1,
            linestyle="--",
            alpha=0.6,
        )
        ax2.set_ylabel("RAM Used (GB)")
        ax2.legend(loc="upper right")

        if show:
            plt.tight_layout()
            plt.show()

        return ax

    def plot_gpu(
        self, gpu_id: int = 0, ax: Optional[plt.Axes] = None, show: bool = False
    ) -> Optional[plt.Axes]:
        """
        Plot GPU usage over time.

        Args:
            gpu_id: GPU ID to plot
            ax: Matplotlib axes to plot on. Creates new if None
            show: Whether to display the plot immediately

        Returns:
            The axes object with the plot, or None if GPU data not available
        """
        gpu_load_col = f"gpu_{gpu_id}_gpu_load"
        gpu_mem_col = f"gpu_{gpu_id}_gpu_memory_percent"

        if gpu_load_col not in self.df.columns:
            logger.warning(f"GPU {gpu_id} data not found in monitoring file")
            return None

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 4))

        ax.plot(
            self.df["elapsed_seconds"],
            self.df[gpu_load_col],
            label=f"GPU {gpu_id} Load",
            color="red",
            linewidth=2,
        )
        ax.plot(
            self.df["elapsed_seconds"],
            self.df[gpu_mem_col],
            label=f"GPU {gpu_id} Memory",
            color="orange",
            linewidth=2,
        )
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Usage (%)")
        ax.set_title(f"GPU {gpu_id} Usage Over Time")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 100)

        if show:
            plt.tight_layout()
            plt.show()

        return ax

    def plot_all(
        self, output_path: Optional[Union[str, Path]] = None, show: bool = True
    ) -> Figure:
        """
        Create a comprehensive plot with all monitoring data.

        Args:
            output_path: Path to save the figure. If None, doesn't save
            show: Whether to display the plot

        Returns:
            The matplotlib Figure object
        """
        # Check if GPU data is available
        has_gpu = any(col.startswith("gpu_0_") for col in self.df.columns)

        # Create subplots
        n_plots = 3 if has_gpu else 2
        fig, axes = plt.subplots(n_plots, 1, figsize=(14, 4 * n_plots))

        if n_plots == 2:
            axes = list(axes)

        # Plot CPU
        self.plot_cpu(ax=axes[0])

        # Plot Memory
        self.plot_memory(ax=axes[1])

        # Plot GPU if available
        if has_gpu:
            self.plot_gpu(gpu_id=0, ax=axes[2])

        # Add overall title
        fig.suptitle(f"System Monitoring - {self.csv_path.stem}", fontsize=16, y=0.995)

        plt.tight_layout()

        # Save if requested
        if output_path:
            output_path = Path(output_path)
            fig.savefig(output_path, dpi=150, bbox_inches="tight")
            logger.info(f"Figure saved to {output_path}")

        # Show if requested
        if show:
            plt.show()

        return fig

    def get_statistics(self) -> dict:
        """
        Calculate statistics for the monitoring session.

        Returns:
            Dictionary with various statistics
        """
        stats = {
            "duration_seconds": self.df["elapsed_seconds"].max(),
            "sample_count": len(self.df),
            "cpu": {
                "mean": self.df["cpu_percent"].mean(),
                "max": self.df["cpu_percent"].max(),
                "min": self.df["cpu_percent"].min(),
                "std": self.df["cpu_percent"].std(),
            },
            "ram": {
                "mean_percent": self.df["ram_percent"].mean(),
                "max_percent": self.df["ram_percent"].max(),
                "mean_used_gb": self.df["ram_used_gb"].mean(),
                "max_used_gb": self.df["ram_used_gb"].max(),
            },
        }

        # Add GPU stats if available
        if "gpu_0_gpu_load" in self.df.columns:
            stats["gpu_0"] = {
                "mean_load": self.df["gpu_0_gpu_load"].mean(),
                "max_load": self.df["gpu_0_gpu_load"].max(),
                "mean_memory_percent": self.df["gpu_0_gpu_memory_percent"].mean(),
                "max_memory_percent": self.df["gpu_0_gpu_memory_percent"].max(),
            }

        return stats

    def print_summary(self):
        """Print a summary of the monitoring session."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("MONITORING SESSION SUMMARY")
        print("=" * 60)
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"Samples: {stats['sample_count']}")
        print("\n--- CPU ---")
        print(f"  Mean: {stats['cpu']['mean']:.2f}%")
        print(f"  Max:  {stats['cpu']['max']:.2f}%")
        print(f"  Min:  {stats['cpu']['min']:.2f}%")
        print("\n--- RAM ---")
        print(
            f"  Mean: {stats['ram']['mean_percent']:.2f}% ({stats['ram']['mean_used_gb']:.2f} GB)"
        )
        print(
            f"  Max:  {stats['ram']['max_percent']:.2f}% ({stats['ram']['max_used_gb']:.2f} GB)"
        )

        if "gpu_0" in stats:
            print("\n--- GPU 0 ---")
            print(f"  Mean Load: {stats['gpu_0']['mean_load']:.2f}%")
            print(f"  Max Load:  {stats['gpu_0']['max_load']:.2f}%")
            print(f"  Mean Memory: {stats['gpu_0']['mean_memory_percent']:.2f}%")
            print(f"  Max Memory:  {stats['gpu_0']['max_memory_percent']:.2f}%")

        print("=" * 60 + "\n")


def visualize_monitoring_file(
    csv_path: Union[str, Path], output_dir: Optional[Union[str, Path]] = None
):
    """
    Convenience function to visualize a monitoring file.

    Args:
        csv_path: Path to monitoring CSV file
        output_dir: Directory to save plots. If None, uses same dir as CSV
    """
    csv_path = Path(csv_path)
    if output_dir is None:
        output_dir = csv_path.parent

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    vis = MonitoringVisualizer(csv_path)
    vis.print_summary()

    output_path = output_dir / f"{csv_path.stem}_visualization.png"
    vis.plot_all(output_path=output_path, show=False)

    logger.info(f"Visualization complete. Saved to {output_path}")
