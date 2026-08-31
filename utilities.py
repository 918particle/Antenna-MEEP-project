from pathlib import Path

import matplotlib.pyplot as plt
import meep as mp
import numpy as np
import pandas as pd

from models import RadPatternResults, VSWRResults


def _load_sim_rad_results_from_csv(results_file: Path | str) -> RadPatternResults:
    results_file = Path(results_file).resolve()
    if not results_file.suffix:
        results_file = results_file.with_suffix(".csv")
    if not results_file.exists():
        raise FileNotFoundError(
            f"The provided path for results does not exist: {results_file}"
        )
    df = pd.read_csv(results_file)

    steering_beam_base_frequency = df["steering_beam_base_frequency"][0]
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
        steering_beam_base_frequency=steering_beam_base_frequency,
        frequencies=frequencies,
        angles=angles,
        base_directivity=base_directivity,
        sweep_directivity=sweep_directivity,
        df=df,
    )


def _load_sim_vswr_results_from_csv(results_file: Path | str) -> VSWRResults:
    results_file = Path(results_file).resolve()
    if not results_file.suffix:
        results_file = results_file.with_suffix(".csv")
    if not results_file.exists():
        raise FileNotFoundError(
            f"The provided path for results does not exist: {results_file}"
        )
    df = pd.read_csv(results_file)

    return VSWRResults(
        frequencies=df["frequency"].to_numpy(),
        gamma=df["gamma"].to_numpy(),
        vswr=df["vswr"].to_numpy,
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
        sim_results = _load_sim_rad_results_from_csv(sim_results)

    for i, frequency in enumerate(sim_results.frequencies):
        frequency = f"{frequency:.4f}"
        fig = plt.figure(dpi=300)
        plt.polar(
            sim_results.angles,
            sim_results.sweep_directivity[i],
            color="black",
            label=f"simulation-{frequency}",
        )
        plt.polar(
            sim_results.angles,
            sim_results.base_directivity[i],
            color="blue",
            label=f"simulation-base-{sim_results.steering_beam_base_frequency}",
        )
        if lab_data_file:
            if not Path(lab_data_file).exists():
                lab_data_file = Path("lab_data") / lab_data_file
            lab_angles, lab_directivity = np.loadtxt(lab_data_file, unpack=True)
            lab_angles *= np.pi / 180.0
            plt.polar(lab_angles, lab_directivity, "o", color="black", label="lab")
        ax = fig.gca()
        ax.set_rlim(-26, 1)
        ax.set_rticks([-15, -3])
        ax.grid(True)
        ax.set_rlabel_position(180)
        ax.tick_params(labelsize=18)
        plt.legend(bbox_to_anchor=(1, 1.02), loc="upper left")

        file_name = Path(output_folder) / f"rad_pattern_{frequency.replace('.', '_')}"
        plt.savefig(file_name, bbox_inches="tight")
        plt.close()


def plot_vswr(
    sim_results: VSWRResults | Path | str,
    output_folder: Path | str,
    lab_data_file: Path | str | None = None,
):
    output_folder = resolve_output_folder(output_folder)
    if not isinstance(sim_results, VSWRResults):
        sim_results = _load_sim_vswr_results_from_csv(sim_results)

    plt.figure(dpi=300)
    plt.plot(
        sim_results.frequencies,
        sim_results.vswr,
        color="black",
        linewidth=2,
        label="MEEP sim",
    )
    # plt.xlim(0, 20)
    # plt.ylim(0, 10)
    # plt.xticks(np.arange(0, 21, 2), fontsize=20)
    # plt.yticks(np.arange(0, 11, 2), fontsize=20)
    plt.xlabel("Frequency", fontsize=20)
    plt.ylabel("VSWR", fontsize=20)

    if lab_data_file:
        if not Path(lab_data_file).exists():
            lab_data_file = Path("lab_data") / lab_data_file
        lab_frequencies, _, lab_vswr = np.loadtxt(lab_data_file, unpack=True)
        plt.plot(
            lab_frequencies, lab_vswr, "o", color="black", linewidth=2, label="Lab data"
        )
    plt.legend(bbox_to_anchor=(1, 1.02), loc="upper left")

    file_name = Path(output_folder) / "vswr"
    plt.savefig(file_name, format="pdf", bbox_inches="tight")
    plt.close()


def plot_surfaces(sim: mp.Simulation, output_folder: Path | str, file_name: str = "surfaces"):
    file_name = file_name.split(".")[0]
    output_folder = resolve_output_folder(output_folder)
    f = plt.figure(dpi=300)
    sim.plot2D(ax=f.gca())
    file_name = Path(output_folder) / f"{file_name}.png"
    plt.savefig(file_name)
    plt.close()
