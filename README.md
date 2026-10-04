## Configs
The parameters for a run all live in "config" files. You can view these in the "configs" folder.

The purpose of these configs is so that it is straightforward to have multiple combinations of parameters saved. 

For instance, lets say I frequently run a 3D 5-horn radiation pattern analysis. I also frequently run a 2D 1-horn radiation pattern analysis. Instead of needing to remember all of the different parameters for both analyses and having to retype them in every time I'm changing back and forth, I create two configs, ex: ANALYSIS_CONFIG_5HORN_3D and ANALYSIS_CONFIG_1HORN_2D. 

Now when I want to run one of those, I can just type in the name of the config and it contains all of the associated parameters. Another bonus is then when you commit the configs to the repository, other people can easily see and use the same parameters you ran.

This is especially helpful because there are many sets of parameters that may be reused across different analyses. For instance, the properties of a GDSII file - such as which layer is which part of the antenna - are likely going to remain unchanged across analyses. Therefore, there is a config for a GDSII file, which then can be reused across analyses.

Now for what all the configs are.
- First there is the GDSIIFileConfigHorn (specifically horn because we will add other antenna types later).
  - These configs live in ~/configs/gdsii_configs.py.
- Next is the AntennaConfig, 
  - These configs live in ~/configs/antenna_configs.py.
  - The property 'gdsii_file_config' should be set equal to a GDSIIFileConfigHorn (or another non-horn type of GDSII file config once we make those)
- Now is the config for the specific analysis type
  - For radiation pattern analysis, there is RadPatternAnalysisConfig.
    - These configs live in ~/configs/rad_pattern_analysis.py. 
  - For VSWR analysis, there is VSWRAnalysisConfig.
    - These configs live in ~/configs/vswr_analysis.py.
- Lastly, there's the AnalysisConfig
  - These configs live in ~/configs/analysis_configs.py.
  - These are the highest level configs. They are the ones you actually call to run in run_analysis.py.
  - These configs have a property called 'analysis_type_config' which should be set equal to a RadPatternAnalysisConfig or a VSWRAnalysisConfig.

For all configs, add on another if you need something different, or change an existing one if you know the current version is no longer needed (i.e. you are tuning the parameters).

## How to run it
To run anything, you run the file run_analysis.py.

There is an area of that file that is specifically labeled "INPUTS". That is the only area you should need to touch.

### Instructions
- Set 'config' equal to the AnalysisConfig you want to run.
- Set 'output_folder' equal to the name of the folder you'd like your results in.
  - The folder will be a subfolder in ~/results/
  - Note that if you use a folder name that already exists in ~/results/, if you are running the same type of analysis as the outputs already in that folder (i.e. another radiation pattern analysis) then the results will be overwritten in that folder.
  - Note that in the ~/results/ folder there is a .gitignore file. This makes it so git ignores the contents of the folder, so there isn't a whole bunch of everyone's scratch work on the repo. You will notice this when you run 'git status' and see that nothing inside the results folder shows up.
- Set 'lab_data_file' to either None or the name of the .dat file in the ~/lab_data/ folder containing the lab data results you want to plot your simulation results against.
  - Put None if you only want to plot the simulation results.
- Set 'use_existing_outputs' to either True or False.
  - The purpose of this is for if you've already ran a simulation and just want to replot it, for instance against some different lab data. When you run an analysis, it saves the output as a csv file in the output folder.
  - True means use the output file that already lives in the output_folder specified.
  - False means run the simulation. You *must* put False if you have not previously ran the analysis/there is not a *_results.csv file for your simulation type in the output_folder you specified.
- Set 'max_parallelization' to None or an integer.
  - This is the maximum number of simulations that will be ran at once.
  - Set it to None if you want to use the default value which is one less than the number of CPU logical processes on the computer you running on (so your computer if running it locally or the computer you are SSHd into).
