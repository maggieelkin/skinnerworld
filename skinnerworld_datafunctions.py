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


def show_data(d):
    """
    Function to create a dataframe from dictionary of gridworld objects
    useful to store data
    :param d: dictionary of pickled agentdata objects
    :return: dataframe of select variables form agentdata objects
    """
    df = pd.DataFrame()
    for data in d:
        if d[data].lever == 'Ratio' and d[data].lever_reward_limit == 0:
            schedule = 'FR-1'
        elif d[data].lever == 'Ratio':
            schedule = 'FR-' + str(d[data].lever_reward_limit)
        else:
            schedule = 'VR-' + str(d[data].lever_reward_limit)
        df1 = pd.DataFrame({'Algorithm': d[data].algorithm,
                            'Lever': d[data].lever,
                            'Lever Limit': d[data].lever_reward_limit,
                            'Schedule': schedule,
                            'Epsilon': d[data].e,
                            'Gamma': d[data].gamma,
                            'alpha': d[data].alpha,
                            'lambda': d[data].lam,
                            'Episodes': d[data].episodes,
                            'Reward': d[data].total_reward,
                            'Avg step': np.round(np.mean(d[data].step_togo_list), 2)
                            },
                           index=[d[data].title])
        df = df.append(df1)
    return df


def get_average_q_table(data):
    """
    Function to average all q_tables in a dictonairy that holds AgentData
    :param data: dictionary of AgentData Objects
    :type data: dict
    :return: Averaged Q table dictionary
    :rtype: dict
    """
    tables = []
    for key in data.keys():
        tables.append(data[key].q_table)
    n = len(tables)
    avg_q_table = {}
    for q_table in tables:
        for state in q_table.keys():
            for action, q in q_table[state].items():
                if not state in avg_q_table.keys():
                    avg_q_table[state] = {action: q}
                else:
                    if not action in avg_q_table[state].keys():
                        avg_q_table[state].update({action: q})
                    else:
                        avg_q_table[state].update({action: avg_q_table[state][action] + q})
    for state in avg_q_table.keys():
        for action, q in avg_q_table[state].items():
            avg_q = q / n
            avg_q_table[state].update({action: avg_q})
    return avg_q_table
