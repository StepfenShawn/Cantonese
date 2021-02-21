"""
    Test script for cantonese examples
"""
"""
import io
import os
import glob
import datetime

starttime = datetime.datetime.now()
file_list = []
# Get all the file names under examples
for f in glob.glob(os.path.join('..\examples', '*.cantonese')):
    file_list.append(f)
i = 0
print("==============START TEST================")
while i < len(file_list):
    print("Running:" + file_list[i] +  "......")
    os.system("python cantonese.py " + file_list[i])
    print("End")
    i += 1
print("=============END=======================")
endtime = datetime.datetime.now()
# Count and Output the runtime
print("Finished in " + str((endtime - starttime).seconds) + "s!")
"""
class Matrix(object):
	def __init__(self, list_a):
		assert isinstance(list_a, list)
		self.matrix = list_a
		self.shape = (len(list_a), len(list_a[0]))
		self.row = self.shape[0]
		self.column = self.shape[1]

	def build_zero_value_matrix(self, shape):
		zero_value_mat = []
		for i in range(shape[0]):
			zero_value_mat.append([])
			for j in range(shape[1]):
				zero_value_mat[i].append(0)
		zero_value_matrix = Matrix(zero_value_mat)
		return zero_value_matrix

	def matrix_addition(self, the_second_mat):
		assert isinstance(the_second_mat, Matrix)
		assert the_second_mat.shape == self.shape
		result_mat = self.build_zero_value_matrix(self.shape)
		for i in range(self.row):
			for j in range(self.column):
				result_mat.matrix[i][j] = self.matrix[i][j] + the_second_mat.matrix[i][j]
		return result_mat

	def matrix_multiplication(self, the_second_mat):
		assert isinstance(the_second_mat, Matrix)
		assert self.shape[1] == the_second_mat.shape[0]
		shape = (self.shape[0], the_second_mat.shape[1])
		result_mat = self.build_zero_value_matrix(shape)
		for i in range(self.shape[0]):
			for j in range(the_second_mat.shape[1]):
				number = 0
				for k in range(self.shape[1]):
					number += self.matrix[i][k] * the_second_mat.matrix[k][j]
				result_mat.matrix[i][j] = number
		return result_mat


list_1 = [[1, 1], [2, 2]]
list_2 = [[2, 2], [3, 3]]
list_3 = [[1, 1, 1], [2, 2, 2]]

mat1 = Matrix(list_1)
mat2 = Matrix(list_2)
print(mat1.matrix, mat2.matrix)
mat4 = mat1.matrix_addition(mat2)
print(mat4.matrix)

mat3 = Matrix(list_3)
print(mat3.matrix)
mat5 = mat1.matrix_multiplication(mat3)
print(mat5.matrix)