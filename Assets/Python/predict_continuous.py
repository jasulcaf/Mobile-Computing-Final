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
        dir_path = Path("/Users/matthewbutera/Desktop/4thyr/Spring/MobileComputing/Mobile-Computing-Final/Assets/Python")
        # dir_path = Path("Android/Data/com.uchicago.mobilecomputinglabs")
        parent_path = dir_path.parent.absolute()
        csv_path = str(parent_path) + "/Resources/curr_data.csv"
    except Exception as e:
        print("issues with path stuff")
        print(e)
    
    try: # JOBLIB STUFF
        # Load saved model 
        joblib_path = str(dir_path) + '/model_weights.joblib'
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
        



