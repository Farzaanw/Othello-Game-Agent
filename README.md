# ♟️ Othello AI Agent (4x4)
**Minimax & Alpha-Beta Pruning Implementation**

---

## 📌 Overview

This project implements a computer opponent for a simplified **4x4 version of Othello** using adversarial search techniques. The agent determines optimal moves using **Minimax** and **Alpha-Beta Pruning**, with support for multiple heuristic evaluation functions.

Othello is a two-player, turn-based strategy game in which players aim to finish with more pieces than their opponent by flipping captured pieces.

### Game Setup

- `X` → Dark player (moves first)  
- `O` → Light player (moves second)  
- ASCII-based board display  
- Initial positions:
  - X at (1,1) and (2,2)
  - O at (1,2) and (2,1)
- If a player has no legal move → turn passes  
- If neither player can move → game ends  
- Winner = player with more pieces  

The 4x4 board is small enough for exhaustive search, but this project also explores **depth-limited search with heuristic evaluation**.

---

## 🧠 Algorithms Implemented

### 1️⃣ Minimax

Standard adversarial search algorithm:
- Recursively evaluates future states
- Assumes optimal play from both players
- Returns the move that maximizes utility

---

### 2️⃣ Alpha-Beta Pruning

Optimized version of Minimax:
- Prunes branches that cannot influence the final decision
- Significantly reduces nodes expanded
- Enables deeper search within the same computational budget

---

## ⏹️ Search Termination

Search stops when:
- A terminal state is reached, OR  
- A predefined depth limit is reached  

Terminal state utilities:

- `0` → Tie  
- `+∞ (inf)` → Win  
- `-∞ (-inf)` → Loss  

For depth-limited search, non-terminal states are evaluated using heuristics:

### 🔹 H0 — Piece Difference
