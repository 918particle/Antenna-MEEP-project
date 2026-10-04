#!/usr/bin/env python3
"""
horn_radiation_patterns.py

Utilities for loading BAO HORN S21 CSV measurements and producing
ensemble-averaged E-plane and H-plane radiation-pattern plots.

Expected VNA CSV format (after three header lines):
    Frequency [Hz], S21 [dB], Phase [deg]

Typical filenames:
    BAO_HORN3_E(+35.0)_H(+0.0).CSV
    BAO_HORN3_E(+0.0)_H(+70.0).CSV

Typical folder names:
    BAO_HORN3_E-PLANE
    BAO_HORN3_H-PLANE

Primed data sets such as HORN5' can be excluded automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Iterable, Literal, Optional
import re
import zipfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

Plane = Literal["E", "H"]
NormalizeMode = Literal["ensemble", "per_horn"]


@dataclass(frozen=True)
class PatternResult:
    plane: str
    center_ghz: float
    band_low_ghz: float
    band_high_ghz: float
    angles_deg: np.ndarray
    gain_db: np.ndarray
    horns: tuple[int, ...]


class HornRadiationPatternAnalyzer:
    """Analyze angular S21 sweeps from the 3D-printed RF horn measurements."""

    _folder_re = re.compile(
        r"BAO_HORN(?P<horn>\d+)(?P<prime>')?_(?P<plane>[EH])-PLANE(?:_v\d+)?$",
        re.IGNORECASE,
    )
    _file_re = re.compile(
        r"BAO_HORN(?P<horn>\d+)_"
        r"E\((?P<e>[+\-]?\d+(?:\.\d+)?)\)_"
        r"H\((?P<h>[+\-]?\d+(?:\.\d+)?)\)\.CSV$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        source: str | Path,
        horns: Iterable[int] = range(1, 9),
        exclude_primed: bool = True,
    ) -> None:
        self.source = Path(source)
        self.horns = tuple(sorted(set(int(h) for h in horns)))
        self.exclude_primed = bool(exclude_primed)

        self.bin_centers_ghz = np.arange(6.0, 19.0, 1.0)
        self.bin_width_ghz = 1.0
        self.min_frequency_ghz = 5.5

        # data[horn][plane][angle_deg] = DataFrame
        self.data: dict[int, dict[str, dict[float, pd.DataFrame]]] = {}
        self.excluded_files: list[str] = []
        self._tmpdir: Optional[TemporaryDirectory] = None
        self._root: Optional[Path] = None

    # --------------------------- loading ---------------------------
    def load_data(self) -> "HornRadiationPatternAnalyzer":
        self.data.clear()
        self.excluded_files.clear()
        root = self._prepare_source()
        self._root = root

        for path in sorted(root.rglob("*.CSV")):
            folder = path.parent.name
            fm = self._folder_re.fullmatch(folder)
            mm = self._file_re.fullmatch(path.name)
            if fm is None or mm is None:
                continue

            horn = int(fm.group("horn"))
            plane = fm.group("plane").upper()
            is_primed = fm.group("prime") is not None

            if horn not in self.horns:
                continue
            if self.exclude_primed and is_primed:
                self.excluded_files.append(str(path))
                continue
            if int(mm.group("horn")) != horn:
                raise ValueError(f"Horn mismatch between folder and file: {path}")

            e_angle = float(mm.group("e"))
            h_angle = float(mm.group("h"))
            angle_deg = e_angle if plane == "E" else h_angle

            df = self._read_vna_csv(path)
            self.data.setdefault(horn, {}).setdefault(plane, {})[angle_deg] = df

        self._validate_loaded_data()
        return self

    def _prepare_source(self) -> Path:
        if self.source.is_dir():
            return self.source
        if self.source.suffix.lower() == ".zip":
            self._tmpdir = TemporaryDirectory(prefix="horn_patterns_")
            root = Path(self._tmpdir.name)
            with zipfile.ZipFile(self.source, "r") as zf:
                zf.extractall(root)
            return root
        raise ValueError("source must be a directory or ZIP archive")

    @staticmethod
    def _read_vna_csv(path: Path) -> pd.DataFrame:
        df = pd.read_csv(
            path,
            skiprows=3,
            header=None,
            names=["frequency_hz", "s21_db", "phase_deg"],
        )
        for col in ("frequency_hz", "s21_db", "phase_deg"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return (
            df.dropna(subset=["frequency_hz", "s21_db"])
            .sort_values("frequency_hz")
            .reset_index(drop=True)
        )

    def _validate_loaded_data(self) -> None:
        if not self.data:
            raise RuntimeError("No horn measurement CSV files were loaded.")
        missing = [h for h in self.horns if h not in self.data]
        if missing:
            raise RuntimeError(f"Requested horns not found: {missing}")
        for h in self.horns:
            for plane in ("E", "H"):
                if plane not in self.data[h]:
                    raise RuntimeError(f"HORN{h} is missing {plane}-plane data")

    # ---------------------- frequency binning ----------------------
    def set_frequency_binning(
        self,
        centers_ghz: Iterable[float],
        bin_width_ghz: float = 1.0,
        min_frequency_ghz: float = 5.5,
    ) -> "HornRadiationPatternAnalyzer":
        centers = np.asarray(list(centers_ghz), dtype=float)
        if centers.ndim != 1 or centers.size == 0:
            raise ValueError("centers_ghz must contain at least one value")
        if bin_width_ghz <= 0:
            raise ValueError("bin_width_ghz must be positive")
        self.bin_centers_ghz = centers
        self.bin_width_ghz = float(bin_width_ghz)
        self.min_frequency_ghz = float(min_frequency_ghz)
        return self

    def band_limits(self, center_ghz: float) -> tuple[float, float]:
        half = 0.5 * self.bin_width_ghz
        low = max(self.min_frequency_ghz, float(center_ghz) - half)
        high = float(center_ghz) + half
        return low, high

    # ---------------------- pattern calculations ----------------------
    def common_angles(self, plane: Plane) -> np.ndarray:
        plane = self._normalize_plane(plane)
        angle_sets = [set(self.data[h][plane]) for h in self.horns]
        return np.asarray(sorted(set.intersection(*angle_sets)), dtype=float)

    def get_horn_pattern(
        self,
        horn: int,
        plane: Plane,
        center_ghz: float,
        normalize: bool = True,
    ) -> tuple[np.ndarray, np.ndarray]:
        plane = self._normalize_plane(plane)
        low_ghz, high_ghz = self.band_limits(center_ghz)
        angles = self.common_angles(plane)

        values = np.array([
            self._band_average(
                self.data[horn][plane][float(angle)], low_ghz, high_ghz
            )
            for angle in angles
        ])

        if np.any(~np.isfinite(values)):
            raise RuntimeError(
                f"Missing bin samples for HORN{horn}, {plane}-plane, "
                f"{center_ghz:g} GHz"
            )
        if normalize:
            values = values - np.max(values)
        return angles, values

    def get_ensemble_pattern(
        self,
        plane: Plane,
        center_ghz: float,
        normalize_mode: NormalizeMode = "ensemble",
        angular_stride: int = 1,
    ) -> PatternResult:
        """
        Return an ensemble-average normalized pattern.

        normalize_mode='ensemble':
            Average binned S21[dB] across horns first, then set the ensemble
            maximum to 0 dB. This matches the most recent HORN1-HORN8 workflow.

        normalize_mode='per_horn':
            Normalize each horn to 0 dB first, then average the normalized
            patterns.
        """
        plane = self._normalize_plane(plane)
        if angular_stride < 1:
            raise ValueError("angular_stride must be >= 1")

        angles = self.common_angles(plane)
        low_ghz, high_ghz = self.band_limits(center_ghz)

        horn_patterns = []
        for horn in self.horns:
            _, values = self.get_horn_pattern(
                horn,
                plane,
                center_ghz,
                normalize=(normalize_mode == "per_horn"),
            )
            horn_patterns.append(values)

        ensemble = np.mean(np.vstack(horn_patterns), axis=0)
        if normalize_mode == "ensemble":
            ensemble = ensemble - np.max(ensemble)
        elif normalize_mode != "per_horn":
            raise ValueError("normalize_mode must be 'ensemble' or 'per_horn'")

        return PatternResult(
            plane=plane,
            center_ghz=float(center_ghz),
            band_low_ghz=low_ghz,
            band_high_ghz=high_ghz,
            angles_deg=angles[::angular_stride],
            gain_db=ensemble[::angular_stride],
            horns=self.horns,
        )

    def _band_average(
        self, df: pd.DataFrame, low_ghz: float, high_ghz: float
    ) -> float:
        f = df["frequency_hz"].to_numpy()
        s21 = df["s21_db"].to_numpy()
        mask = (
            (f >= low_ghz * 1e9)
            & (f <= high_ghz * 1e9)
            & (f >= self.min_frequency_ghz * 1e9)
        )
        if not np.any(mask):
            return np.nan
        return float(np.mean(s21[mask]))

    @staticmethod
    def _normalize_plane(plane: str) -> str:
        p = plane.upper().replace("-PLANE", "").strip()
        if p not in ("E", "H"):
            raise ValueError("plane must be 'E' or 'H'")
        return p

    # --------------------------- plotting ---------------------------
    def plot_polar(
        self,
        plane: Plane,
        center_ghz: float,
        *,
        ax=None,
        normalize_mode: NormalizeMode = "ensemble",
        angular_stride: int = 2,
        radial_limits_db: tuple[float, float] = (-30.0, 0.0),
        radial_ticks_db: Iterable[float] = (-30.0, -20.0, -10.0, 0.0),
        angular_tick_step_deg: float = 45.0,
        marker: Optional[str] = None,
        markersize: Optional[float] = None,
        title: Optional[str] = None,
        fontfamily: str = "Courier New",
        fontsize: float = 12.0,
        grid: bool = True,
        plot_kwargs: Optional[dict] = None,
        axes_customizer: Optional[Callable] = None,
    ):
        """
        Plot one polar radiation pattern and return (fig, ax, pattern).

        Default style matches the recent URSCA-style figures:
          E-plane = black circles
          H-plane = black crosses
          no connecting line
          radial range = -30 to 0 dB
          angular ticks every 45 degrees
          no title unless supplied
          angular_stride=2

        Pass an existing polar Axes via ``ax=...`` or use ``axes_customizer``
        for arbitrary Matplotlib customization.
        """
        pattern = self.get_ensemble_pattern(
            plane, center_ghz, normalize_mode, angular_stride
        )

        if ax is None:
            fig = plt.figure(figsize=(7.8, 7.8))
            ax = fig.add_subplot(111, projection="polar")
        else:
            fig = ax.figure

        marker = marker or ("o" if pattern.plane == "E" else "x")
        markersize = markersize or (4.0 if pattern.plane == "E" else 5.0)

        rmin_db, rmax_db = radial_limits_db
        if rmax_db <= rmin_db:
            raise ValueError("radial_limits_db must be (lower_db, upper_db)")

        clipped = np.clip(pattern.gain_db, rmin_db, rmax_db)
        radius = rmax_db - clipped
        theta = np.deg2rad(pattern.angles_deg)

        kwargs = dict(
            linestyle="None",
            marker=marker,
            color="black",
            markersize=markersize,
        )
        if plot_kwargs:
            kwargs.update(plot_kwargs)
        ax.plot(theta, radius, **kwargs)

        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)

        radial_span = rmax_db - rmin_db
        ax.set_rlim(radial_span, 0)

        ticks_db = np.asarray(list(radial_ticks_db), dtype=float)
        ax.set_rticks(rmax_db - ticks_db)
        ax.set_yticklabels([f"{x:g}" for x in ticks_db])
        ax.set_rlabel_position(135)
        ax.set_thetagrids(np.arange(0, 360, angular_tick_step_deg))
        ax.grid(grid, linewidth=0.6)

        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontfamily(fontfamily)
            lab.set_fontsize(fontsize)

        if title is not None:
            ax.set_title(title, fontfamily=fontfamily)

        if axes_customizer is not None:
            axes_customizer(ax, pattern)

        return fig, ax, pattern

    def plot_all_frequency_bins(
        self,
        plane: Plane,
        output_directory: str | Path,
        *,
        filename_template: str = "{plane}_plane_{frequency:g}GHz.png",
        dpi: int = 300,
        close: bool = True,
        **plot_polar_kwargs,
    ) -> list[Path]:
        output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        outputs = []

        for center in self.bin_centers_ghz:
            fig, ax, pattern = self.plot_polar(
                plane=plane,
                center_ghz=float(center),
                **plot_polar_kwargs,
            )
            path = output_directory / filename_template.format(
                plane=pattern.plane,
                frequency=pattern.center_ghz,
            )
            fig.savefig(path, dpi=dpi, bbox_inches="tight")
            outputs.append(path)
            if close:
                plt.close(fig)

        return outputs

    # ---------------------- optional beamwidth ----------------------
    def beamwidth_3db(
        self,
        plane: Plane,
        center_ghz: float,
        normalize_mode: NormalizeMode = "ensemble",
    ) -> dict[str, float]:
        """Return HPBW from the two -3 dB crossings around the main lobe."""
        p = self.get_ensemble_pattern(
            plane, center_ghz, normalize_mode, angular_stride=1
        )
        a = np.asarray(p.angles_deg)
        g = np.asarray(p.gain_db)

        peak_index = int(np.argmax(g))
        peak_angle = float(a[peak_index])

        rel = ((a - peak_angle + 180.0) % 360.0) - 180.0
        order = np.argsort(rel)
        rel = rel[order]
        g = g[order]
        i0 = int(np.argmin(np.abs(rel)))
        level = -3.0

        left = None
        for i in range(i0, 0, -1):
            if g[i] >= level and g[i - 1] <= level:
                left = self._linear_crossing(
                    rel[i], g[i], rel[i - 1], g[i - 1], level
                )
                break

        right = None
        for i in range(i0, len(rel) - 1):
            if g[i] >= level and g[i + 1] <= level:
                right = self._linear_crossing(
                    rel[i], g[i], rel[i + 1], g[i + 1], level
                )
                break

        beamwidth = np.nan if left is None or right is None else right - left
        return {
            "frequency_ghz": float(center_ghz),
            "peak_angle_deg": peak_angle,
            "left_3db_relative_deg": np.nan if left is None else float(left),
            "right_3db_relative_deg": np.nan if right is None else float(right),
            "beamwidth_deg": float(beamwidth),
        }

    @staticmethod
    def _linear_crossing(x1, y1, x2, y2, level) -> float:
        if y2 == y1:
            return 0.5 * (x1 + x2)
        return x1 + (level - y1) * (x2 - x1) / (y2 - y1)


if __name__ == "__main__":
    analyzer = HornRadiationPatternAnalyzer("BAO_HORN.zip")
    analyzer.load_data()

    analyzer.set_frequency_binning(
        centers_ghz=range(6, 19),
        bin_width_ghz=1.0,
        min_frequency_ghz=5.5,
    )

    fig, ax, pattern = analyzer.plot_polar(
        plane="E",
        center_ghz=6.0,
        angular_stride=2,
        radial_limits_db=(-30, 0),
        title=None,
    )
    fig.savefig("E_plane_6GHz.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    analyzer.plot_all_frequency_bins(
        "E",
        "plots/E_plane",
        angular_stride=2,
        radial_limits_db=(-30, 0),
        title=None,
    )

    analyzer.plot_all_frequency_bins(
        "H",
        "plots/H_plane",
        angular_stride=2,
        radial_limits_db=(-30, 0),
        title=None,
    )

    print(analyzer.beamwidth_3db("H", 10.0))
