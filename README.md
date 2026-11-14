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

### 1. Install miniconda3
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

### 2. Check miniconda3 installed correctly
1. Run `conda --version or conda list`
    - Output should look like these in this picture! <img width="796" height="888" alt="conda list" src="https://github.com/user-attachments/assets/556fbd0b-14ee-478a-bff8-ae46b803fa0a" />
        - You may have a different version installed or different packages in the conda environment
    
### 3. Install Git
_Skip if you have Git already installed_
1. For most Linux distributions, I think this line should work: `sudo apt update && sudo apt install git`, but give it a search online to check what you should run

### 4. Clone the repo
1. Open your Linux terminal
2. Navigate into the folder where you want the code to go
    - Note that the cloning process will create another folder in your current folder that then contains all the code
3. On the repo page on Github, click the big green ‘Code’ button, then copy the HTTPS URL
<img width="1280" height="632" alt="Screenshot 2026-11-06 203628" src="https://github.com/user-attachments/assets/aa265ea4-34f5-4c58-afc8-b8788c7d5ac4" />

4. Go back to your terminal
5. Run `git clone' followed by the url
    - This will probably be `git clone https://github.com/918particle/Antenna-MEEP-project.git` but technically the link could change so it is good practice to copy it from the repo
6. Now if you run `ls` you will see a new folder called the name of the repo and then if you `cd` into it then `ls` again, you will see what’s in it

### 5. Create conda environment and install dependencies
1. Run `conda env create -f environment.yml -n mp`
    - This creates a conda environment called mp and installs all the dependencies in it for the repo, including MEEP
2. Run `conda activate mp`
    - This activates the virtual environment
    - You will need to run this every time you start a new terminal that you are running MEEP python code in


### 6. (Optional) Set up VS Code
This is an optional step, but Visual Studio Code (AKA VS Code) is a commonly-used IDE with many helpful features.
#### 1. Download VS Code

- Download page: https://code.visualstudio.com/download?_exp_download=fb315fc982
- If you are on a computer with a Windows OS, download the Windows version
- If you are on a computer with a Linux OS, check what distribution you have
    -  Run `cat /etc/os-release` in your terminal to check
    -  For ‘NAME’ it will say the distribution name
    -  Search online for ‘does your_distribution_name use debian or rpm?’
       -  If it says debian, download the .deb format, if it says RPM download the .rpm format
    -  Follow the prompts in the installer then open it once it’s done installing

#### 2. This step depends on your OS
- _**For Windows Users: Download WSL Extension**_
    1. In the extensions menu (left menu bar, the four cubes), search ‘wsl’
    2. Click install for the one called ‘WSL’ by Microsoft, icon is the Linux penguin (whose name is Tux)
    3. When it’s done installing, press Ctrl+Shift+P on your keyboard
        -  This opens the command pallet
    4. Search for and select ‘WSL: Connect to WSL’
    5. Wait for the progress bar at the bottom to say it’s done
    6. Open the command pallet again and search for and select ‘WSL: Open folder in WSL’
    7. Select the folder that the GitHub repo is in
        - The one created by `git clone`

- _**For Linux Users: Open the code folder**_
    1. Click ‘Open Folder…’
    2. Select the folder that the GitHub repo is in
        - The one created by `git clone`

#### 3. Save folder as workspace
_This is optional but recommended! It saves your preferences and if you close and reopen a workspace, it saves your UI layout and reopens all your tabs you had open._
1. Click ‘File’ then ‘Save Workspace As…’
    - This will be creating a `.code-workspace` file
    - I’d save it to be in the repo folder
2. Reload VS Code
    - Open the command pallet (`Ctrl+Shift+P`) then select ‘Reload Window’

#### 4. Install extensions
1. Open the extensions menu, whcih is in the left hand menu, the symbol with the four cubes.
2. Install Python extension
    - Note that this Python extension isn’t reinstalling Python, it is installing a way for VS Code to run Python.
    - The extension is just called 'Python' and the developer is Microsoft.
    - Note that installing the Python extension automatically installs a few other extensions, do not be concerned.
3. (Optional) Install Ruff
    - Ruff is a formatter and something called a linter. Linters flags formatting errors and the formatter fixes them.
    - The extension developer is Astral Software.
    - If you open the command pallet (`Ctrl+Shift+P`) after installing and search Ruff, you will see all of the different command options.
        - Clicking the settings button next to a command opens the key-bindings settings. If you want, you can set what your key-binding/keyboard shortcuts are for the various commands.
        - I have `Ctrl+Shift+W` for `Ruff: Format Imports` and `Ctrl+Shift+D` for `Ruff: Format Document`. Those are the only two Ruff commands I use.
        - Alternatively, see step 7.5 of this section to have it auto format the document and imports when you save the file.
4. (Optional) Install autodocstring
    - This one is helpful if you will be doing any code developing. If you write a function then under the function name type three double quotes ("""), it will autogenerate a template for the docstring.
    - The developer is Nils Werner.

#### 5. Select Python interpreter
_The Python extension will need to have finished installing for these steps_
1. Open up the command pallet (`Ctrl+Shift+P`) and click on `Python: Select Interpreter`.
2. You may be prompted to select which workspace file this is for. Click the one you created (if you created one).
3. We want to select the one called `mp`, with the path most likely `~/miniconda3/envs/mp/bin/python`.
    - If you don’t see it, you will need to select ‘Enter interpreter path…’, then paste in the path.
    - If that doesn’t work, click ‘Find’, then navigate to where the python file is, which should be at that path.
    
#### 6. (Optional) Enable Autosave
- This is helpful so you don't forget to save. Remember, Git has version control so if you've committed something before changing it, you can always restore that old version.
- Enable it by going to File -> Autosave.
     
#### 7. (Optional) Set up settings.json file 
_This is a way to set up some preferences for VS Code. I think all of this can also be done from the Settings menu._
1. If you do not have a folder called '.vscode' in the repo folder, create one.
2. Inside that folder, if you do not have a file called settings.json, create one.
3. Inside settings.json, paste the following:
   ```
   {
        "python.defaultInterpreterPath": "/home/yourusername/miniconda3/envs/mp/bin/python",
        "python-envs.defaultEnvManager": "ms-python.python:conda",
        "python-envs.defaultPackageManager": "ms-python.python:conda",
        "python-envs.pythonProjects": [
            {
                "path": ".",
                "envManager": "ms-python.python:conda",
                "packageManager": "ms-python.python:conda"
            }
        ]
   }
   ```
   Make sure to change 'yourusername' in that first line to your username. Theoretically this should have it automatically activate `mp` whenever you open a new terminal. It's theoretical because sometimes it mysteriously doesn't work.
   
4. To be able to run the unit tests in VS Code, add a comma after the last square bracket and add the following after that, before the last curly bracket:
   ```
       "python.testing.unittestArgs": [
        "-v",
        "-s",
        "./tests",
        "-p",
        "test_*.py"
    ],
    "python.testing.unittestEnabled": true,
    "python.testing.pytestEnabled": false
   ```
   You can see the VS Code unit test menu by clicking the little flask icon on the left side bar.

5. If you have Ruff installed and want it to autoformat when you save a file, add a comma after the last square bracket and add the following after that, before the last curly bracket:
   ```
       "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports.ruff": "explicit"
        }
    }
   ```
   The "explicit" part means this only happens when you manually save the file, like with Ctrl+S, not when it autosaves, if you have that enabled.
   

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
