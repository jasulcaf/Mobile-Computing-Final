import argparse
from glob import glob
from collections import Counter
from sklearn.ensemble import HistGradientBoostingClassifier
import joblib
import pandas as pd

"""
Create a non-deep learning classifier (e.g. multiclass SVM, decision tree, random forest)
to perform activity detection that improves upon your prior algorithm.

Usage:
    
    python3 Python/predict_shallow.py <sensor .csv sample>

    python3 Python/predict_shallow.py --label_folder <folder with sensor .csv samples>
"""

def predict_shallow(sensor_data: str) -> str:
    """Run prediction on an sensor data sample.

    Replace the return value of this function with the output activity label
    of your shallow classifier for the given sample. Feel free to load any files and write
    helper functions as needed.
    """
    # Load saved model 
    clf = joblib.load('Python/model_weights.joblib')

    # # Load testing data into dataframe
    test_data = pd.read_csv(sensor_data, usecols=range(37))
    
    # # Generate predictions using trained model
    predictions = clf.predict(test_data)
    c = Counter(predictions)

    # extract the three digit number from the input file name
    file_number = sensor_data.split("_")[1].split(".")[0]

    return c.most_common()[0][0]

# predict_shallow('Data/Lab2/Test/test_001.csv')

def predict_shallow_folder(data_folder: str, output: str):
    """Run the model's prediction on all the sensor data in data_folder, writing labels
    in sequence to an output text file."""

    data_files = sorted(glob(f"{data_folder}/*.csv"))
    labels = map(predict_shallow, data_files)

    with open(output, "w+") as output_file:
        output_file.write("\n".join(labels))


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
        default="Data/Lab2/Labels/shallow.txt",
        help="Output filename of labels when running predictions on a directory",
    )

    args = parser.parse_args()

    if args.sample:
        print(predict_shallow(args.sample))

    elif args.label_folder:
        predict_shallow_folder(args.label_folder, args.output)