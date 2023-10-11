# this code use the concept of heap sort to sort the number in ascending order

# defining th efunction


def heapify(arr, n, i):
    largest = i
    left_child = 2 * i + 1
    right_child = 2 * i + 2

    if left_child < n and arr[left_child] > arr[largest]:
        largest = left_child

    if right_child < n and arr[right_child] > arr[largest]:
        largest = right_child

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)


def heap_sort(arr):
    n = len(arr)

    # Build a max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Extract elements from the heap one by one
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = (
            arr[0],
            arr[i],
        )  # Swap the root (max element) with the last element
        heapify(arr, i, 0)  # Call max heapify on the reduced heap


# Example usage
arr = [27, 8, 19, 2, 103, 77]
heap_sort(arr)

# displaying the final result

print("Sorted array is:", arr)
