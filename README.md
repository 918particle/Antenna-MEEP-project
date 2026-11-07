# Initial Set Up
## On Windows
### 1. Install WSL
WSL documentation: https://learn.microsoft.com/en-us/windows/wsl/setup/environment
1. Open Powershell in the Start Menu
2. Click 'Run as Administrator'
    - If it says ‘Do you allow this application to make changes to your device’ -> Click ‘Yes’
3. Run `wsl --install -d Ubuntu`
    - This will download the Ubuntu distribution of Linux (the -d is short for --distribution)
       - The distributions are pretty similar but Ubuntu is the default
    - You will be prompted to create a username and password
       - When you type in your password, nothing will appear but it is registering it! It’s called ‘blind typing’
       - Make your password memorable or write it down. You can always reset it though
       - You’ll need your password when installing packages
### 2. Confirm WSL install worked
1. Restart your computer
2. Open the Powershell terminal again
3. Run `wsl -l -v`
    - This is shorthand for `wsl --list --verbose`
    - This means we want a list of what’s installed in WSL and we want details about each item
    - It should look like what’s below, though the version potentially may be different
<img width="874" height="304" alt="wsl list" src="https://github.com/user-attachments/assets/5e41647f-aae9-4d26-8de6-6563318eb739" />


### 3. Open Ubuntu
- You can now open Ubuntu by just searching for it in your Start menu!
- What opens is a regular looking terminal, like what you’d see if you opened Linux on a computer with a Linux OS
Continue onto the next section

## On Linux / On Windows continued
If you are on Linux, start here by opening a regular terminal. If you are on Windows, start here from the last step where you opened Ubuntu.

### 1. / 4. Install miniconda3
You can skip this step if you already have miniconda3 installed in your Linux environment.
Documentation: https://www.anaconda.com/docs/getting-started/miniconda/install/linux-install#wget
1. Run `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
    - This downloads the installer for miniconda3
2. Run `bash Miniconda3-latest-Linux-x86_64.sh`
    - This actually installs miniconda3 from the installer
    - It will prompt you to accept the license terms
        - You may need to scroll through the terms to get to the accept/decline prompt
        - You will have to say ‘yes’ for it to install
    - It will prompt you for an install location
        - It will suggest something like `/home/yourusername/miniconda3`
        - That’s correct, accept that
    - At the end it will say something like ‘Do you wish the installer to initialize Miniconda3?’
        - Say yes, it means that your terminal will automatically start conda when you open it
3. Run `source ~/.bashrc`
    - The line basically restarts the shell
    - Alternatively, you can just close the terminal and reopen it

### 2. / 5. Check miniconda3 installed correctly
1. Run `conda --version or conda list`
    - Output should look like these in this picture! <img width="796" height="888" alt="conda list" src="https://github.com/user-attachments/assets/556fbd0b-14ee-478a-bff8-ae46b803fa0a" />
        - You may have a different version installed or different packages in the conda environment

### 3. / 6. Install MEEP
1. Run `conda create -n mp -c conda-forge pymeep`
    - This creates a new virtual environment then installs MEEP in it
    - `create` creates a new virtual environment
    - `-n mp` means we are naming the virtual environment ‘mp' (you can name it something else)
    - `-c conda-forge` is saying we will be downloading the package from a channel called conda-forge (which is a package manager for conda)
    - `pymeep` is the name of Meep’s python package
2. Run `conda install conda-forge::h5utils`
    - This installs the h5utils package from conda-forge, for some MEEP stuff we use h5topng from it
3. Run `conda activate mp`
    - This activates the virtual environment
    - You will need to run this every time you start a new terminal that you are running MEEP python code in

### 4. / 7. Install Git
1. Run `conda install conda-forge::git`

### 5. / 8. Clone the repo
1. Open your Linux terminal
2. Navigate into the folder where you want the code to go
    - Note that the cloning process will create another folder in your current folder that then contains all the code
3. On the repo page on Github, click the big green ‘Code’ button, then copy the HTTPS URL
<img width="1280" height="632" alt="Screenshot 2026-11-06 203628" src="https://github.com/user-attachments/assets/aa265ea4-34f5-4c58-afc8-b8788c7d5ac4" />

4. Go back to your terminal
5. Run `git clone' followed by the url
    - This will probably be `git clone https://github.com/918particle/Antenna-MEEP-project.git` but technically the link could change so it is good practice to copy it from the repo
6. Now if you run `ls` you will see a new folder called the name of the repo and then if you `cd` into it then `ls` again, you will see what’s in it

### 6. / 9. Set up VS Code
This is an optional step, but Visual Studio Code (AKA VS Code) is a commonly-used IDE with many helpful features.
1. Download VS Code
    - Download page: https://code.visualstudio.com/download?_exp_download=fb315fc982
    - If you are on a computer with a Windows OS, download the Windows version
    - If you are on a computer with a Linux OS, check what distribution you have
        -  Run `cat /etc/os-release` in your terminal to check
        -  For ‘NAME’ it will say the distribution name
        -  Search online for ‘does your_distribution_name use debian or rpm?’
            -  If it says debian, download the .deb format, if it says RPM download the .rpm format
    -  Follow the prompts in the installer then open it once it’s done installing

2. For Windows Users: Download WSL Extension
<br>  _Only for Windows users! Skip this step if you are on a Linux machine._
    1. In the extensions menu (left menu bar, the four cubes), search ‘wsl’
    2. Click install for the one called ‘WSL’ by Microsoft, icon is the Linux penguin (whose name is Tux)
    3. When it’s done installing, press Ctrl+Shift+P on your keyboard
        -  This opens the command pallet
    4. Search for and select ‘WSL: Connect to WSL’
    5. Wait for the progress bar at the bottom to say it’s done
    6. Open the command pallet again and search for and select ‘WSL: Open folder in WSL’
    7. Select the folder that the GitHub repo is in
       - The one created by `git clone`

2. For Linux Users: Open the code folder
<br> _Only for Linux users! Skip this step if you are on a Windows machine._
    1. Click ‘Open Folder…’
    2. Select the folder that the GitHub repo is in
       - The one created by `git clone`

# How to Run the Code! 🏃
To run anything, you run the file run_analysis.py.

There is an area of that file that is specifically labeled "INPUTS". That is the only area you should need to touch.
<img width="607" height="405" alt="Inputs" src="https://github.com/user-attachments/assets/7bdcbaae-e049-443b-83bb-bba75ebce635" />



## Instructions
- Set 'config' equal to the AnalysisConfig you want to run. (See section below on configs)
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

See the Wiki (up on the top menu bar) for more info on how this all works
