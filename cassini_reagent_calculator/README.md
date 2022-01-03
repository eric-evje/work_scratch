Last updated: January 2, 2022

This folder contains python scripts and notebooks to assisst in the automation and subsequent analysis of the Cassini reagent use calculator. The output data can be used to determine effects of changing factors of ESIV, quenching, well plate fill volume, etc on the number of well plates needed per run. The relationship is stepwise and not easily predicted with an equation, so leveraging the pre-existing Google Sheets based calculator is an easy means to not duplicate the simulation of the calculator while allowing easy automation and visualization that is flexible and fast

This directory contains:
- `reagent_calculator_automater.py`: Automates changes to the Google Sheet Document: [here](https://docs.google.com/spreadsheets/d/1pVIvUz61vQ8UA74E1ngY5_-LhBnqBePjn6H54iaMd2c/edit#gid=2102398028)
- `reagent_calculator_input.csv`: The input to the reagent calculator. If different cells than those available are required to be manipulated, they must be manually added at present. Running the script `reagent_calculator_automator.py` writes to the columns to the write per row, becoming the input for the visualization script. The available values are as follows:
  - esiv (effective sample immersion volume)	
  - react_volume_overshoot (assumed overfill over ESIV)
  - img_overshoot (assumed overfill over imaging volume)
  - wash_overshoot	(assumed overfill over wash volume)
  - quencher_period (how often quencher is used. 0.5 indicates 2 quenchers per cycle. 1 indicates once per cycle. 20 indicates once per run.
  - well_plate (volume each well in a well plate can safely hold through freeze-thaw cycles
- `well_plate_config_models.ipynb`: Automates plotting of data from the output of `reagent_calculator_automater.py`
