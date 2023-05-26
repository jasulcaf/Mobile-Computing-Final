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
    From here we would be able to determine STD was the outputted result for both HGBC & RFC (since this is the most probable outcome). The names STDwLEGS simply refers to some variations
