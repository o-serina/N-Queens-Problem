#Authors: Serina Oswalt & Owen Brock
#AI 6150 Project 2
import random
from statistics import mean

SIDEWAYS_CAP = 100
RR_SAMPLES = 200
RUN_SETS = [50, 100, 200, 500, 1000, 1500]


def random_board(n):
    # create a random board (1 queen per row)
    return [random.randrange(n) for _ in range(n)]


def attack_pairs(board):
    # count how many pairs of queens are attacking each other
    total = 0
    size = len(board)

    for r1 in range(size):
        for r2 in range(r1 + 1, size):
            c1 = board[r1]
            c2 = board[r2]

            if c1 == c2 or abs(c1 - c2) == abs(r1 - r2):
                total += 1

    return total


def possible_moves(board):
    # generate all possible moves by changing one queen
    size = len(board)
    next_states = []

    for row in range(size):
        old_col = board[row]

        for new_col in range(size):
            if new_col == old_col:
                continue

            trial = board.copy()
            trial[row] = new_col
            next_states.append(trial)

    return next_states


def pick_move(board):
    # pick a best neighbor (lowest heuristic)
    candidates = possible_moves(board)
    best_score = None
    best_choices = []

    for state in candidates:
        score = attack_pairs(state)

        if best_score is None or score < best_score:
            best_score = score
            best_choices = [state]
        elif score == best_score:
            best_choices.append(state)

    return random.choice(best_choices), best_score


def climb_once(start_board, sideways_ok=False, sideways_cap=SIDEWAYS_CAP):
    # run hill climbing once
    board = start_board.copy()
    score = attack_pairs(board)

    moves_taken = 0
    sideways_count = 0
    history = [(board.copy(), score)]

    while True:
        if score == 0:
            return {
                "solved": True,
                "moves": moves_taken,
                "end_board": board,
                "end_score": score,
                "history": history,
            }

        next_board, next_score = pick_move(board)

        if next_score < score:
            # normal improvement
            board = next_board
            score = next_score
            moves_taken += 1
            sideways_count = 0
            history.append((board.copy(), score))
            continue

        if sideways_ok and next_score == score and sideways_count < sideways_cap:
            # allow sideways move (same score)
            board = next_board
            score = next_score
            moves_taken += 1
            sideways_count += 1
            history.append((board.copy(), score))
            continue

        # stuck
        return {
            "solved": False,
            "moves": moves_taken,
            "end_board": board,
            "end_score": score,
            "history": history,
        }


def batch_trials(n, runs, sideways_ok=False, sideways_cap=SIDEWAYS_CAP):
    # run multiple times and collect stats
    wins = 0
    losses = 0

    win_moves = []
    loss_moves = []

    examples = []

    for run_index in range(runs):
        start = random_board(n)
        result = climb_once(start, sideways_ok=sideways_ok, sideways_cap=sideways_cap)

        if result["solved"]:
            wins += 1
            win_moves.append(result["moves"])
        else:
            losses += 1
            loss_moves.append(result["moves"])

        # save a few examples to show later
        if run_index < 4:
            examples.append({
                "start": start,
                "solved": result["solved"],
                "moves": result["moves"],
                "history": result["history"],
            })

    return {
        "runs": runs,
        "wins": wins,
        "losses": losses,
        "win_pct": (wins / runs) * 100 if runs else 0.0,
        "loss_pct": (losses / runs) * 100 if runs else 0.0,
        "avg_win_moves": mean(win_moves) if win_moves else 0.0,
        "avg_loss_moves": mean(loss_moves) if loss_moves else 0.0,
        "examples": examples,
    }


def restart_until_solved(n, sideways_ok=False, sideways_cap=SIDEWAYS_CAP):
    # keep restarting until a solution is found
    restarts = 0
    total_moves = 0

    while True:
        start = random_board(n)
        result = climb_once(start, sideways_ok=sideways_ok, sideways_cap=sideways_cap)
        total_moves += result["moves"]

        if result["solved"]:
            return {
                "restarts": restarts,
                "moves": total_moves,
                "end_board": result["end_board"],
            }

        restarts += 1


def restart_experiment(n, samples=RR_SAMPLES, sideways_cap=SIDEWAYS_CAP):
    # compare restart behavior with and without sideways moves
    plain_restart_counts = []
    plain_move_counts = []

    sideways_restart_counts = []
    sideways_move_counts = []

    for _ in range(samples):
        plain = restart_until_solved(n, sideways_ok=False, sideways_cap=sideways_cap)
        plain_restart_counts.append(plain["restarts"])
        plain_move_counts.append(plain["moves"])

        side = restart_until_solved(n, sideways_ok=True, sideways_cap=sideways_cap)
        sideways_restart_counts.append(side["restarts"])
        sideways_move_counts.append(side["moves"])

    return {
        "samples": samples,
        "plain_avg_restarts": mean(plain_restart_counts) if plain_restart_counts else 0.0,
        "plain_avg_moves": mean(plain_move_counts) if plain_move_counts else 0.0,
        "side_avg_restarts": mean(sideways_restart_counts) if sideways_restart_counts else 0.0,
        "side_avg_moves": mean(sideways_move_counts) if sideways_move_counts else 0.0,
    }


def show_example(example):
    print(f"Start board: {example['start']}")
    print(f"Outcome: {'Solved' if example['solved'] else 'Stuck'}")
    print(f"Moves used: {example['moves']}")
    print("Path:")

    for step_num, (state, score) in enumerate(example["history"]):
        print(f"  Move {step_num}: board={state}, h={score}")

    print()


def show_summary(title, data_rows):
    print(title)
    print("=" * len(title))
    print(f"{'Runs':>6} {'Win %':>10} {'Loss %':>10} {'Avg Win':>12} {'Avg Loss':>12}")

    for row in data_rows:
        print(
            f"{row['runs']:>6} "
            f"{row['win_pct']:>10.2f} "
            f"{row['loss_pct']:>10.2f} "
            f"{row['avg_win_moves']:>12.2f} "
            f"{row['avg_loss_moves']:>12.2f}"
        )

    print()


def show_restart_summary(data):
    print("Random Restart Results")
    print("======================")
    print(f"Trials: {data['samples']}")
    print(f"Average restarts without sideways moves: {data['plain_avg_restarts']:.2f}")
    print(f"Average moves without sideways moves: {data['plain_avg_moves']:.2f}")
    print(f"Average restarts with sideways moves: {data['side_avg_restarts']:.2f}")
    print(f"Average moves with sideways moves: {data['side_avg_moves']:.2f}")
    print()


def main():
    print("N-Queens Hill Climbing\n")

    try:
        n = int(input("Enter n: ").strip())
        if n < 4:
            print("Use n >= 4.")
            return
    except ValueError:
        print("Invalid input.")
        return

    print("\nRunning tests...")

    basic_rows = [batch_trials(n, runs, sideways_ok=False) for runs in RUN_SETS]
    sideways_rows = [batch_trials(n, runs, sideways_ok=True) for runs in RUN_SETS]
    rr_data = restart_experiment(n)

    print()
    show_summary("Basic Hill Climbing", basic_rows)
    show_summary("Hill Climbing with Sideways Moves", sideways_rows)
    show_restart_summary(rr_data)

    print("Example runs (basic):")
    for ex in basic_rows[0]["examples"]:
        show_example(ex)

    print("Example runs (sideways):")
    for ex in sideways_rows[0]["examples"]:
        show_example(ex)


if __name__ == "__main__":
    main()