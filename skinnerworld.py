import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import random
import time
from collections.abc import Mapping
import time
import pandas as pd
print('t')

class Cell(object):
    def __init__(self, x, y, actions, reward=0, changeagent=False):
        self.x = x
        self.y = y
        self.actions = actions
        self.reward = reward
        self.changeagent = changeagent
        self.q = dict()
        for action in actions:
            self.q[action] = 0
        self.v = 0
        self.n = dict()
        for action in actions:
            self.n[action] = 0
        self.total_g = dict()
        for action in actions:
            self.total_g[action] = []
        self.episode_g = None
        self.reset_episode_g(actions)

    def reset_episode_g(self, actions):
        self.episode_g = dict()
        for action in actions:
            self.episode_g[action] = 0


class StateGrid(object):
    """
    Class to hold cell objects
    """

    def __init__(self):
        self.cell00 = Cell(60, 60, ['right', 'down'])
        self.cell01 = Cell(160, 60, ['left', 'right', 'down'])
        self.cell02 = Cell(260, 60, ['left', 'right', 'down'])
        self.cell03 = Cell(360, 60, ['right', 'left', 'down'])
        self.cell04 = Cell(460, 60, ['left', 'down'])
        self.cell10 = Cell(60, 160, ['right', 'up', 'down'])
        self.cell11 = Cell(160, 160, ['right', 'left', 'up', 'down'])
        self.cell12 = Cell(260, 160, ['right', 'left', 'up', 'down'])
        self.cell13 = Cell(360, 160, ['right', 'left', 'up', 'down'], reward=-20, changeagent=True)
        self.cell14 = Cell(460, 160, ['left', 'up', 'down'])
        self.cell20 = Cell(60, 260, ['right', 'up', 'down'])
        self.cell21 = Cell(160, 260, ['right', 'left', 'up', 'down'], reward=-20, changeagent=True)
        self.cell22 = Cell(260, 260, ['right', 'left', 'up', 'down'])
        self.cell23 = Cell(360, 260, ['right', 'left', 'up', 'down'])
        self.cell24 = Cell(460, 260, actions=['left', 'up', 'down'])
        self.cell30 = Cell(60, 360, ['right', 'up', 'down'])
        self.cell31 = Cell(160, 360, ['right', 'left', 'up', 'down'])
        self.cell32 = Cell(260, 360, ['right', 'left', 'up', 'lever'])
        self.cell33 = Cell(360, 360, ['right', 'left', 'up', 'down'])
        self.cell34 = Cell(460, 360, ['left', 'up', 'down'])
        self.cell40 = Cell(60, 460, ['right', 'up'], reward=-10, changeagent=True)
        self.cell41 = Cell(160, 460, ['left', 'up', 'lever'])
        self.cell42 = Cell(260, 460, [])
        self.cell43 = Cell(360, 460, ['right', 'up', 'lever'])
        self.cell44 = Cell(460, 460, ['left', 'up'])
        self.grid = [
            self.cell00, self.cell01, self.cell02, self.cell03, self.cell04,
            self.cell10, self.cell11, self.cell12, self.cell13, self.cell14,
            self.cell20, self.cell21, self.cell22, self.cell23, self.cell24,
            self.cell30, self.cell31, self.cell32, self.cell33, self.cell34,
            self.cell40, self.cell41, self.cell42, self.cell43, self.cell44
        ]


class Canvas(tk.Frame):
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, master)
        self.canvas = tk.Canvas(bg='white', height=600, width=770)
        rat_file = Image.open('images/rat.png')
        self.rat_image = ImageTk.PhotoImage(rat_file)
        shock_file = Image.open('images/shock.png')
        self.shock_image = ImageTk.PhotoImage(shock_file)
        lever_file = Image.open('images/lever.png')
        lever_file_left = Image.open('images/lever_left1.png')
        self.lever_image = ImageTk.PhotoImage(lever_file)
        self.lever_image2 = ImageTk.PhotoImage(lever_file_left)
        cheese_file = Image.open('images/cheese.png')
        self.cheese_image = ImageTk.PhotoImage(cheese_file)
        shock_rat_file = Image.open('images/shock_rat.png')
        self.shock_rat_image = ImageTk.PhotoImage(shock_rat_file)
        self.agent = None
        self.button = None
        # intvars for ints to show on screen
        self.reward_int = tk.IntVar()
        self.total_reward_int = tk.IntVar()
        self.episode_int = tk.IntVar()
        self.step_int = tk.IntVar()
        self.sleep_var = tk.StringVar()
        self.epsilon_var = tk.StringVar()
        self.gamma_var = tk.StringVar()
        self.alpha_var = tk.StringVar()
        # sets up grid locations and actions
        self.grid = StateGrid()
        self.create_images()
        self.setup_grid()
        self.setup_canvas_items()
        # pack canvas
        self.canvas.pack()

    def create_images(self):
        self.canvas.create_image(60, 460, image=self.shock_image)
        self.canvas.create_image(160, 260, image=self.shock_image)
        self.canvas.create_image(360, 160, image=self.shock_image)
        self.canvas.create_image(260, 460, image=self.lever_image, tag='lever')
        # self.canvas.create_image(460, 260, image=self.cheese_image)
        # self.canvas.create_rectangle(410, 210, 510, 310, fill='light green')

        self.agent = self.canvas.create_image(60, 60, image=self.rat_image, tag='agent')

    def setup_grid(self, w=510, h=510):
        # Creates all vertical lines at intevals of 100
        for i in range(10, w, 100):
            self.canvas.create_line([(i, 10), (i, h)], tag='grid_line')
        # Creates all horizontal lines at intevals of 100
        for i in range(10, h, 100):
            self.canvas.create_line([(10, i), (w, i)], tag='grid_line')
        # right side line
        self.canvas.create_line(w, 10, h, h)
        # bottom side line
        self.canvas.create_line(10, h, w, h)

    def setup_canvas_items(self):
        # reward label and int to display
        reward_label = self.canvas.create_text(50, 540)
        self.canvas.itemconfig(reward_label, text="Episode Reward: ")

        reward_box = tk.Entry(textvariable=str(self.reward_int), justify="center", width=10)
        self.canvas.create_window(130, 540, window=reward_box)
        # total reward label and int to display
        total_reward_label = self.canvas.create_text(210, 540)
        self.canvas.itemconfig(total_reward_label, text="Total Reward: ")

        total_reward_box = tk.Entry(textvariable=str(self.total_reward_int), justify="center", width=10)
        self.canvas.create_window(290, 540, window=total_reward_box)
        # episode label and int to display
        episode_label = self.canvas.create_text(50, 570)
        self.canvas.itemconfig(episode_label, text="Episode: ")
        episode_box = tk.Entry(textvariable=str(self.episode_int), justify="center", width=10)
        self.canvas.create_window(130, 570, window=episode_box)
        # step label and int to display
        step_label = self.canvas.create_text(210, 570)
        self.canvas.itemconfig(step_label, text='Step: ')
        step_box = tk.Entry(textvariable=str(self.step_int), justify="center", width=10)
        self.canvas.create_window(290, 570, window=step_box)

        sleep_label = self.canvas.create_text(550, 30)
        self.canvas.itemconfig(sleep_label, text='Speed: ')
        sleep_entry = tk.Entry(textvariable=self.sleep_var, justify="center", width=10)
        self.canvas.create_window(600, 30, window=sleep_entry)

        epsilon_label = self.canvas.create_text(549, 60)
        self.canvas.itemconfig(epsilon_label, text='Epsilon: ')
        epsilon_entry = tk.Entry(textvariable=self.epsilon_var, justify="center", width=10)
        self.canvas.create_window(600, 60, window=epsilon_entry)

        gamma_label = self.canvas.create_text(660, 30)
        self.canvas.itemconfig(gamma_label, text='Gamma: ')
        gamma_entry = tk.Entry(textvariable=self.gamma_var, justify='center', width=10)
        self.canvas.create_window(715, 30, window=gamma_entry)

        alpha_label = self.canvas.create_text(660, 60)
        self.canvas.itemconfig(alpha_label, text='Alpha: ')
        alpha_entry = tk.Entry(textvariable=self.alpha_var, justify='center',width=10)
        self.canvas.create_window(715, 60, window=alpha_entry)

        # episode_limit_label = self.canvas.create_text(550, 60)
        # self.canvas.itemconfig(episode_limit_label, text = '# Episodes: ')




class GridWorld(Canvas):

    def __init__(self, master):
        super().__init__(master)

        self.master.bind('<KeyPress>', self.human_move_agent)
        # buttons
        # step button
        label_frame = tk.LabelFrame(self.canvas, background='white', height=200, width=50)
        label = tk.Label(label_frame, text="Sample Average Q", background='white')
        label.pack(padx=0, pady=5)
        self.button = tk.Button(label_frame, text="One Episode",
                                command=lambda: self.sample_average_q_control(episodes=self.episode + 1))
        self.button.configure(width=10, activebackground="#33B5E5")
        self.button.pack(padx=5, pady=5)
        self.run_button = tk.Button(label_frame, text="Run", command=lambda: self.sample_average_q_control(episodes=15))
        self.run_button.configure(width=10, activebackground="#33B5E5")
        self.run_button.pack(padx=5, pady=5)
        self.canvas.create_window(650, 170, window=label_frame, anchor='center')

        mc_frame = tk.LabelFrame(self.canvas, background='white', height=200, width=100)
        mc_label = tk.Label(mc_frame, text="Monte Carlo", background='white')
        mc_label.pack(padx=16, pady=5)
        self.button_mc = tk.Button(mc_frame, text="One Episode",
                                   command=lambda: self.monte_carlo_control(episodes=self.episode + 1))
        self.button_mc.configure(width=10, activebackground="#33B5E5")
        self.button_mc.pack(padx=5, pady=5)
        self.run_button_mc = tk.Button(mc_frame, text="Run", command=lambda: self.monte_carlo_control(episodes=15))
        self.run_button_mc.configure(width=10, activebackground="#33B5E5")
        self.run_button_mc.pack(padx=5, pady=5)
        self.canvas.create_window(650, 290, window=mc_frame, anchor='center')

        q_frame = tk.LabelFrame(self.canvas, background='white', height=200, width=100)
        q_label = tk.Label(q_frame, text="Q Learning", background='white')
        q_label.pack(padx=20, pady=5)
        self.button_q = tk.Button(q_frame, text="One Episode",
                                  command=lambda: self.q_learning_control(episodes=self.episode + 1))
        self.button_q.configure(width=10, activebackground="#33B5E5")
        self.button_q.pack(padx=5, pady=5)
        self.run_button_q = tk.Button(q_frame, text="Run", command=lambda: self.q_learning_control(episodes=15))
        self.run_button_q.configure(width=10, activebackground="#33B5E5")
        self.run_button_q.pack(padx=5, pady=5)
        self.canvas.create_window(650, 410, window=q_frame, anchor='center')

        sarsa_frame = tk.LabelFrame(self.canvas, background='white', height=200, width=100)
        sarsa_label = tk.Label(sarsa_frame, text="SARSA", background='white')
        sarsa_label.pack(padx=32, pady=5)
        self.button_sarsa = tk.Button(sarsa_frame, text="One Episode",
                                      command=lambda: self.sarsa_control(episodes=self.episode + 1))
        self.button_sarsa.configure(width=10, activebackground="#33B5E5")
        self.button_sarsa.pack(padx=5, pady=5)
        self.run_button_sarsa = tk.Button(sarsa_frame, text="Run", command=lambda: self.sarsa_control(episodes=15))
        self.run_button_sarsa.configure(width=10, activebackground="#33B5E5")
        self.run_button_sarsa.pack(padx=5, pady=5)
        self.canvas.create_window(650, 530, window=sarsa_frame, anchor='center')

        self.q_value_button = tk.Button(text="Show Q Values", command=lambda: self.show_q_values())
        self.q_value_button.configure(width=10, activebackground="#33B5E5")
        self.canvas.create_window(390, 540, window=self.q_value_button)

        self.hide_q_value_button = tk.Button(text="Hide Q Values", command=lambda: self.hide_q_values())
        self.hide_q_value_button.configure(width=10, activebackground="#33B5E5")
        self.canvas.create_window(390, 570, window=self.hide_q_value_button)

        self.reward = 0
        self.total_reward = 0
        self.total_reward_int.set(self.total_reward)
        self.episode_reward = 0
        self.reward_int.set(self.episode_reward)
        self.episode = 1
        self.episode_int.set(self.episode)
        self.step = 1
        self.step_int.set(self.step)
        self.lever_state = []
        self.agent_state = self.grid.grid[0]
        self.previous_state = None
        self.q_table = dict()
        for cell in self.grid.grid:
            self.q_table[cell.x, cell.y] = cell.q
        self.n_table = dict()
        for cell in self.grid.grid:
            self.n_table[cell.x, cell.y] = cell.n
        self.episode_g = dict()
        for cell in self.grid.grid:
            self.episode_g[cell.x, cell.y] = cell.episode_g
        self.total_g = dict()
        for cell in self.grid.grid:
            self.total_g[cell.x, cell.y] = cell.total_g
        self.episode_policy = []
        self.reward_list = []
        self.episode_end = False

    def initialize_gridworld(self):
        self.reward = 0
        self.total_reward = 0
        self.total_reward_int.set(self.total_reward)
        self.episode_reward = 0
        self.reward_int.set(self.episode_reward)
        self.episode = 1
        self.episode_int.set(self.episode)
        self.step = 1
        self.step_int.set(self.step)
        self.lever_state = []
        self.agent_state = self.grid.grid[0]
        self.previous_state = None
        self.q_table = dict()
        for cell in self.grid.grid:
            self.q_table[cell.x, cell.y] = cell.q
        self.n_table = dict()
        for cell in self.grid.grid:
            self.n_table[cell.x, cell.y] = cell.n
        self.episode_g = dict()
        for cell in self.grid.grid:
            self.episode_g[cell.x, cell.y] = cell.episode_g
        self.total_g = dict()
        for cell in self.grid.grid:
            self.total_g[cell.x, cell.y] = cell.total_g
        self.episode_policy = []
        self.reward_list = []
        self.episode_end = False

    def show_q_values(self):
        self.canvas.delete('q')
        for cell in walk.grid.grid:
            for action in cell.actions:
                if action == 'right':
                    x_coord = cell.x + 30
                    y_coord = cell.y
                elif action == 'left':
                    x_coord = cell.x - 30
                    y_coord = cell.y
                elif action == 'up':
                    x_coord = cell.x
                    y_coord = cell.y - 30
                elif action == 'down':
                    x_coord = cell.x
                    y_coord = cell.y + 30
                else:
                    break
                self.canvas.create_text(x_coord, y_coord, text=np.round(self.q_table[(cell.x, cell.y)][action], 2),
                                        font="Verdana 8", tag='q')
        # square 160,460 lever q
        self.canvas.create_text(190, 460, text=np.round(self.q_table[(160, 460)]['lever'], 2), font="Verdana 8",
                                tag='q', fill='green')
        # square 260, 360 lever q
        self.canvas.create_text(260, 390, text=np.round(self.q_table[(260, 360)]['lever'], 2), font="Verdana 8",
                                tag='q', fill='green')
        # square 360, 460 lever q
        self.canvas.create_text(330, 460, text=np.round(self.q_table[(360, 460)]['lever'], 2), font="Verdana 8",
                                tag='q', fill='green')

    def hide_q_values(self):
        self.canvas.delete('q')

    def setup_agent(self, sleep):
        self.episode_end = False
        self.canvas.delete('agent')
        self.agent = self.canvas.create_image(60, 60, image=self.rat_image, tag='agent')
        self.master.update()
        time.sleep(sleep)
        self.agent_state = self.grid.grid[0]
        self.episode_reward = 0
        self.lever_state = []
        self.reward_list = []
        self.episode_policy = []
        for cell in self.grid.grid:
            cell.reset_episode_g(cell.actions)
            self.episode_g[cell.x, cell.y] = cell.episode_g
        self.reward = 0
        self.reward_int.set(self.reward)
        self.episode = self.episode + 1
        self.episode_int.set(self.episode)
        self.step = 1
        self.step_int.set(self.step)

    def increase_reward(self):
        self.episode_reward = self.episode_reward + self.reward
        self.total_reward = self.total_reward + self.reward
        self.reward_int.set(self.episode_reward)
        self.total_reward_int.set(self.total_reward)
        self.reward_list.append(self.reward)

    def increase_step(self, sleep, action):
        memory = {(self.previous_state.x, self.previous_state.y): action}
        self.episode_policy.append(dict(memory))
        self.step = self.step + 1
        self.step_int.set(self.step)
        self.master.update()
        time.sleep(sleep)
        previous_state = self.previous_state.x, self.previous_state.y
        N = self.n_table[previous_state][action] + 1
        self.n_table[previous_state].update({action: N})

    def lever_press_image_flip(self, sleep):
        self.canvas.delete('lever')
        self.canvas.create_image(260, 460, image=self.lever_image2, tag='lever')
        self.master.update()
        time.sleep(sleep)
        self.canvas.delete('lever')
        self.canvas.create_image(260, 460, image=self.lever_image, tag='lever')

    def lever_press(self, sleep):
        self.previous_state = self.agent_state
        self.increase_step(sleep, action='lever')
        if len(self.lever_state) == 3:
            self.lever_press_image_flip(sleep)
            self.canvas.create_rectangle(210, 410, 310, 510, fill='white')
            self.canvas.create_image(260, 460, image=self.lever_image, tag='lever')
            self.reward = 100
            self.canvas.create_image(self.agent_state.x, self.agent_state.y, image=self.cheese_image, tag='cheese')
            self.master.update()
            time.sleep(sleep)
            self.canvas.delete('cheese')
            self.increase_reward()
            self.episode_end = True
        else:
            self.lever_state.append(1)
            self.reward_list.append(0)
            if len(self.lever_state) == 3:
                self.canvas.create_rectangle(210, 410, 310, 510, fill='yellow')
            self.lever_press_image_flip(sleep)

    def change_agent_image(self, sleep):
        if self.agent_state.changeagent:
            x = self.agent_state.x
            y = self.agent_state.y
            self.canvas.delete('agent')
            self.agent = self.canvas.create_image(x, y, image=self.shock_rat_image, tag='agent')
            self.master.update()
            time.sleep(sleep)
            self.canvas.delete('agent')
            self.agent = self.canvas.create_image(x, y, image=self.rat_image, tag='agent')

    def move_action(self, action, sleep):
        self.previous_state = self.agent_state
        self.increase_step(sleep, action=action)
        if action == 'right':
            self.canvas.move(self.agent, 100, 0)
        elif action == 'left':
            self.canvas.move(self.agent, -100, 0)
        elif action == 'down':
            self.canvas.move(self.agent, 0, 100)
        else:
            # action == 'up':
            self.canvas.move(self.agent, 0, -100)
        s = self.canvas.coords(self.agent)
        for cell in self.grid.grid:
            if cell.x == s[0] and cell.y == s[1]:
                self.agent_state = cell
        self.change_agent_image(sleep)
        self.reward = self.agent_state.reward
        self.increase_reward()

    def human_move_agent(self, event, sleep=0.3):
        if event.keysym == "Escape":
            self.episode_end = True
            self.monte_carlo_prediction()
            self.setup_agent(sleep)
        elif event.keysym == "space":
            self.lever_press(sleep)
        else:
            while True:
                if event.keysym == "Up":
                    action_selected = 'up'
                elif event.keysym == "Down":
                    action_selected = 'down'
                elif event.keysym == "Left":
                    action_selected = 'left'
                elif event.keysym == "Right":
                    action_selected = 'right'
                else:
                    break
                self.move_action(action=action_selected, sleep=sleep)
                break

    def sample_average_q(self, action):
        R = self.reward
        state = self.previous_state.x, self.previous_state.y
        N = self.n_table[state][action]
        Q = self.q_table[state][action]
        Q = Q + ((1 / N) * (R - Q))
        self.q_table[state].update({action: Q})

    def q_learning_control(self, episodes):
        pass

    def sarsa_control(self, episodes):
        pass

    def monte_carlo_prediction(self):
        if len(self.gamma_var.get()) > 0:
            gamma = float(self.gamma_var.get())
        else:
            gamma = 0.5
        value_holder = set()
        for i in range(0, len(self.episode_policy)):
            for key, value in self.episode_policy[i].items():
                state = key
                action = value
                tup = (state, action)
                if tup in value_holder:
                    break
                else:
                    value_holder.add(tup)
                    G = 0
                    t = 0
                    for j in range(i, len(self.reward_list)):
                        G = G + (gamma ** t) * (self.reward_list[j])
                        t = t + 1
                    self.episode_g[state][action] = G
                    self.total_g[state][action].append(G)
                    returns = self.total_g[state][action]
                    self.q_table[state][action] = np.mean(returns)

    def monte_carlo_control(self, episodes):
        if len(self.sleep_var.get()) > 0:
            sleep = float(self.sleep_var.get())
        else:
            sleep = 0.3
        if len(self.epsilon_var.get()) > 0:
            e = float(self.epsilon_var.get())
        else:
            e = 0.01
        while self.episode < episodes:
            current_state = self.agent_state.x, self.agent_state.y
            ex = np.random.choice(['exploit', 'explore'], p=[1 - e, e])
            if ex == 'exploit':
                max_action = max(self.q_table[current_state].values())
                action_selected = np.random.choice([k for (k, v) in self.q_table[current_state].items()
                                                    if v == max_action])
            else:
                actions = self.agent_state.actions
                action_selected = np.random.choice(actions)
            if action_selected == 'lever':
                self.lever_press(sleep=sleep)
                if self.episode_end:
                    self.monte_carlo_prediction()
                    self.setup_agent(sleep)
            else:
                self.move_action(action=action_selected, sleep=sleep)

    def sample_average_q_control(self, episodes):
        if len(self.sleep_var.get()) > 0:
            sleep = float(self.sleep_var.get())
        else:
            sleep = 0.3
        while self.episode < episodes:
            current_state = self.agent_state.x, self.agent_state.y
            e = 0.01
            ex = np.random.choice(['exploit', 'explore'], p=[1 - e, e])
            if ex == 'exploit':
                max_action = max(self.q_table[current_state].values())
                action_selected = np.random.choice([k for (k, v) in self.q_table[current_state].items()
                                                    if v == max_action])
            else:
                actions = self.agent_state.actions
                action_selected = np.random.choice(actions)
            if action_selected == 'lever':
                self.lever_press(sleep=sleep)
                if self.episode_end:
                    self.sample_average_q(action_selected)
                    self.setup_agent(sleep=sleep)
            else:
                self.move_action(action=action_selected, sleep=sleep)
                self.sample_average_q(action_selected)


def show_tkinter_q_table(grid):
    q = grid.q_table
    df = pd.DataFrame(q)
    df = df.reset_index()
    # %%
    root = tk.Tk()
    i = 0
    c = 0
    for x in df.columns.to_list():
        tk.Label(root, text=x).grid(row=i, column=c)
        c = c + 1

    for i, row in df.iterrows():
        c = 0
        for cell in row:
            tk.Label(root, text=cell).grid(row=i + 1, column=c)
            c = c + 1
    root.mainloop()


app = tk.Tk()
walk = GridWorld(app)
walk.mainloop()
