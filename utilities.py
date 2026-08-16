from pathlib import Path

import matplotlib.pyplot as plt
import meep as mp
import numpy as np
import pandas as pd

from models import RadPatternResults


def _load_rad_results_from_csv(results_file: Path | str) -> RadPatternResults:
    results_file = Path(results_file)
    if not results_file.suffix:
        results_file = results_file.with_suffix(".csv")
    if not results_file.exists():
        raise FileNotFoundError(
            f"The provided path for results does not exist: {results_file}"
        )
    df = pd.read_csv(results_file)

    frequencies = df["frequency"].drop_duplicates().to_numpy()
    angles = df["angle"].drop_duplicates().to_numpy()
    base_directivity = (
        df.pivot(
            index="frequency",
            columns="angle",
            values="base_directivity",
        )
        .reindex(index=frequencies, columns=angles)
        .to_numpy()
    )
    sweep_directivity = (
        df.pivot(
            index="frequency",
            columns="angle",
            values="sweep_directivity",
        )
        .reindex(index=frequencies, columns=angles)
        .to_numpy()
    )

    return RadPatternResults(
        frequencies=frequencies,
        angles=angles,
        base_directivity=base_directivity,
        sweep_directivity=sweep_directivity,
        df=df,
    )


def resolve_output_folder(output_folder: Path | str) -> Path:
    output_folder = Path(output_folder).resolve()
    results_dir = (Path(__name__).parent / "results").resolve()
    if output_folder.is_relative_to(results_dir):
        return output_folder
    return results_dir / output_folder.name


def plot_radiation_pattern(
    sim_results: RadPatternResults | Path | str,
    output_folder: Path | str,
    lab_data_file: Path | str | None = None,
):
    output_folder = resolve_output_folder(output_folder)
    if not isinstance(sim_results, RadPatternResults):
        sim_results = _load_rad_results_from_csv(sim_results)

    for i, frequency in enumerate(sim_results.frequencies):
        fig = plt.figure(dpi=300)
        plt.polar(
            sim_results.angles,
            sim_results.sweep_directivity[i],
            color="black",
            label="simulation",
        )
        if lab_data_file:
            if not Path(lab_data_file).exists():
                lab_data_file = Path("lab_data") / lab_data_file
            x, y = np.loadtxt(lab_data_file, unpack=True)
            x *= np.pi / 180.0
            plt.polar(x, y, "o", color="black", label="lab")
        ax = fig.gca()
        ax.set_rlim(-26, 1)
        ax.set_rticks([-15, -3])
        ax.grid(True)
        ax.set_rlabel_position(180)
        ax.tick_params(labelsize=18)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        file_name = Path(output_folder) / f"rad_pattern_{str(frequency).replace(".", "_")}"
        plt.savefig(file_name)
        plt.close()


def plot_surfaces(sim: mp.Simulation, output_folder: Path | str):
    output_folder = resolve_output_folder(output_folder)
    f = plt.figure(dpi=300)
    sim.plot2D(ax=f.gca())
    file_name = Path(output_folder) / "surfaces.png"
    plt.savefig(file_name)
    plt.close()
