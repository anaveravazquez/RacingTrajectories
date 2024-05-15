# RacingTrajectories

## Overview
This project is a Python package for generating and analyzing racing trajectories. The package is designed to be used in the context of recorded racing simulation runs on the track Nürburgring (GP version). The package provides a set of tools for reading and visualizing telemetry data, generating racing trajectories, and analyzing the performance of the generated trajectories. The final product of this exam project is a streamlit dashboard that allows the user to interactively explore the racing trajectories of different players, seeing where they performed well and where they could have done better.


## Installation and usage 
- Clone the repository
- Create an environment for Python 3.9.13 and install the package by running `pip install -r requirements.txt.` in the root directory of the repository
- Access the directory "RacingTrajectories\streamlit"
- run the command `streamlit run app.py` in the terminal
- The dashboard will open in your default browser and you can start exploring the racing trajectories


## Remarks
- The data_animation.py file takes too long time to run in real time and is therefore not included in the streamlit dashboard. The output of several permutations were created, and in an ideal world, the animations would have been created in real time.
- We did play arround with geo pandas, moving pandas, geo points, geo lines, and folium, but never found a good integration with streamlit, and decided to use Plotly to host the visualizations. 

