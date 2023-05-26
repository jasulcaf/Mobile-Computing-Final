import argparse
import os
from glob import glob
import pandas as pd
import math
from collections import Counter
from sklearn.ensemble import HistGradientBoostingClassifier
import sklearn
import joblib
from pathlib import Path


if __name__ == "__main__":
    try: # PATH STUFF
        # FOR PC: THIS MUST BE SET MANUALLY BECAUSE get_dir() DOESNT WORK AFTER 
        # PYINSTALLER CONVERTS TO .EXE
        dir_path = "/Users/matthewbutera/Desktop/4thyr/Spring/MobileComputing/Mobile-Computing-Final" #on PC
        # dir_path = Path("/storage/emulated/0/Android/data/com.uchicago.mobilecomputinglabs/files") # for VR 
        # parent_path = dir_path.parent.absolute()

        csv_path = str(dir_path) + "/Resources/curr_data.csv" # on PC
        # csv_path = str(dir_path) + "/csv_data.csv" # on VR
    except Exception as e:
        print("issues with path stuff")
        print(e)
    
    try: # JOBLIB STUFF
        # Load saved model 
        joblib_path = str(dir_path) + '/Python/model_weights_rfc_hl_headset_left_cont_right_cont.joblib' # on PC
        # joblib_path = str(dir_path) + '/model_weights_rfc_hl_headset_left_cont_right_cont.joblib' # on VR
    except Exception as e:
        print("issues with joblib stuff")
        print(e)

    try: # CLF STUFF
        clf = joblib.load(joblib_path)
    except Exception as e:
        print("issues with clf stuff")
        print(e)

    try: # PANDAS STUFF
        test_data = pd.read_csv(str(csv_path), usecols=range(37))
    except Exception as e:
        print("issues with pandas stuff")
        print(e)

    try: # PREDICTIONS STUFF
        # Generate predictions using trained model
        predictions = clf.predict(test_data)
    except Exception as e:
        print("issues with predictions stuff")
        print(e)

    try: # COUNTER STUFF
        c = Counter(predictions)
        # print(c.keys())
        print(c.most_common()[0][0])
    except Exception as e:
        print("issues with counter stuff")
        print(e)
        



