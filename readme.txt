#  Inebriation Learning Tool

# CPSC 4140/6140 — Human and Computer Interaction
# Team 7:
Ben Curry
Cayden Akers
Haagen Williams
Ryan Kissel


# Project Description
The Inebriation Learning Tool is a Python-based interface that simulates how impairment from alcohol or fatigue affects reaction time, coordination, and accuracy.
It uses a Tkinter GUI and a Flask backend to collect, store, and analyze user performance data.
Users complete several interactive tasks and can view results and graphs generated from their performance.


# Extract the Project
$ cp ~/Downloads/InebriationLearningTool.zip ~/
$ unzip InebriationLearningTool.zip
$ cd InebriationLearningTool


# Set Up the Environment
Use the Makefile to automatically set up the virtual environment and install dependencies.
$ make help 
    - Lists available commands.
$ make env
    - Creates a virtual environment, installs all required Python packages listed in requirements.txt, and outputs the command to activate the environment: 
        $ source venv/bin/activate.


# Run the Interface
To start the backend and the Tkinter GUI:
$ make run
This command launches the Flask backend server in the background on port 5000 and opens the Tkinter graphical interface.


# Using the Interface
1. Enter your user-created username and click Start.
2. Select a test to perform:
   - Fitts’ Law Test
   - Target Tracking Test
   - Balance Game
   - Typing Accuracy Test


3. Choose an impairment level (None, Mild, Moderate, or Severe) and complete the tests based on the instructions provided.


4. Complete the Alcohol Knowledge Quiz.


5. Press the Analyze Results button
After completing tests, open Analyze Results from the main menu.
This feature displays average performance data and allows you to generate graphs for Fitts’ Law and quiz results.
Generated plots are saved to the data/ folder.


6. Exit the program
Gracefully close the Tkinter window using the exit button.


# Data Storage
All test and quiz data are automatically saved to the data/ directory.
Each CSV file corresponds to a specific test and impairment level or quiz result:
    - fitts_normal.csv
    - fitts_mild.csv
    - fitts_moderate.csv
    - fitts_severe.csv
    - quiz_results.csv


# Clean Up
To remove generated files (caches, csvs, pngs), run:
$ make clean