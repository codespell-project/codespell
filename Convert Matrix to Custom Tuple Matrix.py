# Python3 code to demonstrate working of
# Convert Matrix to Custom Tuple Matrix
# Using zip() + loop

# initializing lists
test_list = [[4, 5, 6], [6, 7, 3], [1, 3, 4]]

# printing original list
print("The original list is : " + str(test_list))

# initializing List elements
add_list = ["Gfg", "is", "best"]

# Convert Matrix to Custom Tuple Matrix
# Using zip() + loop
res = []
for idx, ele in zip(add_list, test_list):
    for e in ele:
        res.append((idx, e))

# printing result
print("Matrix after conversion : " + str(res))
