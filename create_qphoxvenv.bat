@echo off

set ENV_NAME=qphoxvenv

echo QX_OCS: Initialising "%ENV_NAME%" virtual environment.
echo QX_OCS: This script requires an installation of anaconda.

:: Locate anaconda from the base environment
cd /
if exist "Anaconda3" (
    cd Anaconda3\condabin
) else (
    cd %UserProfile%
    if exist "anaconda3" (
        cd %UserProfile%\anaconda3\condabin
    ) else (
        echo QX_OCS: Could not locate anaconda. Install and repeat process. Exiting script.
        exit
    )
)
:: Check if the conda venv exists
conda env list | findstr /C:"%ENV_NAME%" > nul
if %ERRORLEVEL%==0 (
    echo QX_OCS: Environment "%ENV_NAME%" already exists. Exiting script.
    exit 
) else (
    echo QX_OCS: Creating Environment "%ENV_NAME%".
) 

call conda update -y -n base -c defaults conda
call conda create -y -n %ENV_NAME% python=3.12
call conda activate %ENV_NAME%
call pip install numpy scipy matplotlib pandas pyserial datetime qcodes simple-pid jupyter notebook

echo QX_OCS: Successfully created "%ENV_NAME%" virtual environment. Exiting script.
