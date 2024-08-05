from game_env import GameEnv
from game_state import GameState

"""
This file contains a restricted transition function.

This transition function does not support testcases for which super charge or super jump tiles must be considered.
This function does not implement an absorbing 'exited' state, and instead returns a 'terminal' flag for each outcome.

You may use or modify this code for your solution (including to add support for super charge/jump and to add an
absorbing 'exited' state).
"""


def get_transition_outcomes_restricted(game_env, state, action):
    """
    This method assumes (state, action) is a valid combination.

    :param game_env: GameEnv instance
    :param state: current state
    :param action: selected action
    :return: list of (next_state, immediate_reward, probability) tuples
    """
    reward = -1 * GameEnv.ACTION_COST[action]
    remaining_prob = 1.0
    outcomes = []

    max_glide1_outcome = max(game_env.glide1_probs.keys())
    max_glide2_outcome = max(game_env.glide2_probs.keys())
    max_glide3_outcome = max(game_env.glide3_probs.keys())

    # handle each action type separately
    if action in GameEnv.WALK_ACTIONS:
        # set movement direction
        if action == GameEnv.WALK_LEFT:
            move_dir = -1
        else:
            move_dir = 1

        # walk on normal walkable tile (super charge case not handled)
        # if on ladder, handle fall case
        if game_env.grid_data[state.row + 1][state.col] == GameEnv.LADDER_TILE and \
                game_env.grid_data[state.row + 2][state.col] not in GameEnv.COLLISION_TILES:
            next_row, next_col = state.row + 2, state.col
            # check if a gem is collected or goal is reached
            next_gem_status, _ = check_gem_collected_or_goal_reached(game_env, next_row, next_col, state.gem_status)
            outcomes.append((GameState(next_row, next_col, next_gem_status), reward, game_env.ladder_fall_prob))
            remaining_prob -= game_env.ladder_fall_prob

        next_row, next_col = state.row, state.col + move_dir
        # check for collision or game over
        next_row, next_col, collision, is_terminal = \
            check_collision_or_terminal(game_env, next_row, next_col, row_move_dir=0, col_move_dir=move_dir)

        # check if a gem is collected or goal is reached
        next_gem_status, _ = check_gem_collected_or_goal_reached(game_env, next_row, next_col, state.gem_status)

        if collision:
            # add any remaining probability to current state
            outcomes.append((GameState(next_row, next_col, next_gem_status),
                             reward - game_env.collision_penalty, remaining_prob))
        elif is_terminal:
            # add any remaining probability to current state
            outcomes.append((GameState(next_row, next_col, next_gem_status),
                             reward - game_env.game_over_penalty, remaining_prob))
        else:
            outcomes.append((GameState(next_row, next_col, next_gem_status), reward, remaining_prob))

    elif action == GameEnv.JUMP:
        # jump on normal walkable tile (super jump case not handled)

        next_row, next_col = state.row - 1, state.col
        # check for collision or game over
        next_row, next_col, collision, is_terminal = \
            check_collision_or_terminal(game_env, next_row, next_col, row_move_dir=-1, col_move_dir=0)

        # check if a gem is collected or goal is reached
        next_gem_status, _ = check_gem_collected_or_goal_reached(game_env, next_row, next_col, state.gem_status)

        if collision:
            # add any remaining probability to current state
            outcomes.append((GameState(next_row, next_col, next_gem_status), reward - game_env.collision_penalty, 1.0))
        elif is_terminal:
            # add any remaining probability to current state
            outcomes.append((GameState(next_row, next_col, next_gem_status), reward - game_env.game_over_penalty, 1.0))
        else:
            outcomes.append((GameState(next_row, next_col, next_gem_status), reward, 1.0))

    elif action in GameEnv.GLIDE_ACTIONS:
        # glide on any valid tile
        # select probabilities to sample move distance
        if action in {GameEnv.GLIDE_LEFT_1, GameEnv.GLIDE_RIGHT_1}:
            probs = game_env.glide1_probs
            max_outcome = max_glide1_outcome
        elif action in {GameEnv.GLIDE_LEFT_2, GameEnv.GLIDE_RIGHT_2}:
            probs = game_env.glide2_probs
            max_outcome = max_glide2_outcome
        else:
            probs = game_env.glide3_probs
            max_outcome = max_glide3_outcome

        # set movement direction
        if action in {GameEnv.GLIDE_LEFT_1, GameEnv.GLIDE_LEFT_2, GameEnv.GLIDE_LEFT_3}:
            move_dir = -1
        else:
            move_dir = 1

        # add each possible movement distance to set of outcomes
        next_row, next_col = state.row + 1, state.col
        for d in range(0, max_outcome + 1):
            next_col = state.col + (move_dir * d)
            # check for collision or game over
            next_row, next_col, collision, is_terminal = \
                check_collision_or_terminal_glide(game_env, next_row, next_col, row_move_dir=0, col_move_dir=move_dir)

            # check if a gem is collected or goal is reached
            next_gem_status, _ = check_gem_collected_or_goal_reached(game_env, next_row, next_col, state.gem_status)

            if collision:
                # add any remaining probability to current state
                outcomes.append((GameState(next_row, next_col, next_gem_status),
                                 reward - game_env.collision_penalty, remaining_prob))
                break
            if is_terminal:
                # add any remaining probability to current state
                outcomes.append((GameState(next_row, next_col, next_gem_status),
                                 reward - game_env.game_over_penalty, remaining_prob))
                break

            # if this state is a possible outcome, add to list
            if d in probs.keys():
                outcomes.append((GameState(next_row, next_col, next_gem_status), reward, probs[d]))
                remaining_prob -= probs[d]

    elif action in GameEnv.DROP_ACTIONS:
        # drop on any valid tile
        next_row, next_col = state.row, state.col

        drop_amount = {GameEnv.DROP_1: 1, GameEnv.DROP_2: 2, GameEnv.DROP_3: 3}[action]

        # drop until drop amount is reached
        for d in range(1, drop_amount + 1):
            next_row = state.row + d

            # check for collision or game over
            next_row, next_col, collision, is_terminal = \
                check_collision_or_terminal_glide(game_env, next_row, next_col, row_move_dir=1, col_move_dir=0)

            # check if a gem is collected or goal is reached
            next_gem_status, _ = check_gem_collected_or_goal_reached(game_env, next_row, next_col, state.gem_status)

            if collision:
                # add any remaining probability to current state
                outcomes.append((GameState(next_row, next_col, next_gem_status),
                                 reward - game_env.collision_penalty, 1.0))
                break
            if is_terminal:
                # add any remaining probability to current state
                outcomes.append((GameState(next_row, next_col, next_gem_status),
                                 reward - game_env.game_over_penalty, 1.0))
                break

            if d == drop_amount:
                outcomes.append((GameState(next_row, next_col, next_gem_status), reward, 1.0))

    else:
        assert False, '!!! Invalid action given to perform_action() !!!'

    return outcomes


def check_collision_or_terminal(game_env, row, col, row_move_dir, col_move_dir):
    """
    Checks for collision with solid tile, or entering lava tile. Returns resulting next state (after bounce back if
    colliding), and booleans indicating if collision or game over has occurred.
    :return: (next_row,  next_col, collision (True/False), terminal (True/False))
    """
    terminal = False
    collision = False
    # check for collision condition
    if (not 0 <= row < game_env.n_rows) or (not 0 <= col < game_env.n_cols) or \
            game_env.grid_data[row][col] in GameEnv.COLLISION_TILES:
        row -= row_move_dir     # bounce back to previous position
        col -= col_move_dir     # bounce back to previous position
        collision = True
    # check for game over condition
    elif game_env.grid_data[row][col] == GameEnv.LAVA_TILE:
        terminal = True

    return row, col, collision, terminal


def check_collision_or_terminal_glide(game_env, row, col, row_move_dir, col_move_dir):
    """
    Checks for collision with solid tile, or entering lava tile for the special glide case (player always moves down by
    1, even if collision occurs). Returns resulting next state (after bounce back if colliding), and booleans indicating
    if collision or game over has occurred.
    :return: (next_row,  next_col, collision (True/False), terminal (True/False))
    """
    # variant for checking glide actions - checks row above as well as current row
    terminal = False
    collision = False
    # check for collision condition
    if (not 0 <= row < game_env.n_rows) or (not 0 <= col < game_env.n_cols) or \
            game_env.grid_data[row][col] in GameEnv.COLLISION_TILES or \
            game_env.grid_data[row - 1][col] in GameEnv.COLLISION_TILES:
        row -= row_move_dir     # bounce back to previous position
        col -= col_move_dir     # bounce back to previous position
        collision = True
    # check for game over condition
    elif game_env.grid_data[row][col] == GameEnv.LAVA_TILE or \
            game_env.grid_data[row - 1][col] == GameEnv.LAVA_TILE:
        terminal = True

    return row, col, collision, terminal


def check_gem_collected_or_goal_reached(game_env, row, col, gem_status):
    """
    Checks if the new row and column contains a gem, and returns an updated gem status. Additionally returns a flag
    indicating whether the goal state has been reached (all gems collected and player at exit).
    :return: new gem_status, solved (True/False)
    """
    is_terminal = False
    # check if a gem is collected (only do this for final position of charge)
    if (row, col) in game_env.gem_positions and \
            gem_status[game_env.gem_positions.index((row, col))] == 0:
        gem_status = list(gem_status)
        gem_status[game_env.gem_positions.index((row, col))] = 1
        gem_status = tuple(gem_status)
    # check for goal reached condition (only do this for final position of charge)
    elif row == game_env.exit_row and col == game_env.exit_col and \
            all(gs == 1 for gs in gem_status):
        is_terminal = True
    return gem_status, is_terminal


