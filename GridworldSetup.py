import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd




class Cell(object):
    """
    Class to generate cell parameters for each cell in the gridworld
    x and y represent the middle coordinates of each cell
    actions are a list of possible actions alloted to the agent in that cell
    reward is the corresponding reward for entering the cell
    changeagent is a boolean field to represent if the agent's image will change when the agent enters the cell

    """
    def __init__(self, x, y, actions, reward=0, changeagent=False):
        self.x = x
        self.y = y
        self.actions = actions
        self.reward = reward
        self.changeagent = changeagent
        # dictionaries to hold q values, n values episode discounted return and total discounted return
        self.q = dict()
        self.n = dict()
        self.total_g = dict()
        self.episode_g = dict()
        # eligiblity trace dictionary for SARSA
        self.episode_e = dict()
        # v value for the cell
        self.v = 0
        self.reset_all_values(actions)

    def reset_all_values(self, actions):
        """
        Function to reset all values of the cell
        Used in training to restart the gridworld
        :param actions: list of actions for the cell
        :return: cell attributes are reset to 0
        """
        for action in actions:
            self.q[action] = 0
            self.n[action] = 0
            self.total_g[action] = []
            self.v = 0
        self.reset_episode_g(actions)
        self.reset_episode_e(actions)

    def reset_episode_g(self, actions):
        """
        Function to reset episode discounted return for the cell state
        used in training to reset episode G at the start of each episode
        :param actions: list of actions for the cell
        :return: cell episode_g is reset to 0
        """
        for action in actions:
            self.episode_g[action] = 0

    def reset_episode_e(self, actions):
        """
        reset the episode eligibilty trace for the cell state
        used in training to restart e values at the start of each episode
        :param actions: list of actions for the cell
        :return: episode_e is reset to 0
        """
        for action in actions:
            self.episode_e[action] = 0


class StateGrid(object):
    """
    Class to hold cell objects
    each cell is generated here by calling the Cell class
    Creates a list of cells in the grid

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
        self.cell40 = Cell(60, 460, ['right', 'up'], reward=-20, changeagent=True)
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
    """
    Class to store the Canvas items that are shown on the screen
    Inheirits the Tkinter GUI frame as master

    """
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, master)
        # create a canvas
        self.canvas = tk.Canvas(bg='white', height=600, width=790)
        # adds the files for the images used on screen
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
        # creates the agent
        self.agent = None

        # intvars for ints to show on screen
        self.reward_int = tk.IntVar()
        self.total_reward_int = tk.IntVar()
        self.episode_int = tk.IntVar()
        self.step_int = tk.IntVar()

        # string vars for user defined variables
        # default values are set if no parameters are set prior to launching the GUI
        self.sleep_var = tk.StringVar()
        self.sleep_var.set('0.3')
        self.epsilon_var = tk.StringVar()
        self.epsilon_var.set('0.1')
        self.gamma_var = tk.StringVar()
        self.gamma_var.set('0.9')
        self.alpha_var = tk.StringVar()
        self.alpha_var.set('0.5')
        self.episode_var = tk.StringVar()
        self.episode_var.set('500')
        self.lambda_var = tk.StringVar()
        self.lambda_var.set('0.5')

        self.title_var = tk.StringVar()
        self.title_var.set('SkinnerWorld')

        # variable to set lever schedule as variable or fixed
        # 1 is variable, 2 is fixed
        self.lever_var = tk.IntVar()
        self.lever_var.set(2)

        # variable to set the lever limit, no defualt is needed, if none is added, defaults to 0 (i.e. 1)
        self.lever_limit = tk.StringVar()

        # variable to set the algorithm
        # 1 is sample average q, 2 is monte carlo, 3 is Q learning, 4 is SARSA
        self.algorithm_var = tk.IntVar()
        self.algorithm_var.set(1)

        # variables to show or hide q and v values on the screen
        # 1 is show, 0 is hide
        self.show_q_var = tk.IntVar()
        self.show_q_var.set(0)

        # 1 is show, 0 is hide
        self.show_v_var = tk.IntVar()
        self.show_v_var.set(0)

        # sets up grid locations and actions
        self.grid = StateGrid()
        self.create_images()
        self.setup_grid()
        self.setup_canvas_items()
        # pack canvas
        self.canvas.pack()

    def create_images(self):
        """
        Creates images on the screen
        :return:
        """
        self.canvas.create_image(60, 460, image=self.shock_image)
        self.canvas.create_image(160, 260, image=self.shock_image)
        self.canvas.create_image(360, 160, image=self.shock_image)
        self.canvas.create_image(260, 460, image=self.lever_image, tag='lever')
        self.agent = self.canvas.create_image(60, 60, image=self.rat_image, tag='agent')

    def setup_grid(self, w=510, h=510):
        """
        Sets up the grid for the GUI
        :param w: width of grid
        :param h: height of grid
        :return:
        """
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
        """
        Sets up canvas items such as text, boxes to display variables
        :return:
        """
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

        # variables on screen
        variable_frame = tk.LabelFrame(self.canvas, text='Variables', labelanchor='n', background='white', pady=5,
                                       padx=1)
        sleep_label = tk.Label(variable_frame, text="Speed: ", background='white')
        sleep_label.grid(row=1, column=1)
        sleep_entry = tk.Entry(variable_frame, textvariable=self.sleep_var, justify="center", width=10)
        sleep_entry.grid(row=1, column=2)

        epsilon_label = tk.Label(variable_frame, text="Epsilon: ", background='white')
        epsilon_label.grid(row=2, column=1)
        epsilon_entry = tk.Entry(variable_frame, textvariable=self.epsilon_var, justify="center", width=10)
        epsilon_entry.grid(row=2, column=2)

        episode_label = tk.Label(variable_frame, text='Episodes: ', background='white')
        episode_label.grid(row=3, column=1)
        episode_entry = tk.Entry(variable_frame, textvariable=self.episode_var, justify='center', width=10)
        episode_entry.grid(row=3, column=2)

        gamma_label = tk.Label(variable_frame, text="Gamma: ", background='white')
        gamma_label.grid(row=1, column=3)
        gamma_entry = tk.Entry(variable_frame, textvariable=self.gamma_var, justify='center', width=10)
        gamma_entry.grid(row=1, column=4)

        alpha_label = tk.Label(variable_frame, text="Alpha: ", background='white')
        alpha_label.grid(row=2, column=3)
        alpha_entry = tk.Entry(variable_frame, textvariable=self.alpha_var, justify='center', width=10)
        alpha_entry.grid(row=2, column=4)

        lambda_label = tk.Label(variable_frame, text='Lambda: ', background='white')
        lambda_label.grid(row=3, column=3)
        lambda_entry = tk.Entry(variable_frame, textvariable=self.lambda_var, justify='center', width=10)
        lambda_entry.grid(row=3, column=4)

        self.canvas.create_window(650, 60, window=variable_frame, anchor='center')

        # algorithms to choose from
        algorithm_frame = tk.LabelFrame(self.canvas, text='Algorithms', labelanchor='n', background='white', pady=5)
        algorithm_frame.columnconfigure(1, weight=1)
        algorithm_frame.columnconfigure(2, weight=1)
        algorithm_frame.rowconfigure(1, weight=1)
        algorithm_frame.rowconfigure(2, weight=1)
        sample_radio = tk.Radiobutton(algorithm_frame, text='Sample Average Q', variable=self.algorithm_var,
                                      background='white', value=1)
        sample_radio.grid(row=1, column=1, sticky='W')
        mc_radio = tk.Radiobutton(algorithm_frame, text='Monte Carlo', variable=self.algorithm_var, background='white',
                                  value=2)
        mc_radio.grid(row=1, column=2, sticky='W')
        q_radio = tk.Radiobutton(algorithm_frame, text='Q Learning', variable=self.algorithm_var, background='white',
                                 value=3)
        q_radio.grid(row=2, column=1, sticky='W')
        sarsa_radio = tk.Radiobutton(algorithm_frame, text='SARSA', variable=self.algorithm_var, background='white',
                                     value=4)
        sarsa_radio.grid(row=2, column=2, sticky='W')

        self.canvas.create_window(650, 160, window=algorithm_frame, anchor='center')

        # variables for schedules of reinforcement
        lever_frame = tk.LabelFrame(self.canvas, text='Schedule of Reinforcement', labelanchor='n', background='white',
                                    pady=5, padx=5)
        variable_radio = tk.Radiobutton(lever_frame, text="Variable", variable=self.lever_var, background='white',
                                        value=1)
        variable_radio.grid(column=1, row=1, sticky='W')
        ratio_radio = tk.Radiobutton(lever_frame, text="Fixed", variable=self.lever_var, background='white', value=2)
        ratio_radio.grid(column=2, row=1, sticky='W')
        ratio_label = tk.Label(lever_frame, text="Limit: ", background='white')
        ratio_label.grid(column=1, row=2, sticky='E')
        ratio_entry = tk.Entry(lever_frame, textvariable=self.lever_limit, width=10)
        ratio_entry.grid(column=2, row=2, sticky='W')
        self.canvas.create_window(650, 260, window=lever_frame, anchor='center')


def show_tkinter_q_table(grid):
    """
    Function to show the learned q table after training, not used at all.
    :param grid: gridworld class after training
    :return:
    """
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


