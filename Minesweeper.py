from z3 import *

class problem:
    # problem_NUM = 0 #Default
    # List of different minesweeper problems
    problems = [
        [   
            [[  0 ,  1 , -1 ,  2 , -1 ,  2 ], 
             [  0 ,  1 ,  1 ,  2 ,  3 , -1 ],
             [  1 ,  1 ,  0 ,  0 ,  3 , -1 ],
             [ -1 ,  1 ,  0 ,  0 ,  2 , -1 ],
             [  1 ,  2 ,  2 ,  3 ,  4 ,  3 ],
             [  0 ,  1 , -1 , -1 , -1 , -1 ]] , 

            [['?', '?', '?', '?', '?', '?'], 
             ['?',  1 ,  1 ,  2 ,  3 , '?'],
             ['?',  1 ,  0 ,  0 ,  3 , '?'],
             ['?',  1 ,  0 ,  0 ,  2 , '?'],
             ['?',  2 ,  2 ,  3 ,  4 , '?'],
             ['?', '?', '?', '?', '?', '?']]

        ],
        [
            [[ -1, 2 , 2 , -1, -1],
             [ 3 , -1, 3 , 2 , 2 ],
             [ 2 , -1, 2 , 0 , 0 ],
             [ 2 , 2 , 1 , 0 , 0 ],
             [ -1, 1 , 0 , 0 , 0 ]],

            [['?','?','?','?','?'],
             ['?','?', 3 , 2 , 2 ],
             ['?','?', 2 , 0 , 0 ],
             ['?', 2 , 1 , 0 , 0 ],
             ['?', 1 , 0 , 0 , 0 ]]
        ],
        [
            [[ 0, 2, -1,  4,  2],
             [ 0, 3, -1, -1, -1],
             [ 0, 2, -1,  6,  4],
	         [ 0, 1,  3, -1, -1],  
             [ 0, 0,  2, -1,  3]],

            [[ 0, 2,'?','?','?'],
             [ 0, 3,'?','?','?'],
             [ 0, 2,'?','?','?'],
             [ 0, 1, 3, '?','?'],
             [ 0, 0, 2, '?','?']]
        
        ]
    ]

    number_of_bombs = [10, 6, 8]

    def __init__(self, problem_no):
        self.problem_NUM = problem_no


    def open(self, row, col):
        return self.problems[self.problem_NUM][0][row][col]
    
    def get_initial_state(self):
        return self.problems[self.problem_NUM][1]

    def get_number_of_bombs(self):
        return self.number_of_bombs[self.problem_NUM]
    


class solver:
    bombs = []
    not_bombs = []
    s = Solver()

    def __init__(self, problem: problem):
        self.problem = problem  #An instance of the problem class the solver will solve
        self.init_state = problem.get_initial_state()
        self.number_of_bombs = problem.get_number_of_bombs()
        self.number_of_not_bombs = len(self.init_state)*len(self.init_state[0]) - self.number_of_bombs

    def add_info(self, r, c, adjacent_bombs, X):
        if r == 0: #Top row
            if c == 0:
                #Top left corner
                self.s.add((X[0][1] + X[1][0] + X[1][1] ) == adjacent_bombs)

            elif c == len(self.init_state[r]) - 1:
                #Top right corner
                self.s.add((X[0][c-1] + X[1][c-1] + X[1][c]) == adjacent_bombs)
            else:
                #Top row not corner
                self.s.add((X[0][c-1] + X[0][c+1] + X[1][c-1] + X[1][c] + X[1][c+1]) == adjacent_bombs)

        elif r == len(self.init_state) - 1: #Bottom row

            if c == 0:
                #Bottom left corner
                self.s.add((X[r-1][0] + X[r-1][1] + X[r][1]) == adjacent_bombs)

            elif c == len(self.init_state[r]) - 1:
                #Bottom right corner
                self.s.add((X[r][c-1] + X[r-1][c-1] + X[r-1][c]) == adjacent_bombs)
            
            else:
                #Bottom row not corner
                self.s.add((X[r][c-1] + X[r][c+1] + X[r-1][c-1] + X[r-1][c] + X[r-1][c+1]) == adjacent_bombs)

        else: # All rows apart from top and bottom
            if c == 0:
                #Left column not corner
                self.s.add((X[r-1][c] + X[r-1][c+1] + X[r][c+1] + X[r+1][c+1] + X[r+1][c]) == adjacent_bombs)

            elif c == len(self.init_state[r]) - 1:
                #Right row not corner
                self.s.add((X[r-1][c] + X[r-1][c-1] + X[r][c-1] + X[r+1][c-1] + X[r+1][c]) == adjacent_bombs)
            else:
                #Middle
                self.s.add((X[r-1][c] + X[r-1][c-1] + X[r][c-1] + X[r+1][c-1] + X[r+1][c] + X[r-1][c+1] + X[r][c+1] + X[r+1][c+1]) == adjacent_bombs)


    def get_solution(self):
        # matrix of integer variables
        X = [ [ Int("x_%s_%s" % (i, j)) for j in range(len(self.init_state[i])) ] 
        for i in range(len(self.init_state)) ]

        # each cell contains a number of bombs between 0 and 1
        cells_c  = [ And(0 <= X[i][j], X[i][j] <= 1) 
                for i in range(len(self.init_state)) for j in range(len(self.init_state[i])) ]
    
        self.s.add(cells_c)

        for r in range(len(self.init_state)): #Iterate over every element in self.init_state
            for c in range(len(self.init_state[r])):
                if self.init_state[r][c] != '?':
                    #Adding the restrictions that square gives to the problem
                    self.add_info(r, c, self.init_state[r][c], X)
        #TODO add limitation that sum of all squares in the grid should be equall to the number of bombs
        self.s.add(Sum([Sum(X[i][j]) for i in range(len(X)) for j in range(len(X[i]))]) == self.problem.get_number_of_bombs())
        #The while-loop that opens new bombs
        while len(self.not_bombs) < self.number_of_not_bombs:
            #Finding a not opened square
            for r in range(len(self.init_state)): #Iterate over every element in self.init_state
                for c in range(len(self.init_state[r])):
                    if self.init_state[r][c] == '?':
                        # Checking if the square is safe to open 
                        # By testing wether it is possible for it to be a bomb
                        self.s.push() 
                        self.s.add(X[r][c] == 1)

                        if self.s.check() == unsat: # The square is safe
                            #return 'HEI'
                            self.not_bombs.append([r, c])
                            adjacent_bombs = self.problem.open(r, c)

                            if adjacent_bombs == -1:
                                print(self.s.assertions())
                                print(r, c)
                                return 'FAIL'

                            self.init_state[r][c] = adjacent_bombs
                            self.s.pop()
                            self.add_info(r, c, adjacent_bombs, X)
                        else:
                            self.s.pop()
                    else:
                        if not [r, c] in self.not_bombs:
                            self.not_bombs.append([r, c])
       
        
        if self.s.check() == sat:
            for r in X:
                for square in r:
                    if self.s.model()[square] == 1:
                        self.bombs.append(square)
                    else:
                        self.not_bombs.append(square)
        else:
            print("Unsatisfiable")

        return 'Bombs:' , self.bombs, 'Not bombs:', self.not_bombs
    


def main():
    problem_no = int(input("Enter the problem number you want to solve between 0 and 1: "))
    
    Problem = problem(problem_no)
    Solver = solver(Problem)

    print(Solver.get_solution())

    
main()