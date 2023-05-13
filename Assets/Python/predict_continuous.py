import argparse
import os
from glob import glob
import pandas as pd
import math
from collections import Counter
from sklearn.ensemble import HistGradientBoostingClassifier
import joblib
from pathlib import Path

"""
Use your classifier from Task 3 to perform activity detection 
on a data sample that contains more than one activity, outputting
labels on a 3-second sliding window in 1-second intervals.

Usage:
    
    python3 Python/predict_shallow.py <sensor .csv sample> \
        --output <output .txt file with labels for 3-second windows on each line>

    python3 Python/predict_shallow.py --label_folder <folder with sensor .csv samples> \
        --output <output folder>
"""

def predict_shallow_given_df(df_all_data):
    """Run prediction on an sensor data sample."""
    # Load saved model 
    clf = joblib.load('Python/model_weights.joblib')

    # # Generate predictions using trained model
    predictions = clf.predict(df_all_data)
    c = Counter(predictions)

    # extract the three digit number from the input file name
    # [deadcode] file_number = sensor_data.split("_")[1].split(".")[0]

    return c.most_common()[0][0]

def predict_continuous():
    """Run prediction on an sensor data sample.

    Replace the return value of this function with the output activity label
    of your shallow classifier for the given sample. Feel free to load any files and write
    helper functions as needed.
    """

    # # Load testing data into dataframe
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    # Load saved model 
    joblib_path = dir_path + 'model_weights.joblib'
    clf = joblib.load(joblib_path)
    parent_path = dir_path.parent.absolute()
    csv_path = parent_path + "Scripts/curr_data.csv"
    test_data = pd.read_csv(csv_path, usecols=range(37))
    
    # # Generate predictions using trained model
    predictions = clf.predict(test_data)
    c = Counter(predictions)

    # extract the three digit number from the input file name
    # file_number = sensor_data.split("_")[1].split(".")[0]

    print(c.most_common()[0][0])
    return c.most_common()[0][0]

# predict_continuous(f'Data/Lab2/ContSensingLabeled/JOG_STR.csv')


def predict_continuous_folder(data_folder: str, output_folder: str):
    """Run the model's prediction on all the sensor data in data_folder, writing labels
    in sequence to an output folder."""
    data_files = sorted(glob(f"{data_folder}/*.csv"))
    for file in data_files:
        filename = os.path.basename(file)[:-4]
        file_labels = predict_continuous(file) 

        with open(f"{output_folder}/{filename}_labels.txt", "w+") as out:
            out.write("\n".join(file_labels))


if __name__ == "__main__":
    # Parse arguments to determine whether to predict on a file or a folder
    # You should not need to modify the below starter code, but feel free to
    # add more arguments for debug functions as needed.
    predict_continuous()