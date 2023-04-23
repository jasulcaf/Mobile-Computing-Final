import argparse
import os
from glob import glob
import pandas as pd
import math
from collections import Counter
from sklearn.ensemble import HistGradientBoostingClassifier
import joblib

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

def predict_continuous(sensor_data: str):
    """Run prediction on an sensor data sample, returning an array of labels
    for each 3-second sliding window in the file, using 1-second intervals."""
    # Read data into dataframe
    df_all_data = pd.read_csv(sensor_data, usecols=range(37)) 
    data_length_in_sec = df_all_data.loc[df_all_data.index[-1], "time"]/1000
    num_iters = max(1, math.ceil(data_length_in_sec) - 2) # num of 3sec windows
    detected_labels = []
    parsed_labels = []
    for i in range(0, num_iters):
        # new dataframe with 3 seconds of data
        df_3sec = df_all_data[df_all_data["time"].between(i*1000, (i+3)*1000)]
        # print("\n\n\n\n\=========Row length")
        # print(len(df_3sec))
        # Call our task 3 func with this new dataframe
        detected_label = predict_shallow_given_df(df_3sec)
        # Make this into something easy to read
        parsed_label = detected_label + " # t=" + str(i) + " to t="
        if i == num_iters - 1:
            parsed_label += str(round(data_length_in_sec, 1))
        else:
            parsed_label += str(i+3)
        # add in transition notation
        if i == 0:
            parsed_label += ", activity is " + detected_label
        elif detected_labels[-1] != detected_label:
            parsed_label += ", activity is transitioning to " + detected_label
        elif i >= 2 and (detected_label == detected_labels[-1] and detected_label != detected_labels[-2]):
            parsed_label += ", activity is now mostly " + detected_label
        detected_labels.append(detected_label)
        parsed_labels.append(parsed_label)
    # print("detected labels")
    # print(detected_labels)
    return parsed_labels

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
    parser = argparse.ArgumentParser()

    sample_input = parser.add_mutually_exclusive_group(required=True)
    sample_input.add_argument(
        "sample", nargs="?", help="A .csv sensor data file to run predictions on"
    )
    sample_input.add_argument(
        "--label_folder",
        type=str,
        required=False,
        help="Folder of .csv data files to run predictions on",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="Data/Lab2/Labels/Continuous/",
        help="Output filename of labels when running predictions on a directory",
    )

    args = parser.parse_args()

    if args.sample:
        if ".txt" not in args.output:
            output = args.output + ".txt"
        else:
            output = args.output
        with open(output, "w+") as out:
            out.write("\n".join(predict_continuous(args.sample)))

    elif args.label_folder:
        predict_continuous_folder(args.label_folder, args.output)