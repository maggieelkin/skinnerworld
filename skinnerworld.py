from GridworldSetup import *
import numpy as np
from random import randint
import time

class GridWorld(Canvas):

    def __init__(self, master):
        super().__init__(master)

        self.master.bind('<KeyPress>', self.human_move_agent)

        # buttons step button
        # TODO figure out how many episodes should be run and set that as the max episodes or set
        #  variable on gui for num episodes

        # TODO add V value hide and change radio buttons
        run_frame = tk.LabelFrame(self.canvas, text='Start GridWorld', labelanchor='n', background='white',
                                    pady=5, padx=5)
        self.button = tk.Button(run_frame, text="One Episode",
                                command=lambda: self.agent_control(episodes=self.episode + 1))
        self.button.configure(width=10, activebackground="#33B5E5")
        self.button.grid(row=1, column=1)

        self.run_button = tk.Button(run_frame, text="Run", command=lambda: self.agent_control(episodes=15))
        self.run_button.configure(width=10, activebackground="#33B5E5")
        self.run_button.grid(row=1, column=2)

        show_q_value_radio = tk.Radiobutton(run_frame, text="Show Q Values", variable=self.show_q_var, background='white',
                                        value=1, command=lambda: self.show_q_values())
        show_q_value_radio.grid(row=2, column=1)
        hide_q_value_radio = tk.Radiobutton(run_frame, text="Hide Q Values", variable=self.show_q_var, background='white',
                                        value=0, command=lambda: self.show_q_values())
        hide_q_value_radio.grid(row=2, column=2)
        self.canvas.create_window(650, 340, window=run_frame, anchor='center')

        self.reward = 0
        self.total_reward = 0
        self.episode_reward = 0
        self.episode = 1
        self.step = 1
        self.lever_state = []
        self.agent_state = self.grid.grid[0]
        self.previous_state = None
        self.q_table = dict()
        self.n_table = dict()
        self.episode_g = dict()
        self.total_g = dict()
        self.episode_policy = []
        self.reward_list = []
        self.episode_end = False
        self.lever_reward_step = None
        self.initialize_gridworld()

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
        for cell in self.grid.grid:
            self.q_table[cell.x, cell.y] = cell.q
        for cell in self.grid.grid:
            self.n_table[cell.x, cell.y] = cell.n
        for cell in self.grid.grid:
            self.episode_g[cell.x, cell.y] = cell.episode_g
        for cell in self.grid.grid:
            self.total_g[cell.x, cell.y] = cell.total_g
        self.episode_policy = []
        self.reward_list = []
        self.episode_end = False
        self.set_lever_schedule()

    def show_q_values(self):
        if self.show_q_var.get() > 0:
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
        else:
            self.canvas.delete('q')

    def set_lever_schedule(self):
        if len(self.lever_limit.get()) > 0:
            variable = int(round(float(self.lever_limit.get())))
            ratio = int(round(float(self.lever_limit.get())))
        else:
            variable = 5
            ratio = 0
        if self.lever_var.get() == 1:
            step = randint(0, variable)
            self.lever_reward_step = step
        else:
            self.lever_reward_step = ratio

    def setup_agent(self, sleep):
        self.show_q_values()
        self.episode_end = False
        self.canvas.delete('agent')
        self.agent = self.canvas.create_image(60, 60, image=self.rat_image, tag='agent')
        self.master.update()
        time.sleep(sleep)
        self.agent_state = self.grid.grid[0]
        self.episode_reward = 0
        self.lever_state = []
        self.set_lever_schedule()
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
        if len(self.lever_state) >= self.lever_reward_step - 1:
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
            if len(self.lever_state) >= self.lever_reward_step - 1:
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
        if self.step == 1:
            self.set_lever_schedule()
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

    def q_learning_prediction(self, action):
        # TODO check if this math makes sense
        gamma = float(self.gamma_var.get())
        alpha = float(self.alpha_var.get())
        R = self.reward
        S = self.previous_state.x, self.previous_state.y
        A = action
        Q = self.q_table[S][A]
        current_state = self.agent_state.x, self.agent_state.y
        # TODO:What if there is two max Q(S',a) values?
        max_a = max(self.q_table[current_state].values())
        new_q = Q + alpha * (R + (gamma * max_a) - Q)
        self.q_table[S].update({action: new_q})

    def sarsa_prediction(self, action):
        pass



    def agent_control(self, episodes):
        algorithm = self.algorithm_var.get()
        self.set_lever_schedule()
        sleep = float(self.sleep_var.get())
        e = float(self.epsilon_var.get())
        while self.episode < episodes:
            self.show_q_values()
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
                if algorithm == 1:
                    self.sample_average_q(action_selected)
                elif algorithm == 3:
                    self.q_learning_prediction(action_selected)
                elif algorithm == 4:
                    self.sarsa_prediction(action_selected)
                if self.episode_end:
                    if algorithm == 2:
                        self.monte_carlo_prediction()
                    self.setup_agent(sleep=sleep)
            else:
                self.move_action(action=action_selected, sleep=sleep)
                if algorithm == 1:
                    self.sample_average_q(action_selected)
                elif algorithm == 3:
                    self.q_learning_prediction(action_selected)
                elif algorithm == 4:
                    self.sarsa_prediction(action_selected)




def show_tkinter_q_table(grid):
    # TODO make a way to save results after running gridworld
    q = grid.q_table
    df = pd.DataFrame(q)
    df = df.reset_index()
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
