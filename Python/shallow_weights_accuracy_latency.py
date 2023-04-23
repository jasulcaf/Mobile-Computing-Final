import os
import time
import joblib
import numpy as np
import pandas as pd
from glob import glob
from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
#from sklearn.ensemble import RandomForestClassifier

def get_model_weights():
    df = pd.DataFrame()
    y = []
    for filename in os.listdir('../Data/Lab2/Train'):
        if filename[-4:] == '.csv':
            df_cur = pd.read_csv(f'../Data/Lab2/Train/{filename}', usecols=range(37)) 
            
            df = df.append(df_cur)
            y_cur = [filename[0:3]] * len(df_cur.index)
            y.extend(y_cur)
    X_train, X_val, y_train, y_val = train_test_split(df, y, test_size=0.2)

    # Train model on training set
    clf_hgbc = HistGradientBoostingClassifier()
    clf_hgbc.fit(X_train, y_train)
    #clf_rfc = RandomForestClassifier()
    #clf_rfc.fit(X_train, y_train)

    # Evaluate model on validation set
    score_hgbc = clf_hgbc.score(X_val, y_val)
    #score_rfc = clf_rfc.score(X_val, y_val)
    print(f'Validation set score for all activities using HGBC: {score_hgbc}')
    #print(f'Validation set score for all activities using RFC: {score_rfc}')

    # Retrain model on full training set
    clf_hgbc.fit(df, y)
    #clf_rfc.fit(df, y)
 
    # Save model and preprocessing objects to file
    joblib.dump(clf_hgbc, 'model_weights.joblib')

# df = pd.DataFrame()
# df_cur = pd.read_csv(f'../Data/Lab2/Train/CHP_001.csv', usecols=range(37))
# df = df.append(df_cur)
# print(df)

# Get accuracy and latency
def accuracy_latency():
    activity_precisions = []
    activity_latencies = []
    activities = ["STD", "SIT", "JOG", "CHP", "STR", "TWS"] 
    for activity in activities:
        df = pd.DataFrame()
        y = []
        for file in glob(f'../Data/Lab2/Validation/{activity}*'):
            df_cur = pd.read_csv(file) #.iloc[:, :-1]
            df = df.append(df_cur)
            y_cur = [activity] * len(df_cur.index)
            y.extend(y_cur)
        X_train, X_val, y_train, y_val = train_test_split(df, y, test_size=0.2)

        # Classifier type
        clf = HistGradientBoostingClassifier()

        # Train model on training set
        # Start timer for training latency
        train_start = time.perf_counter()
        clf.fit(X_train, y_train)
        train_latency = time.perf_counter() - train_start

        # Evaluate model on validation set
        # Start timer for inference latency
        infer_start = time.perf_counter()
        y_pred = clf.predict(X_val)
        precision = precision_score(y_val, y_pred, average='weighted')
        infer_latency = time.perf_counter() - infer_start
      
        activity_precisions.append(precision)
        activity_latencies.append(train_latency + infer_latency)
        
    # Print precision and latency for each activity
    for i in range(len(activities)):
        print(f'Validation set precision score for {activities[i]}: {activity_precisions[i]:.4f}, latency: {activity_latencies[i]:.6f}s')

    # Calculate and print average precision and latency for the entire validation set
    avg_precision = np.mean(activity_precisions)
    avg_latency = np.mean(activity_latencies)
    print(f'\nAverage validation set precision score: {avg_precision:.4f}, average latency: {avg_latency:.6f}s')


#get_model_weights()

#Uncomment below line to get accuracy and latency values
accuracy_latency()

