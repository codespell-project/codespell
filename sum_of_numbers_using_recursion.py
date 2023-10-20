def sum_of_digits(n):
    if n < 10:
        return n
    else:
        return n % 10 + sum_of_digits(n // 10)


number = int(input("ENTER A NUMBER: "))
result = sum_of_digits(number)
print(f"The sum of digits in {number} is {result}")
