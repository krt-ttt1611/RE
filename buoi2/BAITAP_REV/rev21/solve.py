from z3 import *

arr_1 = [
  140, 131, 163,  74, 185, 176, 182, 140, 118, 129, 
  217, 255, 209,  79,  31, 217, 231, 229,  89, 102, 
  194, 241, 233,  88,   9, 200, 196, 231, 117,   0, 
  197, 236, 255,  76, 110, 214, 233, 236, 119,  96, 
  214, 246, 200,  86,  17
]

solver = Solver()
flag = [BitVec(f'flag_{i}', 8) for i in range(36)]

for count_1 in range(16,25):
	solver.add((flag[(count_1 - 16)*4] + flag[(count_1 - 16)*4 + 1]) ^ BitVecVal(count_1, 8) == BitVecVal(arr_1[(count_1 - 16) * 5], 8))
	solver.add((flag[(count_1 - 16)*4 + 1] + flag[(count_1 - 16)*4 + 2]) ^ BitVecVal(count_1 + 16, 8) == BitVecVal(arr_1[(count_1 - 16) * 5 + 1], 8))
	solver.add((flag[(count_1 - 16)*4 + 2] + flag[(count_1 - 16)*4 + 3]) ^ BitVecVal(count_1 + 32, 8) == BitVecVal(arr_1[(count_1 - 16) * 5 + 2], 8))
	solver.add((flag[(count_1 - 16)*4] ^ flag[(count_1 - 16)*4 + 3]) ^ BitVecVal(count_1 + 48, 8) == BitVecVal(arr_1[(count_1 - 16)*5 + 3], 8))
	solver.add((flag[(count_1 - 16)*4] + flag[(count_1 - 16)*4 + 2] * 2) ^ BitVecVal(count_1 + 64, 8) == BitVecVal(arr_1[(count_1 - 16)*5 + 4], 8))


text = ''
if solver.check() == sat:
    val = solver.model()
    for i in range(0, 36):
    	char = val[flag[i]].as_long()
    	text += chr(char)

print(text)
	