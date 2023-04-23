"""
Write code that takes the labeled data and outputs a training dataset in `Data/Lab2/Train/`
and a validation dataset in `Data/Lab2/Validation`. These datasets should contain CSV files
that have their corresponding activity in their filename (similar to the the `Labeled/` folder).
No file should appear in both the training and validation sets.
Be sure to include documentation with clear instructions on how to run the script and expected outputs.
"""
all_activities = ["STD", "SIT", "JOG", "CHP", "STR", "TWS"]
total_labeled_per_activity = 116
from random import *
import math 
import os
import shutil

# get_list_random --> Function that returns list of random numbers; whose length 
# is equivalent of total labeled samples * percentage
# Input: 
#   Percentage - Integer representing what percentage of data we want as validation data
def get_list_random(percentage: int):
    ret = []
    number_samples = math.floor(total_labeled_per_activity * (percentage / 100))
    for i in range(0, number_samples):
        curr_rand = randint(1, total_labeled_per_activity)
        while curr_rand in ret:
            curr_rand = randint(1, total_labeled_per_activity)
        ret.append(curr_rand)
    return ret

# delete_repeated_elements --> Function that takes in an initial list as well as
# a comparison list. Remove from initial list elements from the comparison list
# Input
#   lst: Initial List we want to filter
#   comparision: List that will contain all elements to remove
def delete_repeated_elements(lst: list, comparison: list):
    ret = []
    for i in lst:
        if i not in comparison:
            ret.append(i)
    return ret

# get_full_list --> Function that will return a list of ints from 1, 2, ... total_labeled_per_activity
def get_full_list():
    full_list = []
    for i in range(1, total_labeled_per_activity + 1):
        full_list.append(i)
    return full_list

# format_lists --> Input that takes in a list and a number; return the list in 
# STRING format as well as padding (if necessary) as indicated by input number
# Input:
#   lst: List that we wish to format
#   num: How many digits we wish the format to be. 
#       Ex: If num=3 ==> then 1 gets formatted as 001, 2 gets formatted as 002, etc.
def format_list(lst: list, num: int):
    ret = []
    for i in lst:
        tmp = "_" + str(i).zfill(num)
        ret.append(tmp)
    return ret

# get_filepath: This function takes a string for a csv_file and returns the full 
# path that is required to load that csv further on in the file
# Input: 
#   directory: Indicate in what directory to look
#   csv_file: A string that has the name of CSV of interest
# Output: filepath to the specified csv_file
### Slight modification From Lab #1 code --> Jose version
def get_filepath(directory: str, csv_file: str):
    #"Data/Lab2/Labeled"
    relative_path = directory + csv_file + ".csv"
    # print(relative_path)
    # files = glob.glob("../Data/Lab1/*.csv", recursive=True)
    # print(files)
    dirname = os.path.dirname(__file__)
    folder_path = dirname[:-6]
    filename = os.path.join(folder_path, relative_path)
    return filename

# create_validation --> Main function that accomplished Task #1 from Lab2
def create_validation():
    
    # Define what percentage of Data we want to be Validation!!
    desired_percentage = 20
    # Define how many digits the name of files are!!
    num_digits = 3
    
    # Get initial lists in INT format --> both Validation and Training set
    # The number will correlate to CSV files
    validation_set = get_list_random(desired_percentage)
    full_list = get_full_list()
    training_set = delete_repeated_elements(full_list, validation_set)
    
    # Format the lists into STRING format and any leading 0's that were missing
    validation_set = format_list(validation_set, num_digits)
    training_set = format_list(training_set, num_digits)
    
    labeled_directory_path = "Data/Lab2/Labeled/"
    train_directory_path = "Data/Lab2/Train/"
    validation_directory_path = "Data/Lab2/Validation/"
    
    for i in all_activities:
        # Looping through all activities. This loop will copy files from Labeled
        # Directory into Train and Validation Directories
        train_count = 1
        validate_count = 1
        
        for v in validation_set:
            labeled_name = i + v
            desired_name = i + "_" + str(validate_count).zfill(num_digits)
            validate_count += 1
            
            curr_filepath = get_filepath(labeled_directory_path, labeled_name)
            desired_filepath = get_filepath(validation_directory_path, desired_name)
            
            shutil.copy(curr_filepath, desired_filepath)
            
        for t in training_set:
            labeled_name = i + t
            desired_name = i + "_" + str(train_count).zfill(num_digits)
            train_count += 1
            
            curr_filepath = get_filepath(labeled_directory_path, labeled_name)
            desired_filepath = get_filepath(train_directory_path, desired_name)
            
            shutil.copy(curr_filepath, desired_filepath)

create_validation()
# test = get_list_random(20)
# print("Our random is of length: ", len(test))
# full_list = []
# for i in range(1, total_labeled_per_activity + 1):
#     full_list.append(i)
# training_data = delete_repeated_elements(full_list, test)
# print(len(training_data))
# print("Meanwhile the length of the actual full_list is: ", len(full_list))
# test.sort()
# print(test)
# print("_______")
# print(training_data)

# str(1).zfill(3)