from skinnerworld import *
""" Set params as a list of dictionarys to loop through and autorun Gridworld GUI"""
params = [
    {'algorithm_var': 4,
     'alpha_var': 0.5,
     'epsilon_var': 0.1,
     'lever_var': 1,
     'lever_limit': 3,
     'title_var': 'SARSA9',
     'sleep_var': 0.001},
    {'algorithm_var': 4,
     'alpha_var': 0.5,
     'epsilon_var': 0.3,
     'lever_var': 1,
     'lever_limit': 3,
     'title_var': 'SARSA10',
     'sleep_var': 0.001},
    {'algorithm_var': 4,
     'alpha_var': 0.9,
     'epsilon_var': 0.1,
     'lever_var': 1,
     'lever_limit': 3,
     'title_var': 'SARSA11',
     'sleep_var': 0.001},
    {'algorithm_var': 4,
     'alpha_var': 0.9,
     'epsilon_var': 0.3,
     'lever_var': 1,
     'lever_limit': 3,
     'title_var': 'SARSA12',
     'sleep_var': 0.001},

]

# runs the gridworld in automode and passes each param dict to set variables
for param in params:
    app = tk.Tk()
    agent = GridWorld(app, autorun=True, **param)
    agent.mainloop()