import os
import pickle
import pandas as pd
import numpy as np

def create_dict(folder):
    """
    Reads all the pickled objects in a folder and creates a dictionary to store all objects
    :param folder: folder to read datafrome
    :return: dictionary with all pickled objects
    """
    d = dict()
    for filename in os.listdir(folder):
        if filename.endswith('.pkl'):
            with open(folder + '//' + filename, 'rb') as a:
                d[filename.replace('.pkl', '')] = pickle.load(a)
    return d

def show_data(dict):
    """
    Function to create a dataframe from dictionary of gridworld objects
    useful to store data
    :param dict: dictionary of pickled agentdata objects
    :return: dataframe of select variables form agentdata objects
    """
    df = pd.DataFrame()
    for data in dict:
        if dict[data].lever == 'Ratio' and dict[data].lever_reward_limit == 0:
            schedule = 'FR-1'
        elif dict[data].lever == 'Ratio':
            schedule = 'FR-'+str(dict[data].lever_reward_limit)
        else:
            schedule = 'VR-'+str(dict[data].lever_reward_limit)
        df1 = pd.DataFrame({'Algorithm': dict[data].algorithm,
                            'Lever': dict[data].lever,
                            'Lever Limit': dict[data].lever_reward_limit,
                            'Schedule': schedule,
                            'Epsilon': dict[data].e,
                            'Gamma': dict[data].gamma,
                            'alpha': dict[data].alpha,
                            'lambda': dict[data].lam,
                            'Episodes': dict[data].episodes,
                            'Reward': dict[data].total_reward,
                            'Avg step': np.round(np.mean(dict[data].step_togo_list),2)
                            },
                           index=[dict[data].title])
        df = df.append(df1)
    return df

