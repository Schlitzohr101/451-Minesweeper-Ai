#William Murray
#017540586

import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        # """
        # Returns the set of all cells in self.cells known to be mines.
        # """
        # raise NotImplementedError
        # If the count equals the number of cells, all cells are mines
        if len(self.cells) == self.count and self.count > 0:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count is 0, all cells are safe
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If cell is in the sentence, remove it and decrease count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If cell is in the sentence, remove it (count stays the same)
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)
        
        neighbors = set()
        cell_row, cell_column = cell

        for row_offset in range(-1, 2):
            for col_offset in range(-1, 2):
                
                # Skip the cell itself (no offset)
                if row_offset == 0 and col_offset == 0:
                    continue
                
                neighbor_row = cell_row + row_offset
                neighbor_col = cell_column + col_offset

                # Check if neighbor is within bounds
                if 0 <= neighbor_row < self.height and 0 <= neighbor_col < self.width:
                    neighbor_cell = (neighbor_row, neighbor_col)
                    
                    # Only include neighbors that are not already known to be safe or mines
                    if neighbor_cell not in self.safes and neighbor_cell not in self.mines:
                        neighbors.add(neighbor_cell)
                    
                    # If neighbor is known to be a mine, decrease the count
                    elif neighbor_cell in self.mines:
                        count -= 1
                # Add the new sentence if it has cells
        if len(neighbors) > 0:
            new_sentence = Sentence(neighbors, count)
            self.knowledge.append(new_sentence)

        # 4) Mark any additional cells as safe or as mines
        # Iteratively check knowledge base for new inferences
        knowledge_changed = True
        while knowledge_changed:
            knowledge_changed = False

            # Check each sentence for known mines or safes
            for sentence in self.knowledge:
                # Get known mines and safes from this sentence
                known_mines = sentence.known_mines()
                known_safes = sentence.known_safes()

                # Mark any new mines
                if known_mines:
                    for mine in known_mines.copy():
                        if mine not in self.mines:
                            self.mark_mine(mine)
                            knowledge_changed = True

                # Mark any new safes
                if known_safes:
                    for safe in known_safes.copy():
                        if safe not in self.safes:
                            self.mark_safe(safe)
                            knowledge_changed = True

            # 5) Add any new sentences using subset inference
            new_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    # Skip if same sentence or either is empty
                    if s1 == s2 or len(s1.cells) == 0 or len(s2.cells) == 0:
                        continue

                    # If s1 is a subset of s2, infer new sentence
                    if s1.cells.issubset(s2.cells):
                        new_cells = s2.cells - s1.cells
                        new_count = s2.count - s1.count
                        
                        # Create new sentence if it's not empty and not already in knowledge
                        if len(new_cells) > 0:
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                                new_sentences.append(new_sentence)
                                knowledge_changed = True

            # Add new sentences to knowledge base
            self.knowledge.extend(new_sentences)

            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Find safe cells that haven't been clicked yet
        available_safes = self.safes - self.moves_made
        
        if available_safes:
            # Return any safe move
            return available_safes.pop()
        
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Get all possible cells
        all_cells = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                # Only include cells that haven't been chosen and aren't known mines
                if cell not in self.moves_made and cell not in self.mines:
                    all_cells.append(cell)
        
        # Return a random cell if available
        if all_cells:
            return random.choice(all_cells)
        
        return None
