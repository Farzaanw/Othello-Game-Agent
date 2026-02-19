from Players import *
import sys
import OthelloBoard


class GameDriver:
    def __init__(self, p1type="human", p2type="alphabeta", num_rows=4, num_cols=4, p1_eval_type=0, p1_prune=False, p2_eval_type=0, p2_prune=False, p1_depth=8, p2_depth=8):
        if p1type.lower() in "human":
            self.p1 = HumanPlayer('X')

        elif p1type.lower() in "alphabeta":
            self.p1 = AlphaBetaPlayer('X', p1_eval_type, p1_prune, p1_depth)

        else:
            print("Invalid player 1 type!")
            exit(-1)

        if p2type.lower() in "human":
            self.p2 = HumanPlayer('O')

        elif p2type.lower() in "alphabeta":
            self.p2 = AlphaBetaPlayer('O', p2_eval_type, p2_prune, p2_depth)

        else:
            print("Invalid player 2 type!")
            exit(-1)

        self.board = OthelloBoard.OthelloBoard(num_rows, num_cols, self.p1.symbol, self.p2.symbol)
        self.board.initialize()

    def display(self):
        print("Player 1 (", self.p1.symbol, ") score: ", \
                self.board.count_score(self.p1.symbol))

    def process_move(self, curr_player, opponent):
        invalid_move = True
        while(invalid_move):
            (col, row) = curr_player.get_move(self.board)
            if( not self.board.is_legal_move(col, row, curr_player.symbol)):
                print("Invalid move")
            else:
                print("Move:", [col,row], "\n")
                self.board.play_move(col,row,curr_player.symbol)
                return


    def run(self):
        current = self.p1
        opponent = self.p2
        self.board.display()

        cant_move_counter, toggle = 0, 0

        #main execution of game
        print("Player 1(", self.p1.symbol, ") move:")
        # Get a move, then display it in a while loop
        turn_count = 0
        while True:
            if self.board.has_legal_moves_remaining(current.symbol):
                turn_count += 1
                cant_move_counter = 0
                self.process_move(current, opponent)
                self.board.display()
            else:
                print("Can't move")
                if(cant_move_counter == 1):
                    break
                else:
                    cant_move_counter +=1
            toggle = (toggle + 1) % 2
            if toggle == 0:
                current, opponent = self.p1, self.p2
                print("Player 1(", self.p1.symbol, ") move:")
            else:
                current, opponent = self.p2, self.p1
                print("Player 2(", self.p2.symbol, ") move:")

        #decide win/lose/tie state
        state = self.board.count_score(self.p1.symbol) - self.board.count_score(self.p2.symbol)
        if( state == 0):
            print("Tie game!!")
        elif state >0:
            print("Player 1 Wins!")
        else:
            print("Player 2 Wins!")
        print("turn count:", turn_count)
        print("total nodes seen by p1", self.p1.total_nodes_seen)
        print("total nodes seen by p2", self.p2.total_nodes_seen)

def run_experiment1():
    """Experiment 1: Search vs Depth - measure nodes at different depths"""
    depths = [2, 4, 6, 8, 10, 12]
    heuristics = [0, 1, 2]
    h_names = ['H0 (Piece Diff)', 'H1 (Mobility)', 'H2 (Corner)']

    # Initialize results structure
    results = {}
    for h in heuristics:
        results[h] = {'prune_off': {}, 'prune_on': {}}

    print("\nEXPERIMENT 1: SEARCH VS DEPTH\n")
    for depth in depths:
        print("DEPTH: " + str(depth))

        for h_type, h_name in zip(heuristics, h_names):
            print("  " + h_name)

            for prune, label in [(0, "OFF"), (1, "ON")]:
                # Set board to intial state for each run
                board = OthelloBoard.OthelloBoard(4, 4, 'X', 'O')
                board.initialize()

                # Create player with specified heuristic, pruning, and depth
                player = AlphaBetaPlayer('X', h_type, prune, depth)

                # Run alpha-beta search and count nodes
                player.alphabeta(board)
                nodes = player.total_nodes_seen

                status = 'prune_on' if prune else 'prune_off'
                results[h_type][status][depth] = nodes

                print("    Pruning " + label + ": " + str(nodes) + " nodes")

    # Create plot line graph: # of nodes vs. depth for pruning on/off
    try:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, (h_type, h_name) in enumerate(zip(heuristics, h_names)):
            ax = axes[idx]
            
            # Extract data
            no_prune = [results[h_type]['prune_off'][d] for d in depths]
            with_prune = [results[h_type]['prune_on'][d] for d in depths]
            
            # Plot lines
            ax.plot(depths, no_prune, 'o-', label='No Pruning', linewidth=2, markersize=6)
            ax.plot(depths, with_prune, 's-', label='With Pruning', linewidth=2, markersize=6)
            
            ax.set_xlabel('Depth')
            ax.set_ylabel('Nodes Expanded')
            ax.set_title(h_name)
            ax.set_yscale('log')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('experiment1_results.png')
        print("Graph saved as experiment1_results.png")
    except ImportError:
        print("matplotlib not installed - skipping plot")

    print("\nExperiment 1 complete!\n")


def run_experiment2():
    """Experiment 2: Heuristic Quality - play heuristics against each other from both sides"""
    depths = [2, 4, 6, 8]
    h_names = ['H0', 'H1', 'H2']
    pairings = [(0, 1), (0, 2), (1, 2)]

    print("\nEXPERIMENT 2: HEURISTIC QUALITY (WITH PRUNING)\n")
    results = {}

    for depth in depths:
        print("DEPTH: " + str(depth))
        results[depth] = {}

        for h1, h2 in pairings:
            # Run both sides of the matchup
            for side1, side2 in [(h1, h2), (h2, h1)]:
                matchup_key = h_names[side1] + " vs " + h_names[side2]

                # Create and play game
                game = GameDriver('alphabeta', 'alphabeta', 4, 4, side1, 1, side2, 1, depth, depth)

                # Run the game loop until completion
                current = game.p1
                cant_move_counter = 0
                while True:
                    if game.board.has_legal_moves_remaining(current.symbol):
                        cant_move_counter = 0
                        (col, row) = current.get_move(game.board)
                        game.board.play_move(col, row, current.symbol)
                    else:
                        if cant_move_counter == 1:
                            break
                        cant_move_counter += 1
                    current = game.p2 if current == game.p1 else game.p1

                # Determine winner
                score_diff = (game.board.count_score('X') - game.board.count_score('O'))
                if score_diff > 0:
                    result_text = h_names[side1] + " (X) wins"
                elif score_diff < 0:
                    result_text = h_names[side2] + " (O) wins"
                else:
                    result_text = "Tie"

                # Store and print result
                results[depth][matchup_key] = result_text
                print("  " + matchup_key + ": " + result_text)

    # Print summary
    for depth in depths:
        print("\nDEPTH: " + str(depth))
        print("-" * 50)
        for h1, h2 in pairings:
            for side1, side2 in [(h1, h2), (h2, h1)]:
                matchup_key = h_names[side1] + " vs " + h_names[side2]
                print("  " + matchup_key.ljust(20) +
                      results[depth][matchup_key])
    print("\nExperiment 2 complete!\n")


def main():
    # Check if running experiment mode
    if len(sys.argv) > 1 and sys.argv[1].lower() == "experiment1":
        run_experiment1()
        return
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "experiment2":
        run_experiment2()
        return
    
    # Else, run normal game
    board_size = 4 
    game = GameDriver(sys.argv[1], sys.argv[2], board_size, board_size, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    game.run()


if __name__ == "__main__":
    main()

