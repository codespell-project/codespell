# Python3 code to demonstrate working of 
# Convert Matrix to dictionary 
# Using dictionary comprehension + range()

# initializing list
test_list = [[5, 6, 7], [8, 3, 2], [8, 2, 1]] 

# printing original list
print("The original list is : " + str(test_list))

# using dictionary comprehension for iteration
res = {idx + 1 : test_list[idx] for idx in range(len(test_list))}

# printing result 
print("The constructed dictionary : " + str(res))
