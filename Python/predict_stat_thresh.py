import argparse
from glob import glob
import os
import pandas
import math
import time
import sys

"""
Examine the mean and variance of each activity’s sensor data, and build a statistical 
threshold-based classifier for activity detection.

Usage:
    
    python3 Python/predict_stat_thresh.py <sensor .csv sample>

    python3 Python/predict_stat_thresh.py --label_folder <folder with sensor .csv samples>
"""
# get_filepath: This function takes a string for a csv_file and returns the full 
# path that is required to load that csv further on in the file
# Input: 
#   rel_path: A string that has the name of CSV of interest
# Output: filepath to the specified relative path
### Slight modification From Lab #1 code --> Jose version
def get_filepath(rel_path: str):
    relative_path = rel_path + ".csv"

    dirname = os.path.dirname(__file__)
    folder_path = dirname[:-6]
    filename = os.path.join(folder_path, rel_path)
    return filename

### Slight modification From Lab #1 Code --> Jose version
def summarize_sensor_trace(rel_path: str):
    # Complete summarize_sensor_trace() to compute the mean and variance of each of the
    # 36 sensor attributes in a given CSV file. This function should return a dataframe
    # or a dictionary to easily lookup the mean and variance of a given attribute.
    filename = get_filepath(rel_path)
    df = pandas.read_csv(filename, header=0, index_col=False)
    
    # In case want to make the actual new CSV and analyze data is correct (Testing Purpose)
    #new_file_name = "testing" + ".csv"
    column_names = df.columns.values.tolist()[1:]

    means_variances = ["Mean", "Variance"]
    new_df = pandas.DataFrame(index=column_names, columns=means_variances)

    for i in column_names:
        curr_mean = df[i].mean()
        curr_var = df[i].var()

        # The way of how to change the Correct row position on the Accessible column
        new_df.loc[i, 'Mean'] = round(curr_mean, 5)
        new_df.loc[i, 'Variance'] = round(curr_var, 5)

    #new_df.to_csv(new_file_name)
    return new_df

def predict_stat_thresh(sensor_data_path: str) -> str:
    """Run prediction on a sensor data sample.

    Replace the return value of this function with the output activity label
    of your stat-based threshold model. Feel free to load any files and write
    helper functions as needed.
    """
    summary = summarize_sensor_trace(sensor_data_path)
    curr_df = pandas.read_csv(get_filepath(sensor_data_path), header=0, index_col=False)
    
    curr_df["Pos.x"] = (curr_df["controller_left_pos.x"] - curr_df["controller_right_pos.x"])
    curr_df["Pos.y"] = (curr_df["controller_left_pos.y"] - curr_df["controller_right_pos.y"])
    summary.join(curr_df["Pos.x"])
    summary.join(curr_df["Pos.y"])
    # ----------------------Defining variables for ease of use------------------
    
    xdiff_controlers_pos = curr_df["Pos.x"].var()
    ydiff_controlers_pos = curr_df["Pos.y"].var()
    
    xdiff_distance_controlers = curr_df["Pos.x"].mean()
    
    yheadset_velocity = summary.loc['headset_vel.y', 'Variance']
    
    xhead_rot = summary.loc['headset_rot.x', 'Variance']
    yhead_rot = summary.loc['headset_rot.y', 'Variance']
    zhead_rot = summary.loc['headset_rot.z', 'Variance']
    
    xleft_rot = summary.loc['controller_left_rot.x', 'Variance']
    yleft_rot = summary.loc['controller_left_rot.y', 'Variance']
    zleft_rot = summary.loc['controller_left_rot.z', 'Variance']
    
    xright_rot = summary.loc['controller_right_rot.x', 'Variance']
    yright_rot = summary.loc['controller_right_rot.y', 'Variance']
    zright_rot = summary.loc['controller_right_rot.z', 'Variance']
    
    headset_left_distance = summary.loc['headset_pos.y', 'Mean'] - summary.loc['controller_left_pos.y', 'Mean']
    headset_right_distance = summary.loc['headset_pos.y', 'Mean'] - summary.loc['controller_right_pos.y', 'Mean']
    # -------------------------End of defining variables------------------------
    
    # Setting what is minimum to consider having "some" variance
    mininum_var = 50
    
    # Setting what is consider "high"
    high = 500
    very_high = high * 10
    
    # Setting what is considered upper range of distance between distance of controller
    # and headset when sitting
    distance = 0.7
    
    # Setting what is considered high controller distance
    controller_dst = 0.05
    
    # Setting what is considered high headset variance
    headset_up_down = 0.02
    
    if (xdiff_controlers_pos > controller_dst) and (ydiff_controlers_pos > controller_dst):
        # If controller distance RELATIVE to each other have meaningful variance,
        # Then we have a STR activity case
        return "STR"
        # For testing purposes::
        # return "STR" + ".... Meanwhile our result should be: " + sensor_data_path
    elif (yheadset_velocity > headset_up_down):
        # In the case that we have a "bobbing" effect being captures on headset Y axis
        # we have a JOG case
        return "JOG"
        # For testing purposes::
        # return "JOG" + ".... Meanwhile our result should be: " + sensor_data_path
    elif ((((xleft_rot > high) and (yleft_rot > high) and (zleft_rot > high)) 
           or ((xright_rot > high) and (yright_rot > high) and (zright_rot > high)))):
        # When one of the controllers experiences high rotation for all three aspects
        # We have a CHP case
        return "CHP"
        # For testing purposes::
        # return "CHP" + ".... Meanwhile our result should be: " + sensor_data_path
    elif ((((yhead_rot > very_high) and (yleft_rot > very_high)) 
        or ((yhead_rot > very_high) and (yright_rot > very_high)))
        and ((xhead_rot > mininum_var) or (zhead_rot > mininum_var))):
        # If Y has VERY high variance in headset, left controller, and right controller
        # rotation --> We have a TWS
        return "TWS"
        # For testing purposes::
        # return "TWS" + ".... Meanwhile our result should be: " + sensor_data_path
    elif abs(xdiff_distance_controlers) > 0.22 or ((abs(headset_left_distance) > distance) and (abs(headset_right_distance) > distance)):
        # xdiff_distance_controlers tells how apart horizontally the controllers were
        # Meanwhile second condition tries to capture height case
        # Since the distances are higher than the set maximum --> we have a STD case
        return "STD"
        # For testing purposes::
        # return "STD" + ".... Meanwhile our result should be: " + sensor_data_path
    else:
        # The last case here is the SIT case
        return "SIT"
        # For testing purposes::
        #return "SIT" + ".... Meanwhile our result should be: " + sensor_data_path


def predict_stat_thresh_folder(data_folder: str, output_file: str):
    """Run the model's prediction on all the sensor data in data_folder, writing labels
    in sequence to an output text file."""

    data_files = sorted(glob(f"{data_folder}/*.csv"))
    labels = map(predict_stat_thresh, data_files)

    with open(output_file, "w+") as output_file:
        output_file.write("\n".join(labels))

def average_means(lst: list):
    # Takes in a list of floats and returns the averages
    
    # Average of Float Numbers
    # using loop + formula
    curr_sum = 0
    for i in lst:
        curr_sum += i
    res = curr_sum / len(lst)
    return res

def latency_accuracy():
    super_start = time.perf_counter()
    printing_time_results = []
    all_activities = ["STD", "SIT", "JOG", "CHP", "STR", "TWS"]    
    num_to_average = 10
    
    # Loop through all activities and find average latencies and accuracies
    for activity_name in all_activities:
        # Define arrays & counting variables to be used in loop
        time_results = []
        accuracy_results = []
        counter = 0
        total_count = 0
        
        curr_activity = "Data/Lab2/Validation/" + activity_name
        for _ in range(0, num_to_average):
            # Code that we want to be timed --> How long does it take to identify activity
            start = time.perf_counter()
            data_files = sorted(glob(f"{curr_activity}*.csv"))            
            labels = map(predict_stat_thresh, data_files)
            # End of code that we want to be timed
            end = time.perf_counter() - start
    
            # Rest of the function deals with trying to have a pretty print result
            # which is DIFFERENT than time it took for function to finish
            print_start = time.perf_counter()
            time_results.append(end)
            with open("testing_latency.txt", "w+") as output_file:
                counter = 0
                output_file.write("\n".join(labels))
                output_file.seek(0)
                for item in output_file:
                    total_count += 1
                    if item.strip() == activity_name:
                        counter += 1
                accuracy_results.append(counter)
            print_end = time.perf_counter() - print_start
            printing_time_results.append(print_end)
        # Finding averages for latency time & accuracy for activity we are interested
        # As well as extra information such as how much time was spent printing
        averaged_latency = average_means(time_results)
        total_printing_latency = sum(printing_time_results)
        averaged_accuracy = sum(accuracy_results) / len(accuracy_results)
        averaged_total_count = total_count / num_to_average
        print("Currently looking at the activity: " + activity_name + ' took {:.6f}s on average for calculation'.format(averaged_latency))
        print("\twith average accuracy:" + str(averaged_accuracy) + " out of:" + str(averaged_total_count))
    super_end = time.perf_counter() - super_start
    print('In total Latency Accuracy took {:.6f}s'.format(super_end) + ' where printing took {:.6f}s'.format(total_printing_latency))

if __name__ == "__main__":
    # My extra modification ----> If we want to just look at latency times and accuracy
    # it doesn't make sense to pass into this file an arguement, so I make a case to
    # account for this:::::
    if len(sys.argv) == 1:
        # Means that we just want to look at Latency!!!
        latency_accuracy()
        quit()
    ##### ELSE ----> Proceed as normal in terms of function!!!
    
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
        default="Data/Lab2/Labels/stat.txt",
        help="Output filename of labels when running predictions on a directory",
    )

    args = parser.parse_args()

    if args.sample:
        print(predict_stat_thresh(args.sample))

    elif args.label_folder:
        predict_stat_thresh_folder(args.label_folder, args.output)