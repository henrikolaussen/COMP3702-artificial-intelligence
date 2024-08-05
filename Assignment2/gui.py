import tkinter as tk
import time

from game_env import GameEnv

"""
Graphical Visualiser for Dragon Game. You may modify this file if desired.

COMP3702 Assignment 1 "Dragon Game" Support Code

Last updated by njc 15/08/22
"""


class Viewer:

    TILE_W = 32
    TILE_H = 32
    TILE_W_SMALL = 16
    TILE_H_SMALL = 16

    UPDATE_DELAY = 0.5
    TWEEN_STEPS = 16
    TWEEN_DELAY = 0.005

    def __init__(self, game_env):
        self.game_env = game_env
        init_state = game_env.get_init_state()
        self.last_state = init_state

        # choose small or large mode
        self.window = tk.Tk()
        screen_width, screen_height = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        if (screen_width < self.game_env.n_cols * self.TILE_W) or (screen_height < self.game_env.n_rows * self.TILE_H):
            small_mode = True
            self.tile_w = self.TILE_W_SMALL
            self.tile_h = self.TILE_H_SMALL
        else:
            small_mode = False
            self.tile_w = self.TILE_W
            self.tile_h = self.TILE_H

        self.window.title("Dragon Game Visualiser")
        self.window.geometry(f'{self.game_env.n_cols * self.tile_w}x{self.game_env.n_rows * self.tile_h}+50+50')

        self.canvas = tk.Canvas(self.window)
        self.canvas.configure(bg="white")
        self.canvas.pack(fill="both", expand=True)

        # load images
        if small_mode:
            self.tile_dirt = tk.PhotoImage(file='gui_assets/game_tile_dirt_small.png')
            self.tile_dragon = tk.PhotoImage(file='gui_assets/game_tile_dragon_small.png')
            self.tile_exit = tk.PhotoImage(file='gui_assets/game_tile_exit_small.png')
            self.tile_ladder = tk.PhotoImage(file='gui_assets/game_tile_ladder_small.png')
            self.tile_lava = tk.PhotoImage(file='gui_assets/game_tile_lava_small.png')
            self.tile_stone = tk.PhotoImage(file='gui_assets/game_tile_stone_small.png')
            self.tile_gems = [tk.PhotoImage(file='gui_assets/game_tile_gem_red_small.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_green_small.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_blue_small.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_yellow_small.png')]
            self.tile_sj = tk.PhotoImage(file='gui_assets/game_tile_super_jump_small.png')
            self.tile_sc = tk.PhotoImage(file='gui_assets/game_tile_super_charge_small.png')
        else:
            self.tile_dirt = tk.PhotoImage(file='gui_assets/game_tile_dirt.png')
            self.tile_dragon = tk.PhotoImage(file='gui_assets/game_tile_dragon.png')
            self.tile_exit = tk.PhotoImage(file='gui_assets/game_tile_exit.png')
            self.tile_ladder = tk.PhotoImage(file='gui_assets/game_tile_ladder.png')
            self.tile_lava = tk.PhotoImage(file='gui_assets/game_tile_lava.png')
            self.tile_stone = tk.PhotoImage(file='gui_assets/game_tile_stone.png')
            self.tile_gems = [tk.PhotoImage(file='gui_assets/game_tile_gem_red.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_green.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_blue.png'),
                              tk.PhotoImage(file='gui_assets/game_tile_gem_yellow.png')]
            self.tile_sj = tk.PhotoImage(file='gui_assets/game_tile_super_jump.png')
            self.tile_sc = tk.PhotoImage(file='gui_assets/game_tile_super_charge.png')

        # draw background (all permanent features, i.e. everything except dragon and gems)
        for r in range(self.game_env.n_rows):
            for c in range(self.game_env.n_cols):
                if self.game_env.grid_data[r][c] == GameEnv.SOLID_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_stone, anchor=tk.NW)
                elif self.game_env.grid_data[r][c] == GameEnv.LADDER_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_dirt, anchor=tk.NW)
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_ladder, anchor=tk.NW)
                elif self.game_env.grid_data[r][c] == GameEnv.AIR_TILE and not \
                        (r == self.game_env.exit_row and c == self.game_env.exit_col):
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_dirt, anchor=tk.NW)
                elif self.game_env.grid_data[r][c] == GameEnv.LAVA_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_lava, anchor=tk.NW)
                elif r == self.game_env.exit_row and c == self.game_env.exit_col:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_exit, anchor=tk.NW)
                elif self.game_env.grid_data[r][c] == GameEnv.SUPER_JUMP_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_sj, anchor=tk.NW)
                elif self.game_env.grid_data[r][c] == GameEnv.SUPER_CHARGE_TILE:
                    self.canvas.create_image((c * self.tile_w), (r * self.tile_h), image=self.tile_sc, anchor=tk.NW)

        # draw gems for initial state
        self.gem_images = None
        self.draw_gems(init_state)

        # draw dragon position for initial state
        self.dragon_image = None
        self.draw_dragon(init_state.row, init_state.col)

        self.window.update()
        self.last_update_time = time.time()

        # interface to controller
        self.action_queue = []

        self.window.protocol('WM_DELETE_WINDOW', self.__exit)

    def update_state(self, state):
        # tween dragon to new position
        for i in range(1, self.TWEEN_STEPS + 1):
            time.sleep(self.TWEEN_DELAY)
            self.canvas.delete(self.dragon_image)
            r1 = self.last_state.row + (i / self.TWEEN_STEPS) * (state.row - self.last_state.row)
            c1 = self.last_state.col + (i / self.TWEEN_STEPS) * (state.col - self.last_state.col)
            # remove old dragon position, draw new dragon position
            self.draw_dragon(r1, c1)
            self.window.update()
        self.last_state = state

        # remove all gems and re-add uncollected gems
        for g in self.gem_images:
            self.canvas.delete(g)
        self.draw_gems(state)
        # remove and re-draw dragon
        self.canvas.delete(self.dragon_image)
        self.draw_dragon(state.row, state.col)

        # delay until next update
        self.window.update()

        time_since_last_update = time.time() - self.last_update_time
        time.sleep(max(self.UPDATE_DELAY - time_since_last_update, 0))
        self.last_update_time = time.time()

    def draw_gems(self, state):
        self.gem_images = []
        for i, (gr, gc) in enumerate(self.game_env.gem_positions):
            if state.gem_status[i] == 0:
                tile_gem = self.tile_gems[i % len(self.tile_gems)]
                img = self.canvas.create_image((gc * self.tile_w), (gr * self.tile_h), image=tile_gem, anchor=tk.NW)
                self.gem_images.append(img)

    def draw_dragon(self, row, col):
        self.dragon_image = self.canvas.create_image((col * self.tile_w), (row * self.tile_h),
                                                     image=self.tile_dragon, anchor=tk.NW)

    def __exit(self):
        self.action_queue.insert(0, 'q')


class ControlPanel:

    def __init__(self, game_env, viewer):
        self.game_env = game_env
        self.viewer = viewer

        self.window = tk.Tk()
        self.window.title("Dragon Game Controller")
        self.window.geometry(f'400x200+{max(-150 + ((self.game_env.n_cols * self.viewer.tile_w) // 2), 0)}+'
                             f'{100 + self.game_env.n_rows * self.viewer.tile_h}')

        jump_frame = tk.Frame(self.window)
        j_button = tk.Button(jump_frame, text=' J ', command=self.__press_j)
        j_button.config(font=("Courier", 15))
        j_button.pack(side=tk.LEFT)
        jump_frame.pack(side=tk.TOP)

        top_frame = tk.Frame(self.window)
        wl_button = tk.Button(top_frame, text='W L', command=self.__press_wl)
        wl_button.config(font=("Courier", 15))
        wl_button.pack(side=tk.LEFT)
        empty_button = tk.Button(top_frame, text='   ')
        empty_button.config(font=("Courier", 15))
        empty_button.pack(side=tk.LEFT)
        wr_button = tk.Button(top_frame, text='W R', command=self.__press_wr)
        wr_button.config(font=("Courier", 15))
        wr_button.pack(side=tk.RIGHT)
        top_frame.pack(side=tk.TOP)

        mid_frame = tk.Frame(self.window)
        gl3_button = tk.Button(mid_frame, text='GL3', command=self.__press_gl3)
        gl3_button.config(font=("Courier", 15))
        gl3_button.pack(side=tk.LEFT)
        gl2_button = tk.Button(mid_frame, text='GL2', command=self.__press_gl2)
        gl2_button.config(font=("Courier", 15))
        gl2_button.pack(side=tk.LEFT)
        gl1_button = tk.Button(mid_frame, text='GL1', command=self.__press_gl1)
        gl1_button.config(font=("Courier", 15))
        gl1_button.pack(side=tk.LEFT)
        d1_button = tk.Button(mid_frame, text='D 1', command=self.__press_d1)
        d1_button.config(font=("Courier", 15))
        d1_button.pack(side=tk.LEFT)
        gr3_button = tk.Button(mid_frame, text='GR3', command=self.__press_gr3)
        gr3_button.config(font=("Courier", 15))
        gr3_button.pack(side=tk.RIGHT)
        gr2_button = tk.Button(mid_frame, text='GR2', command=self.__press_gr2)
        gr2_button.config(font=("Courier", 15))
        gr2_button.pack(side=tk.RIGHT)
        gr1_button = tk.Button(mid_frame, text='GR1', command=self.__press_gr1)
        gr1_button.config(font=("Courier", 15))
        gr1_button.pack(side=tk.RIGHT)
        mid_frame.pack(side=tk.TOP)

        bottom_frame = tk.Frame(self.window)
        d2_button = tk.Button(bottom_frame, text='D 2', command=self.__press_d2)
        d2_button.config(font=("Courier", 15))
        d2_button.pack(side=tk.TOP)
        d3_button = tk.Button(bottom_frame, text='D 3', command=self.__press_d3)
        d3_button.config(font=("Courier", 15))
        d3_button.pack(side=tk.BOTTOM)
        bottom_frame.pack(side=tk.TOP)

        self.window.protocol('WM_DELETE_WINDOW', self.__press_q)

        self.window.update()

    def __press_j(self):
        self.viewer.action_queue.append(GameEnv.JUMP)

    def __press_wl(self):
        self.viewer.action_queue.append(GameEnv.WALK_LEFT)

    def __press_wr(self):
        self.viewer.action_queue.append(GameEnv.WALK_RIGHT)

    def __press_gl1(self):
        self.viewer.action_queue.append(GameEnv.GLIDE_LEFT_1)

    def __press_gl2(self):
        self.viewer.action_queue.append(GameEnv.GLIDE_LEFT_2)

    def __press_gl3(self):
        self.viewer.action_queue.append(GameEnv.GLIDE_LEFT_3)

    def __press_gr1(self):
        self.viewer.action_queue.append(GameEnv.GLIDE_RIGHT_1)

    def __press_gr2(self):
        self.viewer.action_queue.append(GameEnv.GLIDE_RIGHT_2)

    def __press_gr3(self):
        self.viewer.action_queue.append(GameEnv.GLIDE_RIGHT_3)

    def __press_d1(self):
        self.viewer.action_queue.append(GameEnv.DROP_1)

    def __press_d2(self):
        self.viewer.action_queue.append(GameEnv.DROP_2)

    def __press_d3(self):
        self.viewer.action_queue.append(GameEnv.DROP_3)

    def __press_q(self):
        self.viewer.action_queue.append('q')








