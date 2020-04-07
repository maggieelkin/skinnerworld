from skinnerworld import *
""" Set params as a list of dictionarys to loop through and autorun Gridworld GUI"""
params = [
    {'algorithm_var': 2,
     'epsilon_var': 0.3,
     'lever_var': 1,
     'lever_limit': 3,
     'title_var': 'gt_vr3_6',
     'sleep_var': 0.001,
     'episode_var':2000},
    {'algorithm_var': 2,
     'epsilon_var': 0.3,
     'lever_var': 1,
    'lever_limit':3,
     'title_var': 'gt_vr3_7',
     'sleep_var': 0.001,
     'episode_var': 2000},
    {'algorithm_var': 2,
     'epsilon_var': 0.3,
     'lever_var': 1,
    'lever_limit':3,
     'title_var': 'gt_vr3_8',
     'sleep_var': 0.001,
     'episode_var': 2000},
    {'algorithm_var': 2,
     'epsilon_var': 0.3,
     'lever_var': 1,
    'lever_limit':3,
     'title_var': 'gt_vr3_9',
     'sleep_var': 0.001,
     'episode_var': 2000},
    {'algorithm_var': 2,
     'epsilon_var': 0.3,
     'lever_var': 1,
    'lever_limit':3,
     'title_var': 'gt_vr3_10',
     'sleep_var': 0.001,
     'episode_var': 2000}
]

# runs the gridworld in automode and passes each param dict to set variables
for param in params:
    app = tk.Tk()
    agent = GridWorld(app, autorun=True, **param)
    agent.mainloop()
