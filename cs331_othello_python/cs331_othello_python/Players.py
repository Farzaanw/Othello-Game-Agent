class Player:
    """Base player class"""
    def __init__(self, symbol):
        self.symbol = symbol

    def get_symbol(self):
        return self.symbol
    
    def get_move(self, board):
        raise NotImplementedError()

class HumanPlayer(Player):
    """Human subclass with text input in command line"""
    def __init__(self, symbol):
        Player.__init__(self, symbol)
        self.total_nodes_seen = 0

    def clone(self):
        return HumanPlayer(self.symbol)
        
    def get_move(self, board):
        col = int(input("Enter col:"))
        row = int(input("Enter row:"))
        return  (col, row)


class AlphaBetaPlayer(Player):
    """Class for Alphabeta AI: implement functions minimax, eval_board, get_successors, get_move
    eval_type: int
        0 for H0, 1 for H1, 2 for H2
    prune: bool
        1 for alpha-beta, 0 otherwise
    max_depth: one move makes the depth of a position to 1, search should not exceed depth
    total_nodes_seen: used to keep track of the number of nodes the algorithm has seearched through
    symbol: X for player 1 and O for player 2
    """
    def __init__(self, symbol, eval_type, prune, max_depth):
        Player.__init__(self, symbol)
        self.eval_type = eval_type
        self.prune = prune
        self.max_depth = int(max_depth) 
        self.max_depth_seen = 0
        self.total_nodes_seen = 0
        if symbol == 'X':
            self.oppSym = 'O'
        else:
            self.oppSym = 'X'


    def terminal_state(self, board):
        # If either player can make a move, it's not a terminal state
        for c in range(board.cols):
            for r in range(board.rows):
                if board.is_legal_move(c, r, "X") or board.is_legal_move(c, r, "O"):
                    return False 
        return True 


    def terminal_value(self, board):
        # Regardless of X or O, a win is float('inf')
        state = board.count_score(self.symbol) - board.count_score(self.oppSym)
        if state == 0:
            return 0
        elif state > 0:
            return float('inf')
        else:
            return -float('inf')


    def flip_symbol(self, symbol):
        # Short function to flip a symbol
        if symbol == "X":
            return "O"
        else:
            return "X"


    def alphabeta(self, board):
        # Write minimax function here using eval_board and get_successors
        # type:(board) -> (int, int)
        best_value = -float('inf')
        best_move = (0, 0)
        alpha = -float('inf')
        beta = float('inf')

        # Iterate through all legal moves
        for col in range(board.cols):
            for row in range(board.rows):
                if (board.is_cell_empty(col, row) and board.is_legal_move(col, row, self.symbol)):
                    # This is a legal move
                    new_board = board.cloneOBoard()
                    new_board.play_move(col, row, self.symbol)  # make move

                    # Evaluate this successor (opponent's turn next)
                    value = self.min_value(new_board, alpha, beta, 1)

                    # Track best move
                    if value > best_value:
                        best_value = value
                        best_move = (col, row)

                    # Alpha-beta pruning at root level
                    if self.prune == 1:
                        alpha = max(alpha, value)
                        if beta <= alpha:
                            break

        return best_move

    def max_value(self, board, alpha, beta, depth):
        # Maximizing player (our turn)
        self.total_nodes_seen += 1

        # Check terminal state or depth limit
        if self.terminal_state(board) or depth == self.max_depth:
            return self.eval_board(board)

        successors = self.get_successors(board, self.symbol)

        # If no legal moves, pass turn to opponent
        if len(successors) == 0:
            return self.min_value(board, alpha, beta, depth + 1)

        # find the best move for maximizing player
        v = -float('inf')
        for successor in successors:
            v = max(v, self.min_value(successor, alpha, beta, depth + 1))

            # Alpha-beta pruning
            if self.prune == 1:
                alpha = max(alpha, v)
                if beta <= alpha:
                    break

        return v

    def min_value(self, board, alpha, beta, depth):
        # Minimizing player (opponent's turn)
        self.total_nodes_seen += 1

        # Check terminal state or depth limit
        if self.terminal_state(board) or depth == self.max_depth:
            return self.eval_board(board)

        successors = self.get_successors(board, self.oppSym)

        # If no legal moves, pass turn back to us
        if len(successors) == 0:
            return self.max_value(board, alpha, beta, depth + 1)

        v = float('inf')
        for successor in successors:
            v = min(v, self.max_value(successor, alpha, beta, depth + 1))

            # Alpha-beta pruning
            if self.prune == 1:
                beta = min(beta, v)
                if beta <= alpha:
                    break

        return v

    def eval_board(self, board):
        # Write eval function here
        # type:(board) -> (float)
        # First check if this is a terminal state (game over)
        if self.terminal_state(board):
            return self.terminal_value(board)

        eval_type = int(self.eval_type)

        if eval_type == 0:
            # H0: Piece Difference - your pieces - opponent pieces
            my_pieces = board.count_score(self.symbol)
            opp_pieces = board.count_score(self.oppSym)
            return float(my_pieces - opp_pieces)

        elif eval_type == 1:
            # H1: Mobility - your legal moves - opponent legal moves
            my_moves = 0
            opp_moves = 0

            # Count my legal moves
            for col in range(board.cols):
                for row in range(board.rows):
                    if (board.is_cell_empty(col, row) and board.is_legal_move(col, row, self.symbol)):
                        my_moves += 1

            # Count opponent's legal moves
            for col in range(board.cols):
                for row in range(board.rows):
                    if (board.is_cell_empty(col, row) and board.is_legal_move(col, row, self.oppSym)):
                        opp_moves += 1

            return float(my_moves - opp_moves)

        elif eval_type == 2:
            # Research: According to "https://bonaludo.wordpress.com/2017/01/04/how-to-win-at-othello-part-1-strategy-basics-stable-discs-and-mobility/#:~:text=Corners%20and%20stable%20discs,it%20will%20be%20always%20stable.&text=they%20%E2%80%9Cadhere%E2%80%9D%20to%20the%20group,the%20disc%20in%20the%20corner."
            # H2: My heuristic - corner control + piece difference
            # Reasoning: "It is impossible to catch discs in corners because such discs are adjacent to only three fields (with no possibility to create catching position). If you put your disc in the corner it will be always stable."
            my_pieces = board.count_score(self.symbol)
            opp_pieces = board.count_score(self.oppSym)

            # Count corner pieces (0,0), (0,3), (3,0), (3,3)
            corners = [(0, 0), (0, 3), (3, 0), (3, 3)]
            my_corners = 0
            opp_corners = 0

            for col, row in corners:
                cell = board.get_cell(col, row)
                if cell == self.symbol:
                    my_corners += 1
                elif cell == self.oppSym:
                    opp_corners += 1

            # Piece difference + corner bonus (3x weight)
            piece_diff = my_pieces - opp_pieces
            corner_bonus = (my_corners - opp_corners) * 3
            return float(piece_diff + corner_bonus)

        return 0.0

    def get_successors(self, board, player_symbol):
        # Write function that takes the current state and generates all successors obtained by legal moves
        # type:(board, player_symbol) -> (list)
        successors = []

        # Iterate through all cells on the board
        for col in range(board.cols):
            for row in range(board.rows):
                # Check if cell is empty and move is legal
                if (board.is_cell_empty(col, row) and
                        board.is_legal_move(col, row, player_symbol)):
                    # Clone the board
                    new_board = board.cloneOBoard()
                    # Play the move on the cloned board
                    new_board.play_move(col, row, player_symbol)
                    # Add the new board state to successors
                    successors.append(new_board)

        return successors

    def get_move(self, board):
        # Write function that returns a move (column, row) here using minimax
        # type:(board) -> (int, int)
        return self.alphabeta(board)

       
        





