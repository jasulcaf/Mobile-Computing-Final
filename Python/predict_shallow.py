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
    
    # Load saved models

    #For both hand_leg and leg data
    #clf_hgbc = joblib.load('Python/model_weights_hgbc_both_headset_left_cont_right_cont.joblib')
    #clf_rfc = joblib.load('Python/model_weights_rfc_both_headset_left_cont_right_cont.joblib')

    #For hand_leg data
    #python3 Python/predict_shallow.py --label_folder Data/Hand_Leg_Test --output output_labels.txt
    clf_hgbc = joblib.load('Python/model_weights_hgbc_hl_headset_left_cont_right_cont.joblib')
    clf_rfc = joblib.load('Python/model_weights_rfc_hl_headset_left_cont_right_cont.joblib')

    #For legs data
    #clf_hgbc = joblib.load('Python/model_weights_hgbc_legs_headset_left_cont_right_cont.joblib')
    #clf_rfc = joblib.load('Python/model_weights_rfc_legs_headset_left_cont_right_cont.joblib')


    # Load testing data into dataframe
    test_data = pd.read_csv(sensor_data, usecols=range(37))
    
    # Generate predictions using trained model
    predictions_hgbc = clf_hgbc.predict(test_data)
    c_hgbc = Counter(predictions_hgbc)

    predictions_rfc = clf_rfc.predict(test_data)
    c_rfc = Counter(predictions_rfc)

    # extract the three digit number from the input file name
    file_name = sensor_data.split("_")[0] #[1].split(".")[0]
  

    print(file_name)
    print('HGBC')
    print(c_hgbc)
    print("====")
    print('RFC')
    print(c_rfc)
    print("====")
    print(" ")

    results = [c_hgbc.most_common()[0][0], c_rfc.most_common()[0][0]]
    results_string = ' '.join(results)
    return results_string


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