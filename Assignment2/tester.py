import sys
import time
import os
import hashlib
import random

from game_env import GameEnv
from control.game_env import GameEnv as ControlEnv
from control.game_state import GameState as ControlState
from solution import Solver

"""
Tester script.

Use this script to debug and/or evaluate your solution. You may modify this file if desired.

COMP3702 Assignment 2 "Dragon Game" Support Code

Last updated by njc 15/08/23
"""

VALIDATION_SET_SIZE = 20
VALIDATION_SET_LOOKAHEAD = 100

MAX_ITERATIONS = 1000

VISUALISE_TIME_PER_STEP = 0.7

EPISODE_TRIALS = 50000


def print_usage():
    print("Usage: python tester.py [plan_type] [testcase_file] [-v (optional)]")
    print("    plan_type = 'vi' or 'pi'")
    print("    testcase_file = filename of a valid testcase file (e.g. L1.txt)")
    print("    if -v is specified, the solver's trajectory will be visualised")


def stable_hash(x):
    return hashlib.md5(str(x).encode('utf-8')).hexdigest()


def state_stable_hash(s: ControlState):
    return stable_hash(str((s.row, s.col, s.gem_status)))


def main(arglist):
    os.environ['OPENBLAS_NUM_THREADS'] = '1'

    if len(arglist) != 2 and len(arglist) != 3:
        print_usage()
        return

    plan_type = arglist[0]
    if plan_type not in ['vi', 'pi']:
        print("/!\\ ERROR: Invalid plan_type given")
        print_usage()
        return

    # load environment
    testcase_file = arglist[1]
    game_env = GameEnv(testcase_file)
    control_env = ControlEnv(testcase_file)

    if len(arglist) == 3:
        if arglist[2] == '-v':
            visualise = True
        else:
            print(f"/!\\ ERROR: Invalid option given: {arglist[2]}")
            print_usage()
            return
    else:
        visualise = False

    # construct validation set
    val_states = []
    actions_list = list(ControlEnv.ACTIONS)
    for j in range(VALIDATION_SET_SIZE):
        temp_state = control_env.get_init_state()
        for k in range(VALIDATION_SET_LOOKAHEAD):
            random.seed(stable_hash((j, k)))
            temp_action = random.choice(actions_list)
            valid, _, next_state, _ = control_env.perform_action(temp_state, temp_action)
            if valid:
                temp_state = next_state
        val_states.append(temp_state)

    # run planning
    solver = Solver(game_env)
    iterations = 0
    max_iter_time = 0.0
    iter_time_list = []
    if plan_type == 'vi':
        # values for states in validation set - used for convergence check
        vs_values = {vs: 0.0 for vs in val_states}

        solver.vi_initialise()
        while iterations < MAX_ITERATIONS:
            # read values for states in validation set for this iteration
            for vs in val_states:
                vs_values[vs] = solver.vi_get_state_value(vs)

            # perform an iteration
            t0 = time.time()
            solver.vi_iteration()
            t_iter = time.time() - t0
            if t_iter > max_iter_time:
                max_iter_time = t_iter
            iter_time_list.append(t_iter)

            # break out of loop if converged
            if solver.vi_is_converged():
                break

            iterations += 1

        # test for convergence
        convergence_passed = True
        for vs in val_states:
            if abs(vs_values[vs] - solver.vi_get_state_value(vs)) > (control_env.epsilon * 1.1):
                convergence_passed = False
                break

    else:
        # policy actions for states in validation set - used for convergence check
        vs_policy = {vs: ControlEnv.WALK_LEFT for vs in val_states}

        solver.pi_initialise()
        while not solver.pi_is_converged() and iterations < MAX_ITERATIONS:
            # read policy for states in validation set for this iteration
            for vs in val_states:
                vs_policy[vs] = solver.pi_select_action(vs)

            # perform an iteration
            t0 = time.time()
            solver.pi_iteration()
            t_iter = time.time() - t0
            if t_iter > max_iter_time:
                max_iter_time = t_iter
            iter_time_list.append(t_iter)

            iterations += 1

        # test for convergence
        convergence_passed = True
        for vs in val_states:
            if vs_policy[vs] != solver.pi_select_action(vs):
                convergence_passed = False
                break

    # simulate episode
    level_completed = False
    trial_rewards = []
    control_env = ControlEnv(testcase_file)
    for trial in range(EPISODE_TRIALS):
        persistent_state = control_env.get_init_state()
        episode_reward = 0.0
        visit_count = {persistent_state: 1}

        if visualise and trial == 0:
            try:
                from gui import Viewer
                gui = Viewer(game_env)
            except ModuleNotFoundError:
                gui = None
                control_env.render(persistent_state)
                time.sleep(VISUALISE_TIME_PER_STEP)
        else:
            gui = None

        while not control_env.is_solved(persistent_state) and not control_env.is_game_over(persistent_state) and \
                episode_reward > control_env.reward_min_tgt:
            # query solver to select an action
            if plan_type == 'vi':
                action = solver.vi_select_action(persistent_state)

            else:   # plan_type == 'pi'
                action = solver.pi_select_action(persistent_state)

            # simulate outcome of action
            seed = (str(control_env.episode_seed) + str(trial) + state_stable_hash(persistent_state) +
                    stable_hash(visit_count[persistent_state]))
            valid, reward, persistent_state, is_terminal = control_env.perform_action(persistent_state, action,
                                                                                      seed=seed)

            # updated visited state count (for de-randomisation)
            visit_count[persistent_state] = visit_count.get(persistent_state, 0) + 1

            # update episode reward
            episode_reward += reward

            if visualise and trial == 0:
                print(f'Selected: {action} | Received a reward value of {reward}')

                if gui is not None:
                    gui.update_state(persistent_state)
                else:
                    control_env.render(persistent_state)
                    time.sleep(VISUALISE_TIME_PER_STEP)

        level_completed = control_env.is_solved(persistent_state) or level_completed
        trial_rewards.append(episode_reward)

    # average reward over trials
    avg_reward = sum(trial_rewards) / EPISODE_TRIALS

    # average time per iteration
    avg_iter_time = sum(iter_time_list) / len(iter_time_list)

    msg = f'===== Testcase {testcase_file.split("/")[-1].split(".")[0]} ' \
          f'{"Value Iteration" if plan_type == "vi" else "Policy Iteration"} =====\n'
    msg += f'Number of Iterations: {iterations}    (iterations max target: ' \
           f'{control_env.vi_iter_max_tgt if plan_type == "vi" else control_env.pi_iter_max_tgt})\n'
    msg += f'Average time taken per iteration: {round(avg_iter_time, 4)}    ' \
           f'(average time max target: ' \
           f'{control_env.vi_time_max_tgt if plan_type == "vi" else control_env.pi_time_max_tgt})\n'
    msg += f'Maximum time taken per iteration: {round(max_iter_time, 4)}\n'
    msg += ('Values converged!\n' if convergence_passed else
            'Values failed to converge within the maximum number of iterations.\n')
    if level_completed:
        msg += f'Level completed!\nTotal reward: {round(avg_reward, 1)}    ' \
               f'(reward max target: {control_env.reward_max_tgt})\n'
    else:
        msg += 'Level not completed before reward went below reward min target.\n'
    print(msg)


if __name__ == '__main__':
    main(sys.argv[1:])



