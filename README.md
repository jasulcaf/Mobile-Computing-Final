# Mobile-Computing-Final

Important notes for Data collection, we had people do different types of data collection to account for variability. This results in certain results having labels like "STDwLEGS"; however, this is just the activity STAND with extra "exageration" from the user with their legs. We figured that asking people randomly to participate in the trial, as well as the fact that VR may feel "clunky" for them, might result in our data being too rigid (especially compared to the real scenario: after waking up people are _not_ making rigit movements). 

To run any Quest related code:
Simply build like we did for Lab #1, #2, & #3.

To run Python files:
* For us to determine what Sensor combination is the best (for each Method we tested), we had to determnine the accuracy & latency for each. To run this code, simply run:```python3 shallow_weights_accuracy_latency.py``` while inside the ```Python``` folder. That will result in information being written to the file ```scoreboard.txt``` which is under the ```Python``` folder.
* To run the model for a whole _testing_ folder, we run the following code ```python3 Python/predict_shallow.py --label_folder Data/Hand_Leg_Test --output output_labels.txt``` from the main directory. From terminal outputs, you will get the following information: Name of Testing file (which is the *correct* result), results for HGBC, and results for RFC. Note, an example output might be 
    ```
    STDwLEGS
    HGBC
    Counter({'STD': 395, 'ROL': 122, 'SITtoLAY': 66})
    ====
    RFC
    Counter({'STD': 285, 'ROL': 159, 'SITtoLAY': 139})
    ====
    ```
    From here we would be able to determine STD was the outputted result for both HGBC & RFC (since this is the most probable outcome). The names STDwLEGS simply refers to some variations of STD, thus in this case, the model prediction is correct.

# Unity Scene:
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
terminal command: `pyinstaller predict_continuous.py`. We would upload these files to 
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