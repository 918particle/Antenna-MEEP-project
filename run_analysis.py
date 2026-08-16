import configs.analysis_configs as ac
from models import AnalysisType
from rad_pattern_analysis import RadPatternAnalysis

# ====== INPUTS ======= 
config = ac.ANALYSIS_CONFIG_1HORN_RAD_PATTERN
output_folder = "analysis1"
# ======================

if config.analysis_type == AnalysisType.RAD_PATTERN:
    analysis = RadPatternAnalysis(
        analysis_config=config,
        output_folder=output_folder,
    )
analysis.run_sim()
analysis.plot_results()