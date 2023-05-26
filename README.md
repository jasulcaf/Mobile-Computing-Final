# Mobile Computing Labs

This repository contains Unity template code for the Power Savvy Trio

## Current Configuration
The app is currenlty configured to run in Unity.In order for proper functionality
to run on the headset, we recommend using Oculus Link through Unity.
However, if this is not an option, then in the files `ActivityDetector.cs` and 
`predict_continuous.py`, uncomment code that says "# FOR VR" and comment code that
says "# FOR PC." These lines are only found when regarding obtaining file location
## Issues with Quest
The Quest does not allow C# scripts to run other executables; when this is tried,
the error message is "Access Denied." This is why, ideally, this app should be run
on Oculus Link so that the PC can perform all computation necessary.
## Current Workaround (PC)
As mentioned previously, the configuration is for the PC in order to prove proof-of-concept.
However, the app is based on a .csv created dynamically during 
the scene execution, and this .csv file is empty when run on the PC. Therefore,
in order to simulate the desired behavior on the PC, choose a .csv file from
`Data/` then copy it over to `Resources/` and rename it `curr_data.csv`. Then,
the scene, when run in Play Mode in Unity, will reference this file for detection.
Note the following keyboard triggers:
- `X` to sleep
- `C` to play alarm once instantly
- `Z` to disable alarm
- `V` to play alarm instantly then play it again 15 seconds later
### Further Setup (PC and VR)
In order to run the Python script, we convert it to a .exe file. To do this,
go to the Moible-Computing-Final/Python/ Directory, and run the following
terminal command: `pyinstaller predict_continuous`. We would upload these files to 
Github but cannot because of filesize limit.
## Current Workaround (VR)
Because the model could not be run on the VR headset, the workaround for 
proof-of-concept involves a simulated experience. Specifically:
- `A` to sleep
- `Front Right Trigger` to play alarm once instantly
- `Front Left Trigger` to disable alarm
- `Y` to play alarm instantly then play it again 15 seconds later
Using `Front Right Trigger` will simulate the scenario in which the user gets up
after the alarm
Using `Y` will simulate the scenario in which the user stays sleeping after
the alarm.