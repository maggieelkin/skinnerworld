import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import random
import time
from collections.abc import Mapping
import time


class Cell(object):
    def __init__(self, x, y, actions, reward=0, absorbing=False, changeagent=False):
        self.x = x
        self.y = y
        self.actions = actions
        self.reward = reward
        self.absorbing = absorbing
        self.changeagent = changeagent
        self.q = dict()
        for action in actions:
            self.q[action] = 0
        self.v = 0
        self.n = dict()
        for action in actions:
            self.n[action] = 0
        self.r = dict()
        for action in actions:
            self.r[action] = []


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
        self.cell24 = Cell(460, 260, actions=[], reward=10, absorbing=True)
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
        self.canvas = tk.Canvas(bg='white', height=600, width=700)
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
        # self.canvas.create_text(520, 520, text=self.reward, font="Verdana 10 bold")
        sleep_label = self.canvas.create_text(550, 40)
        self.canvas.itemconfig(sleep_label, text='Speed: ')
        sleep_entry = tk.Entry(textvariable=self.sleep_var, justify="center", width=10)
        self.canvas.create_window(600, 40, window=sleep_entry)
        #episode_limit_label = self.canvas.create_text(550, 60)
        #self.canvas.itemconfig(episode_limit_label, text = '# Episodes: ')


class GridWorld(Canvas):

    def __init__(self, master):
        super().__init__(master)
        # buttons
        # step button
        self.button = tk.Button(text="Step", command=lambda: self.random_move_agent())
        self.button.configure(width=10, activebackground="#33B5E5")
        self.canvas.create_window(600, 100, window=self.button)
        # run button
        self.run_button = tk.Button(text="Run", command=lambda: self.random_move_agent(stop=100))
        self.run_button.configure(width=10, activebackground="#33B5E5")
        self.canvas.create_window(600, 140, window=self.run_button)

        self.master.bind('<KeyPress>', self.human_move_agent)
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
        self.returns_sum = dict()
        for cell in self.grid.grid:
            self.returns_sum[cell.x, cell.y] = cell.r
        self.episode_policy = []
        self.reward_list = []

    def setup_agent(self, sleep):
        self.canvas.move(self.agent, -400, -200)
        self.master.update()
        time.sleep(sleep)
        self.agent_state = self.grid.grid[0]
        self.reward = 0
        self.episode_reward = 0
        self.lever_state = []
        self.reward_int.set(self.reward)
        self.episode = self.episode + 1
        self.episode_int.set(self.episode)

    def increase_reward(self):
        self.episode_reward = self.episode_reward + self.reward
        self.total_reward = self.total_reward + self.reward
        self.reward_int.set(self.episode_reward)
        self.total_reward_int.set(self.total_reward)
        self.reward_list.append(self.reward)


    def increase_step(self, sleep, action):
        self.step = self.step + 1
        self.step_int.set(self.step)
        self.master.update()
        time.sleep(sleep)
        state = self.previous_state.x, self.previous_state.y
        N = self.n_table[state][action] + 1
        self.n_table[state].update({action: N})

    def lever_press_image_flip(self, sleep):
        self.canvas.delete('lever')
        self.canvas.create_image(260, 460, image=self.lever_image2, tag='lever')
        self.master.update()
        time.sleep(sleep)
        self.canvas.delete('lever')
        self.canvas.create_image(260, 460, image=self.lever_image, tag='lever')

    def lever_press(self, sleep):
        print(len(self.lever_state))
        self.previous_state = self.agent_state
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
            self.lever_state = []

        else:
            self.lever_state.append(1)
            self.reward_list.append(0)
            if len(self.lever_state) == 3:
                self.canvas.create_rectangle(210, 410, 310, 510, fill='yellow')
            self.lever_press_image_flip(sleep)
        self.increase_step(sleep, action='lever')

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
        self.increase_step(sleep, action=action)
        if self.agent_state.absorbing:
            self.setup_agent(sleep)

    def agent_memory(self, action):
        memory = {(self.previous_state.x, self.previous_state.y): action}
        self.episode_policy.append(dict(memory))

    def human_move_agent(self, event, sleep=0.3):
        if event.keysym == "space":
            action_selected = 'lever'
        elif event.keysym == "Up":
            action_selected = 'up'
        elif event.keysym == "Down":
            action_selected = 'down'
        elif event.keysym == "Left":
            action_selected = 'left'
        else:
            action_selected = 'right'
        if action_selected == 'lever':
            self.lever_press(sleep)
        else:
            self.move_action(action=action_selected, sleep=sleep)
        self.agent_memory(action=action_selected)
        self.sample_average_q(action_selected)

    def sample_average_q(self, action):
        R = self.reward
        state = self.previous_state.x, self.previous_state.y
        N = self.n_table[state][action]
        Q = self.q_table[state][action]
        Q = Q + ((1 / N) * (R - Q))
        self.q_table[state].update({action: Q})

    def monte_carlo_prediction(self, gamma=0.5):
        for i in range(0, len(self.episode_policy)):
            for key, value in self.episode_policy[i].items():
                state = key
                action = value
                G = 0
                t = 0
                for j in range(i, len(walk.reward_list)):
                    print(t)
                    G = G + (gamma ** t) * (walk.reward_list[j])
                    t = t + 1
                self.returns_sum[state][action].append(G)

    def random_move_agent(self, stop=1):
        if len(self.sleep_var.get()) > 0:
            sleep = float(self.sleep_var.get())
        else:
            sleep = 0.3
        t = 0
        while t < stop:
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
            else:
                self.move_action(action=action_selected, sleep=sleep)
            self.agent_memory(action=action_selected)
            self.sample_average_q(action_selected)
            t = t + 1



app = tk.Tk()
walk = GridWorld(app)
walk.mainloop()



