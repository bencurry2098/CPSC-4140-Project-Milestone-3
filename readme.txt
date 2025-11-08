# Inebriation Learning Tool

# CPSC 4140/6140 — Human and Computer Interaction
# Team 7:
Ben Curry
Cayden Akers
Haagen Williams
Ryan Kissel

# Project Description
The Inebriation Learning Tool is a Python-based educational simulator that demonstrates how impairment from alcohol or fatigue can affect coordination, accuracy, and reaction time.
It uses a Tkinter GUI and a Flask backend to collect, store, and analyze user performance data.
Users complete several interactive tasks and can review educational feedback based on their results.

# Extract the Project
$ unzip InebriationLearningTool.zip
$ cd InebriationLearningTool

# Set Up the Environment
Use the Makefile to automatically set up the virtual environment and install dependencies.
$ make help
    - Lists available commands.
$ make env
    - Creates a virtual environment, installs all required Python packages listed in requirements.txt, and outputs the command to activate the environment:
        $ source venv/bin/activate

# Run the Interface
To start the backend and the Tkinter GUI:
$ make run
This command launches the Flask backend server in the background on port 5000 and opens the Tkinter graphical interface.

# Using the Interface
1. Enter your username and click Start.
2. Select a test to perform:
   - Target Tracking Test
   - Balance Game
   - Typing Accuracy Test
3. Choose an impairment level (None, Mild, Moderate, or Severe) and complete the simulation.
4. Complete the Alcohol Knowledge Quiz.
5. Press the “Analyze Quiz Results” button to view your quiz performance summary.
6. Exit the program using the Exit button on the main menu.

# Data Storage
All data is automatically saved to the data/ directory.

# Clean Up
To remove generated files (caches, CSVs, and logs), run:
$ make clean