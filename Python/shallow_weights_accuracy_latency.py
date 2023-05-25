import os
import time
import joblib
import random
import shutil
import numpy as np
import pandas as pd
from glob import glob
from itertools import combinations
from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

def get_columns_to_read(combo):
    index_map = {'headset': list(range(1, 13)), 'left_cont': list(range(13, 25)), 'right_cont': list(range(25, 37))}
    columns_to_read = [0]  # Always include the time column?

    for item in combo:
        if item in index_map:
            columns_to_read.extend(index_map[item])

    return columns_to_read
    

def get_cross_val_score_for_file(filename, model, X, y, cv=5):
    scores = cross_val_score(model, X, y, cv=cv)
    print(f'Cross-validation scores for file {filename}: {scores}')
    print(f'Average score: {scores.mean()}')


def get_model_weights_latency_precision_accuracy():
    open("scoreboard.txt", "w").close()
    controller_combos = ['headset', 'left_cont', 'right_cont']

    clf_hgbc_legs = HistGradientBoostingClassifier()
    clf_rfc_legs = RandomForestClassifier()
    clf_hgbc_hl = HistGradientBoostingClassifier()
    clf_rfc_hl = RandomForestClassifier()

    for r in range(1, len(controller_combos) + 1):
        for combo in combinations(controller_combos, r):
            print(f"Processing combo: {combo}")

            df_legs = pd.DataFrame()
            y_legs = []

            df_handleg = pd.DataFrame() 
            y_handleg = []

            df_both = pd.DataFrame()
            y_both = []


            for filename in os.listdir('../Data/Legs_Train'):
                if filename[-4:] == '.csv':
                    columns_to_read = get_columns_to_read(combo)
                    df_cur = pd.read_csv(f'../Data/Legs_Train/{filename}', usecols=range(37)).iloc[:, columns_to_read]
                    y_cur = [filename.split('_')[0]] * len(df_cur.index)

                    df_legs = df_legs.append(df_cur)
                    y_legs.extend(y_cur)

                    df_both = df_both.append(df_cur)
                    y_both.extend(y_cur)

                    # Get cross validation scores
                    #get_cross_val_score_for_file(filename, clf_hgbc_legs, df_cur, y_cur)
                    #get_cross_val_score_for_file(filename, clf_rfc_legs, df_cur, y_cur)

            X_legs_train, X_legs_val, y_legs_train, y_legs_val = train_test_split(df_legs, y_legs, test_size=0.2)
           
            # Train model on training set

            start_time = time.time()
            clf_hgbc_legs.fit(X_legs_train, y_legs_train)
            training_latency_hgbc_legs = (time.time() - start_time)

            start_time = time.time()
            clf_rfc_legs.fit(X_legs_train, y_legs_train)
            training_latency_rfc_legs = (time.time() - start_time)
     
            # Calculate precision and inference latency
            start_time = time.time()
            y_legs_val_pred_hgbc = clf_hgbc_legs.predict(X_legs_val)
            inference_latency_hgbc_legs = (time.time() - start_time) 
            precision_hgbc_legs = precision_score(y_legs_val, y_legs_val_pred_hgbc, average='weighted')

            start_time = time.time()
            y_legs_val_pred_rfc = clf_rfc_legs.predict(X_legs_val)
            inference_latency_rfc_legs = (time.time() - start_time) 
            precision_rfc_legs = precision_score(y_legs_val, y_legs_val_pred_rfc, average='weighted')

            with open("scoreboard.txt", "a") as f:
                print(f'Training latency for HGBC on {"_".join(combo)} for legs data: {training_latency_hgbc_legs}, inference latency: {inference_latency_hgbc_legs:.5f}', file=f)
                print(f'Training latency for RFC on {"_".join(combo)} for legs data: {training_latency_rfc_legs}, inference latency: {inference_latency_rfc_legs:.5f}', file=f)
                print(f'Precision score for HGBC on {"_".join(combo)} for legs data: {precision_hgbc_legs}', file=f)
                print(f'Precision score for RFC on {"_".join(combo)} for legs data: {precision_rfc_legs}', file=f)

            # Evaluate model on validation set
            score_hgbc_legs = clf_hgbc_legs.score(X_legs_val, y_legs_val)
            score_rfc_legs = clf_rfc_legs.score(X_legs_val, y_legs_val)
            with open("scoreboard.txt", "a") as f:
                print(f'Validation set accuracy score using HGBC on {"_".join(combo)} for legs data: {score_hgbc_legs}', file=f)
                print(f'Validation set accuracy score using RFC on {"_".join(combo)} for legs data: {score_rfc_legs}', file=f)
                print(' ', file=f)
    
            # Retrain models on full training set
            clf_hgbc_legs.fit(df_legs, y_legs)
            clf_hgbc_legs.fit(df_legs, y_legs)

            # Save model and preprocessing objects to file
            joblib.dump(clf_hgbc_legs, f'model_weights_hgbc_legs_{"_".join(combo)}.joblib')
            joblib.dump(clf_rfc_legs, f'model_weights_rfc_legs_{"_".join(combo)}.joblib')

            for filename in os.listdir('../Data/Hand_Leg_Train'):
                if filename[-4:] == '.csv':
                    columns_to_read = get_columns_to_read(combo)
                    df_cur = pd.read_csv(f'../Data/Hand_Leg_Train/{filename}', usecols=range(37)).iloc[:, columns_to_read]
                    y_cur = [filename.split('_')[0]] * len(df_cur.index)

                    df_handleg = df_handleg.append(df_cur)
                    y_handleg.extend(y_cur)

                    df_both = df_both.append(df_cur)
                    y_both.extend(y_cur)

                    # Get cross validation scores
                    #get_cross_val_score_for_file(filename, clf_hgbc_hl, df_cur, y_cur)
                    #get_cross_val_score_for_file(filename, clf_rfc_hl, df_cur, y_cur)

            X_hl_train, X_hl_val, y_hl_train, y_hl_val = train_test_split(df_handleg, y_handleg, test_size=0.2)

            # Train model on training set
            
            start_time = time.time()
            clf_hgbc_hl.fit(X_hl_train, y_hl_train)
            training_latency_hgbc_hl = (time.time() - start_time)

            start_time = time.time()
            clf_rfc_hl.fit(X_hl_train, y_hl_train)
            training_latency_rfc_hl = (time.time() - start_time)

            # Calculate precision and inference latency
            start_time = time.time()
            y_hl_val_pred_hgbc = clf_hgbc_hl.predict(X_hl_val)
            inference_latency_hgbc_hl = (time.time() - start_time) 
            precision_hgbc_hl = precision_score(y_hl_val, y_hl_val_pred_hgbc, average='weighted')

            start_time = time.time()
            y_hl_val_pred_rfc = clf_rfc_hl.predict(X_hl_val)
            inference_latency_rfc_hl = (time.time() - start_time) 
            precision_rfc_hl = precision_score(y_hl_val, y_hl_val_pred_rfc, average='weighted')

            with open("scoreboard.txt", "a") as f:
                print(f'Training latency for HGBC on {"_".join(combo)} for hand_leg data: {training_latency_hgbc_hl}, inference latency: {inference_latency_hgbc_hl:.5f}', file=f)
                print(f'Training latency for RFC on {"_".join(combo)} for hand_leg data: {training_latency_rfc_hl}, inference latency: {inference_latency_rfc_hl:.5f}', file=f)
                print(f'Precision score for HGBC on {"_".join(combo)} for hand_leg data: {precision_hgbc_hl}', file=f)
                print(f'Precision score for RFC on {"_".join(combo)} for hand_leg data: {precision_rfc_hl}', file=f)

            # Evaluate model on validation set
            score_hgbc_hl = clf_hgbc_hl.score(X_hl_val, y_hl_val)
            score_rfc_hl = clf_rfc_hl.score(X_hl_val, y_hl_val)
            with open("scoreboard.txt", "a") as f:
                print(f'Validation set accuracy score using HGBC on {"_".join(combo)} for hand-leg data: {score_hgbc_hl}', file=f)
                print(f'Validation set accuracy score using RFC on {"_".join(combo)} for hand-leg data: {score_rfc_hl}', file=f)
                print(' ', file=f)

            # Retrain models on full training set
            clf_hgbc_hl.fit(df_handleg, y_handleg)
            clf_hgbc_hl.fit(df_handleg, y_handleg)

            # Save model and preprocessing objects to file
            joblib.dump(clf_hgbc_hl, f'model_weights_hgbc_hl_{"_".join(combo)}.joblib')
            joblib.dump(clf_rfc_hl, f'model_weights_rfc_hl_{"_".join(combo)}.joblib')


get_model_weights_latency_precision_accuracy()

