import os
from pathlib import Path

import configs.analysis_configs as ac
from models import AnalysisType
from rad_pattern_analysis import RadPatternAnalysis
from utilities import plot_radiation_pattern

# ====== INPUTS =======

config = ac.ANALYSIS_CONFIG_HORN_RAD_PATTERN
output_folder = "analysis1"
lab_data_file = "RadPattern_Result_Nov14th.dat"  # .dat file containing lab data to plot against. optional input, put None if ignoring
use_existing_outputs = False  # True if using results from already ran simulation in output folder, False if want to rerun
max_parallelization = None  # Maximum number of simulations that will be ran at once. Put None to use default value of number of CPU logical processes -1

# ======================

if config.analysis_type == AnalysisType.RAD_PATTERN:
    analysis = RadPatternAnalysis(
        analysis_config=config,
        output_folder=output_folder,
    )
if not use_existing_outputs:
    analysis.run_sim()
    analysis.plot_results()
else:
    if not max_parallelization:
        max_parallelization = os.cpu_count() - 1

    if config.analysis_type == AnalysisType.RAD_PATTERN:
        plot_radiation_pattern(
            sim_results=Path("results") / output_folder / "results.csv",
            output_folder=output_folder,
            lab_data_file=lab_data_file,
        )
