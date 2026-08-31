import os
from pathlib import Path

import configs.analysis_configs as ac
from models import AnalysisType
from rad_pattern_analysis import RadPatternAnalysis
from utilities import plot_radiation_pattern, plot_vswr
from vswr_analysis import VSWRAnalysis

# ====== INPUTS =======

config = ac.ANALYSIS_CONFIG_HORN_VSWR
output_folder = "analysis1"  # name of output folder, must change if folder already exists and you don't want results overwritten
lab_data_file = None  # .dat file in lab_data folder containing lab data to plot against. optional input, put None if ignoring
use_existing_outputs = False  # True if using results from already ran simulation in output folder, False if want to rerun
max_parallelization = None  # Maximum number of simulations that will be ran at once. Put None to use default value of number of CPU logical processes -1

# ======================


ANALYSIS_CLASSES = {
    AnalysisType.RAD_PATTERN: RadPatternAnalysis,
    AnalysisType.VSWR: VSWRAnalysis,
}
analysis: RadPatternAnalysis | VSWRAnalysis = ANALYSIS_CLASSES[config.analysis_type](
    analysis_config=config,
    output_folder=output_folder,
)
if not use_existing_outputs:
    analysis.run_sim()
    analysis.plot_results()
else:
    if not max_parallelization:
        max_parallelization = os.cpu_count() - 1

    PLOTTING_FUNCTIONS = {
        AnalysisType.RAD_PATTERN: plot_radiation_pattern,
        AnalysisType.VSWR: plot_vswr,
    }
    plot_function = PLOTTING_FUNCTIONS[config.analysis_type]
    plot_function(
        sim_results=Path("results")
        / output_folder
        / f"{config.analysis_type.value}_results.csv",
        output_folder=output_folder,
        lab_data_file=lab_data_file,
    )
