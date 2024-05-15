# RacingTrajectories

## Overview
This project is a Python package for generating and analyzing racing trajectories. The package is designed to be used in the context of recorded racing simulation runs on the track Nürburgring (GP version). The package provides a set of tools for reading and visualizing telemetry data, generating racing trajectories, and analyzing the performance of the generated trajectories. The final product of this exam project is a streamlit dashboard that allows the user to interactively explore the racing trajectories of different players, seeing where they performed well and where they could have done better.


## Installation and usage 
- Clone the repository
- Create an environment for Python 3.9.13 and install the package by running `pip install -r requirements.txt.` in the root directory of the repository
- Access the directory "RacingTrajectories\streamlit"
- run the command `streamlit run app.py` in the terminal
- The dashboard will open in your default browser and you can start exploring the racing trajectories


# Structure

## Root directory

### data_fetcher.py
- The script we used on Emil's desktop to fetch the data from the racing simulator. The script is included in the repo for reference, but is not used as the requirements.txt does not contain the assetto corsa packages, and the repo does also not contain the racing simulator.

### data_loader.py
- A package to extract, load and transform the data from the racing simulator. The package contains functions for ease of use during our exploratory data analysis, and for the streamlit dashboard. The package is used in the streamlit dashboard to load the data and create the visualizations.

### Juptyer notebooks
- Each jupyter notebook contain parts of the exploratory data analysis and the development of the streamlit dashboard. The notebooks are included in the repo for reference, but are not used in the streamlit dashboard. Some of the code from the notebooks were used in the streamlit dashboard, while others are there for reference of the progress.

## Streamlit directory

### dashboard.py
- The main script for the streamlit dashboard. The script contains the layout of the dashboard, and hosts the visualizations, and the interactivity of the dashboard. This script is the main script to run when starting the streamlit dashboard. You can do this bu running the command "streamlit run dashboard.py" in the terminal.

### prepare_laps.py
- This script contains functions used to prepare the data for the streamlit dashboard. The script is used to create the visualizations in the dashboard, and is run when the dashboard is started. The script is not run manually, but is called from the dashboard.py script.

### data_visualization.py
- The script contains the main visualization craeted with plotly. The script is used in the streamlit dashboard to create the visualizations of the racing trajectories. The script is used in dashboard.py and in data_animation.py.

### data_animation.py
- A script which was intended to be integrated with the dashboard, but was excluded due to long run times. The script creates a GIF animation of the racing trajectories for all permutations of players and sections of the track. The script is not used in the streamlit dashboard, but is included in the repo as it generated the GIFs used in the dashboard.


## Remarks
- The data_animation.py file takes too long time to run in real time and is therefore not included in the streamlit dashboard. The output of several permutations were created, and in an ideal world, the animations would have been created in real time.
- We did play arround with geo pandas, moving pandas, geo points, geo lines, and folium, but never found a good integration with streamlit, and decided to use Plotly to host the visualizations. 

