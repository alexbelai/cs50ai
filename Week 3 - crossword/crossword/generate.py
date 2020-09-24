import sys

from crossword import *
import random
import copy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains:
            toBeRemoved = []
            for x in self.domains[v]:
                if len(x) != v.length:
                    toBeRemoved.append(x)

            for x in toBeRemoved:
                self.domains[v].remove(x)

        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        toBeRemoved = []
        (i, j) = self.crossword.overlaps[x, y]

        # Cycle through x values and check whether a y exists which fulfills constraint
        for xVal in self.domains[x]:
            exists = False
            for yVal in self.domains[y]:
                if xVal[i] == yVal[j]:
                    exists = True
            
            # If no y exists, remove it and turn 'revised' True
            if not exists:
                toBeRemoved.append(xVal)
                revised = True
        
        for v in toBeRemoved:
            self.domains[x].remove(v)

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        queue = set()

        # Fill queue either with all arcs, or arcs specified (if there are any)
        if arcs == None:
            arcList = self.generate_arcs()
            for arc in arcList:
                queue.add(arc)
        else:
            for arc in arcs:
                queue.add(arc)

        # While the queue has elements in it
        while len(queue) != 0:

            # Pick a random element from queue
            elem = queue.pop()
            (x, y) = elem

            # Check for arc consistency
            if self.revise(x, y):

                # If all possible values are removed, problem is not solveable
                if len(self.domains[x]) == 0:
                    return False
                
                # Check for all other variable overlaps ('neighbors') and add them to queue
                for neighbor in (self.crossword.neighbors(x)):

                    # Don't add the arc just modified
                    if neighbor == y:
                        continue
                    
                    queue.add((x, neighbor))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        complete = True
        for v in self.domains:
            if v in assignment:
                continue
            else:
                complete = False
                break
        return complete
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consist = True
        dupes = []
        for v in assignment:
            
            word = assignment.get(v)

            # Check whether variable fits into assigned slot in crossword
            for i in range(len(word)):
                if v.direction == v.ACROSS:
                    if self.crossword.structure[v.i][(v.j + i)] == True:
                        continue
                    else:
                        consist = False
                        break

                elif v.direction == v.DOWN:
                    if self.crossword.structure[(v.i + i)][v.j] == True:
                        continue
                    else:
                        consist = False
                        break
            
            # Check for duplicates
            if word in dupes:
                consist = False
                break
            else:
                dupes.append(word)
            
            # Check for neighboring conflicts
            if len(self.crossword.neighbors(v)) == 0:
                continue
            else:
                for neighbor in self.crossword.neighbors(v):
                    (i, j) = self.crossword.overlaps[v, neighbor]
                    neighborWord = assignment.get(neighbor, 0)

                    # If neighbor not yet assigned, continue
                    if neighborWord == 0:
                        continue
                    else:
                        # If the overlapping letter does not equal what it should, return False
                        if word[i] != neighborWord[j]:
                            consist = False
                            break

        return consist
                    
            

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
 
        orderedList = []

        # Cycle through all values of neighbors, check how many fit with given value of 'var'
        for valueX in self.domains[var]:
            counter = 0
            for neighbor in self.crossword.neighbors(var):
                i, j = self.crossword.overlaps[var, neighbor]

                for valueY in self.domains[neighbor]:
                    if valueX[i] == valueY[j]:
                        counter += 1

            # Append results (value, fit) to list
            orderedList.append([valueX, counter])
        
        # Order list based on counter
        orderedList.sort(key= lambda x: x[1])
        return orderedList

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        unassigned = []
        for v in self.domains:
            if v not in assignment:
                # Unassigned is a list holding each variable, its remaining domain values, and its degree
                unassigned.append([v, len(self.domains[v]), len(self.crossword.neighbors(v))])

        # First sort the list by smallest domain, then by degree
        unassigned.sort(key= lambda x: (x[1], -x[2]))

        # Return first variable in list
        return unassigned[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If complete assignment, return it
        if self.assignment_complete(assignment):
            return assignment
        
        # Else, select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Order selected variable's possible values from domain
        ordered = self.order_domain_values(var, assignment)

        # Check whether assigned value is consistent with assignment
        for i in range(len(ordered)):
            assignment[var] = ordered[i][0]
            consistent = False
            # If it is, go onto next assignment
            if self.consistent(assignment):
                consistent = True

                # Back up domains before AC3 modifies them
                backupDomains = copy.deepcopy(self.domains)

                # Call inferences function (modifies domains but returns a list containing sure values)
                inferences = self.inference(var, assignment)

                # If no inferences were made (Arc consistency not achievable), undo progress
                if inferences is None:
                    self.domains = backupDomains
                else:  
                    # If new sure values exist, add them to assignment
                    for i in range(len(inferences)):
                        assignment[inferences[i][0]] = inferences[i][1]

                result = self.backtrack(assignment)
                if result != None:
                    return result
            # If result is invalid, remove last assigned variable and inferences, continue loop
            if consistent:
                self.domains = backupDomains
                for i in range(len(inferences)):
                    assignment.pop(inferences[i][0])
            assignment.pop(var)

        return None

    def generate_arcs(self):
        """
        Generate a list of all possible arcs between current variables.
        """
        arcList = []
        for x in self.domains:

            # Check whether variables overlap, if they do, add them to arclist
            if len(self.crossword.neighbors(x)) == 0:
                continue
            
            for neighbor in self.crossword.neighbors(x):

                # Check whether variables overlap, if they do, add them to arclist
                if (neighbor, x) not in arcList:
                    arcList.append((x, neighbor))

        return arcList

    def inference(self, var, assignment):
        """
        Draws inferences based on newly assigned variable. Runs AC3 algorithm to enforce arc consistency.
        Returns list of suggested assignments if successful, None if failed.
        """

        # Create neighboring arcs of new variable to pass onto AC3
        arcSet = set()
        for neighbor in self.crossword.neighbors(var):
            arcSet.add((neighbor, var))

        # Call AC3 and check if arc consistency is achieveable
        if self.ac3(arcSet):
            inferences = []
            for var in self.domains:
                if var not in assignment and len(self.domains[var]) == 1:
                    inferences.append([var, list(self.domains[var])[0]])
            return inferences
        else:
            return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
