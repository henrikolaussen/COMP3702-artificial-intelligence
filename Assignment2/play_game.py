import sys
import time

from game_env import GameEnv
from gui import Viewer, ControlPanel

"""
play_game.py

Running this file launches an interactive game session. Becoming familiar with the game mechanics may be helpful in
designing your solution.

The script takes 1 argument:
- input_filename, which must be a valid testcase file (e.g. one of the provided files in the testcases directory)

When prompted for an action, type one of the available action strings (e.g. wr, wl, etc) and press enter to perform the
entered action.

COMP3702 Assignment 2 "Dragon Game" Support Code

Last updated by njc 29/08/23
"""


def main(arglist):
    if len(arglist) != 1:
        print("Running this file launches an interactive game session.")
        print("Usage: play_game.py [input_filename]")
        return -1

    input_file = arglist[0]

    game_env = GameEnv(input_file)
    viewer = Viewer(game_env)
    control_panel = ControlPanel(game_env, viewer)
    persistent_state = game_env.get_init_state()
    total_reward = 0

    # run simulation
    while True:
        viewer.update_state(persistent_state)
        while len(viewer.action_queue) == 0:
            control_panel.window.update()
            time.sleep(0.01)
        a = viewer.action_queue.pop(0)

        if 'q' in a:
            print('\nQuitting.')
            break
        valid, reward, new_state, terminal = game_env.perform_action(persistent_state, a, seed=time.time())
        if not valid:
            print('Action is invalid for the current state. Choose again.')
            continue
        else:
            persistent_state = new_state
        total_reward += reward

        if terminal:
            print(f'Received reward: {reward} | Total reward: {round(total_reward, 1)}')
            viewer.update_state(persistent_state)
            if reward > (-1 * game_env.game_over_penalty):
                print(f'Level completed with total reward of {round(total_reward, 1)} '
                      f'(target reward = {game_env.reward_max_tgt})')
                break
            else:
                print(f'Game Over, with total reward of {round(total_reward, 1)} '
                      f'(target reward = {game_env.reward_max_tgt})')
                break
        else:
            print(f'Received reward: {reward} | Total reward: {round(total_reward, 1)}', end='\r')


if __name__ == '__main__':
    main(sys.argv[1:])
