import unittest

def test_matrix(input):
    Matrix(len(input),input).test_matrix_properties()

def diagonal_matrix(input):
    m = []
    for i in range(0,len(input)+1):
        m.append([])
        for j in range(0,len(input)+1):
            if i < j:
                m[i].append(input[i][j-1])
            if i == j:
                m[i].append(0)
            if i > j:
                m[i].append(input[j][i-1])
            

class Matrix:
    def __init__(self, rank, input_values = [[]]):
        self.rank = rank
        self.value = input_values

class matrix_tests(unittest.TestCase):
    def setUp(self):
        self.matrix = Matrix(len(hardcoded_input),hardcoded_input)
        # self.matrix = Matrix(len(secondary_input)+1,diagonal_matrix(secondary_input))

    def tearDown(self):
        pass

    def test_matrix_properties(self):
        for i in range(0,self.matrix.rank):
            self.assertTrue(self.matrix.value[i][i]==0)
            for j in range(i,self.matrix.rank):
                self.assertTrue(self.matrix.value[i][j]==self.matrix.value[j][i])
                for k in range (j,self.matrix.rank):
                    self.assertTrue(self.matrix.value[i][j] + self.matrix.value[j][k] >= self.matrix.value[i][k])
                    self.assertTrue(self.matrix.value[i][k] + self.matrix.value[j][k] >= self.matrix.value[i][j])
                    self.assertTrue(self.matrix.value[i][j] + self.matrix.value[i][k] >= self.matrix.value[j][k])
                    for l in range(k,self.matrix.rank):
                        self.assertTrue(self.matrix.value[i][k]+self.matrix.value[j][l] >= self.matrix.value[i][j]+self.matrix.value[k][l])
                        self.assertTrue(self.matrix.value[i][k]+self.matrix.value[j][l] >= self.matrix.value[j][k]+self.matrix.value[l][i])

hardcoded_input = [[0,2,2,2],[2,0,2,2],[2,2,0,2],[2,2,2,0]]

secondary_input = [[2,2,2],[2,2],[2]]

if __name__ == '__main__':
    unittest.main()
