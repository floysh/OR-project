MAX_INT = 9e10

class SymmerticGraph :

    def __init__(self, cost_matrix):
        self.cost_matrix = cost_matrix


    def edges(self):
        n = len(self.cost_matrix)
        return [(a,b) for a in range(0,n) for b in range(a+1, n)]

    def cost(self, a, b):
        if a == b :
            return 0
        elif a < b :
            return self.cost_matrix[a,b]
        else:
            return self.cost_matrix[b,a]

    def cost(self, (a,b)):
        return self.cost(self, a, b)

    def outward_star(self, node)
        return self.cost_matrix[node:]