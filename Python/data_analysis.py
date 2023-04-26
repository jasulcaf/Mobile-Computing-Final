# Adding first comment to test out git things

import pandas
import os
import matplotlib.pyplot as plt

# Helper function:
# get_filepath: This function takes a string for a csv_file and returns the full 
# path that is required to load that csv further on in the file
# Input: 
#   csv_file: A string that has the name of CSV of interest
# Output: filepath to the specified csv_file
def get_filepath(csv_file: str):
    relative_path = "Data/jose/files/" + csv_file + ".csv"
    # print(relative_path)
    # files = glob.glob("../Data/Lab1/*.csv", recursive=True)
    # print(files)
    dirname = os.path.dirname(__file__)
    folder_path = dirname[:-6]
    filename = os.path.join(folder_path, relative_path)
    return filename

def summarize_sensor_trace(csv_file: str):
    # Complete summarize_sensor_trace() to compute the mean and variance of each of the
    # 36 sensor attributes in a given CSV file. This function should return a dataframe
    # or a dictionary to easily lookup the mean and variance of a given attribute.
    filename = get_filepath(csv_file)
    df = pandas.read_csv(filename, header=0, index_col=False)
    
    # In case want to make the actual new CSV and analyze data is correct (Testing Purpose)
    new_file_name = csv_file + ".csv"
    column_names = df.columns.values.tolist()[1:]
    print(column_names)
    means_variances = ["Mean", "Variance"]
    new_df = pandas.DataFrame(index=column_names, columns=means_variances)
    print(new_df)
    for i in column_names:
        curr_mean = df[i].mean()
        curr_var = df[i].var()

        # The way of how to change the Correct row position on the Accessible column
        new_df.loc[i, 'Mean'] = curr_mean
        new_df.loc[i, 'Variance'] = curr_var

    new_df.to_csv(new_file_name)
    return new_df

# ----------------------- Testing function with a CSV --------------------------
summarize_sensor_trace("LAY_01")
# ---------------------------- End of testing ----------------------------------

def visualize_sensor_trace(csv_file: str, attribute: str):
    # Complete visualize_sensor_trace() to graph a dimension of an attribute's value 
    # (e.g. controller_left_vel.x) as a function of time for a given CSV file. Remember
    # to label your axes. You may also modify this function to graph all three dimensions
    # of the given attribute (e.g. headset_rot) at once.

    filename = get_filepath(csv_file)
    curr_data = pandas.read_csv(filename, header=0, index_col=False)
    
    x_version = attribute + ".x"
    y_version = attribute + ".y"
    z_version = attribute + ".z"
    plt.plot(curr_data["time"], curr_data[x_version], color='red', label='X axis')
    plt.plot(curr_data["time"], curr_data[y_version], color='blue', label='Y axis')
    plt.plot(curr_data["time"], curr_data[z_version], color='green', label='Z axis')
    
    plt.title("Plot of " + csv_file  + "with attribute: " + attribute)
    plt.legend()
    plt.show()

# Define additional functions as needed here!

# This function takes an activity (1 of the 6) as input, and plots every single
# Attribute (for all 5 different trials) that the activity has -- It also prints
# to console the Mean and and Variance of all Aspects (X, Y, and Z)
def question_three(activity: str):
    attribute_list = []
    device_list = ["headset", "controller_left", "controller_right"]
    measure_list = ["vel", "angularVel", "pos", "rot"]
    sample_size = 5
    for name in device_list:
        for measure in measure_list:
            attribute_list.append(name + "_" + measure)
    print(attribute_list)
    for i in range(1, sample_size + 1):
        extension_name = "_0" + str(i)
        tmp_activities = []
        tmp_activities.append(activity + extension_name)
        print(tmp_activities)
        for filename in tmp_activities:
            curr_data = summarize_sensor_trace(filename)
            for attribute in attribute_list:
                curr_mean_x = curr_data.loc[attribute + ".x", 'Mean']
                curr_mean_y = curr_data.loc[attribute + ".y", 'Mean']
                curr_mean_z = curr_data.loc[attribute + ".z", 'Mean']
                curr_variance_x = curr_data.loc[attribute + ".x", 'Variance']
                curr_variance_y = curr_data.loc[attribute + ".y", 'Variance']
                curr_variance_z = curr_data.loc[attribute + ".z", 'Variance']
                
                print("_______________________________________________________")
                print("The current mean for x is: ", curr_mean_x)
                print("The current mean for y is: ", curr_mean_y)
                print("The current mean for z is: ", curr_mean_z)
                print("The current variance for x is: ", curr_variance_x)
                print("The current variance for y is: ", curr_variance_y)
                print("The current variance for z is: ", curr_variance_z)
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                
                visualize_sensor_trace(filename, attribute)
# Example Call -- I could also choose different Activities!!              
question_three("LAY")

# This functions takes as input both the Activity (1 of the 6) and a Metric (either 
# Mean or Variance) and outputs a CSV that has 5 columns (corresponding to the 5
# different trials per activity) with the correct Metric -- Useful in processing
# data faster
def print_table_question_three(activity: str, metric: str):
    tmp_activities = []
    counter = 1
    sample_size = 5
    for i in range(1, sample_size + 1):
        extension_name = "_0" + str(i)
        tmp_activities.append(activity + extension_name)
    for i in tmp_activities:
        df = summarize_sensor_trace(i)
        if counter == 1:
            filename = get_filepath(i)
            orig_df = pandas.read_csv(filename, header=0, index_col=False)

            column_names = orig_df.columns.values.tolist()[1:]
            new_df = pandas.DataFrame(index=column_names)
        num_string = str(counter)
        new_df[num_string] = df[metric]
        decimals = 4    
        new_df[num_string] = new_df[num_string].apply(lambda x: round(x, decimals))
        counter += 1
    new_df.round(4)
    
    # In case want to make the actual CSV (Testing Purposes & Analyzing Purposes!)
    new_df.to_csv("Activity - " + activity + " temporary - " + metric + ".csv")
    return new_df
# Example Call of how I called the function -- Keep in mind I called for all 6 activities!!!!
# print_table_question_three("STD", "Variance")
# print_table_question_three("STD", "Mean")

# visualize_all_attributes: Function that takes an attribute, makes 5 plots:
# Each plot contains a data collection version (which goes from 01-05), and plots 
# all the different activity for that version
# So, to be more precise ---> There are 5 different plots. Each plot contains 6 subplots
# that corresponds to the 6 different activities
def visualize_all_attributes(attribute: str):
    all_activities = ["STD", "SIT", "JOG", "CHP", "STR", "TWS"]
    for i in range(1, 6):
        extension_name = "_0" + str(i)
        tmp_activities = []
        for name in all_activities:
            tmp_activities.append(name + extension_name)
        print(tmp_activities)
    
        fig, axs = plt.subplots(3, 2)
        fig.suptitle("On Version " + str(i) + " with attribute: " + attribute)
        
        subplot_index_x = 0
        subplot_index_y = 0
        for filename in tmp_activities:
            
            curr_filename = get_filepath(filename)
            curr_data = pandas.read_csv(curr_filename, header=0, index_col=False)
        
            x_version = attribute + ".x"
            y_version = attribute + ".y"
            z_version = attribute + ".z"
            axs[subplot_index_x, subplot_index_y].plot(curr_data["time"], curr_data[x_version], color='red', label='X axis')
            axs[subplot_index_x, subplot_index_y].plot(curr_data["time"], curr_data[y_version], color='blue', label='Y axis')
            axs[subplot_index_x, subplot_index_y].plot(curr_data["time"], curr_data[z_version], color='green', label='Z axis')
            axs[subplot_index_x, subplot_index_y].set_title("Plot of " + filename[:-3], fontsize=8)
            
            subplot_index_x += 1
            if subplot_index_x > 2:
                subplot_index_x = 0
                subplot_index_y += 1
        handles, labels = axs[2,1].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper right")
        fig.set_size_inches(12.5, 8.5)
        plt.show()
# visualize_all_attributes("headset_pos") # Help Differentiate SIT
# visualize_all_attributes("controller_left_rot") # Help Differentiate TWS & JOG
# visualize_all_attributes("headset_rot") # Help Differentiate CHP & STR

# This function takes as input an Activity (one of the 6) and returns a CSV that 
# combines the 5 different trials of that Activity
def combine_CSV(activity: str):
    tmp_activities = []
    tmp_filenames = []
    for i in range(1, 6):
        extension_name = "_0" + str(i)
        tmp_activities.append(activity + extension_name)

    for i in tmp_activities:
        tmp_filenames.append(get_filepath(i))
    df1 = pandas.read_csv(tmp_filenames[0], header=0, index_col=False)
    df2 = pandas.read_csv(tmp_filenames[1], header=0, index_col=False)
    df3 = pandas.read_csv(tmp_filenames[2], header=0, index_col=False)
    df4 = pandas.read_csv(tmp_filenames[3], header=0, index_col=False)
    df5 = pandas.read_csv(tmp_filenames[4], header=0, index_col=False)
    
    # In case want to make the actual new CSV and analyze data is correct (Testing Purpose)
    new_file_name = "../Data/Lab1/Combined_" + activity + ".csv"
    
    combined_df = df1.append(df2, ignore_index=True)
    combined_df = combined_df.append(df3, ignore_index=True)
    combined_df = combined_df.append(df4, ignore_index=True)
    combined_df = combined_df.append(df5, ignore_index=True)
    combined_df.to_csv(new_file_name)
    return combined_df
# Example Call of how I got all my Combined CSVs:
# combine_CSV("JOG")
# Keep in mind I ended up calling for all the different Activites, not just 1!!!

# This function takes in a Metric (which is either Mean or Variance) and returns
# the summarized table for ALL DATA regarding ALL Activities - Used in Question #5
def summarize_combined(metric: str):
    all_activities = ["STD", "SIT", "JOG", "CHP", "STR", "TWS"]
    combined_dfs = []
    for i in all_activities:
        combined_dfs.append(combine_CSV(i))

    column_names = []
    attribute_names = ["headset_rot", "headset_pos", "controller_left_rot", "controller_right_rot"]
    for i in attribute_names:
        x_version = i + ".x"
        y_version = i + ".y"
        z_version = i + ".z"
        column_names.append(x_version)
        column_names.append(y_version)
        column_names.append(z_version)

    summarized_df = pandas.DataFrame(index=column_names, columns=all_activities)
    counter = 0
    for i in column_names:
        for curr_df in combined_dfs:
            if metric == "Mean":
                curr_data = curr_df[i].mean()
            else:
                curr_data = curr_df[i].var()
            summarized_df.loc[i, all_activities[counter]] = curr_data
            counter += 1
        counter = 0
        
    decimals = 4
    for i in all_activities:
        summarized_df[i] = summarized_df[i].apply(lambda x: round(x, decimals))
    summarized_df.round(4)
    summarized_df.to_csv("../Data/Lab1/Summarized_table - " + metric + ".csv")
    return summarized_df
# Function I called to make my graphs in the Writeup:---------------------------
# summarize_combined("Variance")
# summarize_combined("Mean")
# ------------------------------------------------------------------------------

# This function creates graphs and Tables -- Used for Question #6. It finds the 
# distance between the two controllers (Right and Left) at any point in time
def distance_between_controllers():
    all_activities = ["STD", "SIT", "JOG", "CHP", "STR", "TWS"]
    tmp_filenames = []
    for i in all_activities:
        tmp_filenames.append(get_filepath("Combined_" + i))

    df1 = pandas.read_csv(tmp_filenames[0], header=0, index_col=False)
    df2 = pandas.read_csv(tmp_filenames[1], header=0, index_col=False)
    df3 = pandas.read_csv(tmp_filenames[2], header=0, index_col=False)
    df4 = pandas.read_csv(tmp_filenames[3], header=0, index_col=False)
    df5 = pandas.read_csv(tmp_filenames[4], header=0, index_col=False)
    df6 = pandas.read_csv(tmp_filenames[5], header=0, index_col=False)
    tmp_dfs = [df1, df2, df3, df4, df5, df6]
    
    counter = 0
    new_df = pandas.DataFrame(index=["Pos.x", "Pos.y", "Pos.z"], columns=all_activities)
    for i in range(0, 6):
        curr_df = tmp_dfs[i]
        curr_column = all_activities[counter]
        curr_df["Pos.x"] = (curr_df["controller_left_pos.x"] - curr_df["controller_right_pos.x"])
        curr_df["Pos.y"] = (curr_df["controller_left_pos.y"] - curr_df["controller_right_pos.y"])
        curr_df["Pos.z"] = (curr_df["controller_left_pos.z"] - curr_df["controller_right_pos.z"])
    
    fig, axs = plt.subplots(3, 2)
    fig.suptitle("Location Difference of Controllers - Left Controller Minus Right")
    subplot_index_x = 0
    subplot_index_y = 0
    for i in range(0, 6):
        curr_data = tmp_dfs[i]
        axs[subplot_index_x, subplot_index_y].plot(curr_data["time"], curr_data["Pos.x"], color='red', label='X dif')
        axs[subplot_index_x, subplot_index_y].plot(curr_data["time"], curr_data["Pos.y"], color='blue', label='Y dif')
        axs[subplot_index_x, subplot_index_y].plot(curr_data["time"], curr_data["Pos.z"], color='green', label='Z dif')
        axs[subplot_index_x, subplot_index_y].set_title("Plot of " + all_activities[i], fontsize=8)
        subplot_index_x += 1
        if subplot_index_x > 2:
            subplot_index_x = 0
            subplot_index_y += 1
    handles, labels = axs[2,1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")
    fig.set_size_inches(12.5, 8.5)
    plt.show()
    summarized_df_mean = pandas.DataFrame(index=all_activities, columns=["Pos.x", "Pos.y", "Pos.z"])
    summarized_df_variance = pandas.DataFrame(index=all_activities, columns=["Pos.x", "Pos.y", "Pos.z"])
    for i in range(0, 6):
        curr_df = tmp_dfs[i]
        summarized_df_mean.loc[all_activities[i], "Pos.x"] = curr_df["Pos.x"].mean()
        summarized_df_mean.loc[all_activities[i], "Pos.y"] = curr_df["Pos.y"].mean()
        summarized_df_mean.loc[all_activities[i], "Pos.z"] = curr_df["Pos.z"].mean()
        
        summarized_df_variance.loc[all_activities[i], "Pos.x"] = curr_df["Pos.x"].var()
        summarized_df_variance.loc[all_activities[i], "Pos.y"] = curr_df["Pos.y"].var()
        summarized_df_variance.loc[all_activities[i], "Pos.z"] = curr_df["Pos.z"].var()
    new_file_name_mean = "../Data/Lab1/Difference_in_position - Mean.csv"
    new_file_name_var = "../Data/Lab1/Difference_in_position - Variance.csv"
    
    decimals = 4
    for i in ["Pos.x", "Pos.y", "Pos.z"]:
        summarized_df_mean[i] = summarized_df_mean[i].apply(lambda x: round(x, decimals))
        summarized_df_variance[i] = summarized_df_variance[i].apply(lambda x: round(x, decimals))
    
    summarized_df_mean.to_csv(new_file_name_mean)
    summarized_df_variance.to_csv(new_file_name_var)
# distance_between_controllers()