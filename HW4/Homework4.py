# HW4
# MSML606
# Author: Chenhongshu Yu
# UID: 116610971

# Statement: The use of external resources is clearly cited. 
# If no citation is found for any specific part of my submission, 
# it means "No external sources were used; all ideas are my own or from course lecture slides".

import csv
import random
class Homework4:

    # QUESTION 1
    # Implement randomized quicksort and heapsort in the below function
    # Input for the function - an array of floating point numbers ex: [3.0,9.0,1.0]
    # Output - sorted list of numbers ex: [1.0,3.0,9.0]
    # Numbers can be negative, repeated, and floating point numbers
    # DO NOT USE THE INBUILT HEAPQ MODULE TO SOLVE THE PROBLEMS

    # Choose the second version for Randomized Quicksort: 
    # Random pivot selection: 
    # Exchange pivot with an element chosen at random from A[l...r] in Partition.
    def randomQuickSort(self,nums:list) -> list:
        # Keep input unchanged by making a copy
        arr = nums.copy()

        # Partition: values <= pivot: move left, others stay right
        def partition(l:int, r:int) -> int:
            pivot = arr[r]
            i = l - 1

            for j in range(l, r):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

            arr[i + 1], arr[r] = arr[r], arr[i + 1]

            return i + 1

        # Randomly choose pivot from current subarray and place at the end
        def randomized_partition(l:int, r:int) -> int:
            pivot_index = random.randint(l, r)
            arr[pivot_index], arr[r] = arr[r], arr[pivot_index]

            return partition(l, r)

        # Recursively sort elements before and after pivot
        def quicksort(l:int, r:int) -> None:
            if l < r:
                pivot_pos = randomized_partition(l, r)
                quicksort(l, pivot_pos - 1)
                quicksort(pivot_pos + 1, r)

        # Arrays with size 0 or 1 (already sorted)
        if len(arr) <= 1:
            return arr

        quicksort(0, len(arr) - 1)

        return arr

    # HeapSort Steps:
    # 1. Build a max-heap from the input.
    # 2. Repeatedly swap root (current maximum) with the last element in the unsorted region.
    # 3. Shrink heap size by one and heapify from root.
    def heapSort(self,nums:list) -> list:
        # Keep input unchanged by making a copy
        arr = nums.copy()
        n = len(arr)

        def heapify(size:int, root:int) -> None:
            # Root is the largest (max-heap)
            largest = root
            l = 2 * root + 1
            r = 2 * root + 2

            # Compare root with left and right children, update largest as needed
            if l < size and arr[l] > arr[largest]:
                largest = l
            if r < size and arr[r] > arr[largest]:
                largest = r

            if largest != root:
                arr[root], arr[largest] = arr[largest], arr[root]
                # Continue down
                heapify(size, largest)

        # Build the max-heap based on the input array
        for i in range(n // 2 - 1, -1, -1):
            heapify(n, i)

        # Move current max to the end and restore heap property
        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            heapify(end, 0)

        return arr


# Main Function
# Do not edit the code below
if __name__=="__main__":
    homework4  = Homework4()
    testCasesforSorting = []
    try:
        with open('testcases.csv','r') as file:
            testCases = csv.reader(file)
            for row in testCases:
                testCasesforSorting.append(row)
    except FileNotFoundError:
        print("File Not Found") 
    
    # Running Test Cases for Question 1
    print("RUNNING TEST CASES FOR QUICKSORT: ")
    
    for row , (inputValue,expectedOutput) in enumerate(testCasesforSorting,start=1):
        if(inputValue=="" and expectedOutput==""):
            inputValue=[]
            expectedOutput=[]
        else:
            inputValue=inputValue.split(" ")
            inputValue = [float(i) for i in inputValue]
            expectedOutput=expectedOutput.split(" ")
            expectedOutput = [float(i) for i in expectedOutput]
        actualOutput = homework4.randomQuickSort(inputValue)
        are_equal = all(x == y for x, y in zip(actualOutput, expectedOutput))
        if(are_equal):
            print(f"Test Case {row} : PASSED")
        else:
             print(f"Test Case {row}: Failed (Expected : {expectedOutput}, Actual: {actualOutput})")
    
    print("\nRUNNING TEST CASES FOR HEAPSORT: ")         
    for row , (inputValue,expectedOutput) in enumerate(testCasesforSorting,start=1):
        if(inputValue=="" and expectedOutput==""):
            inputValue=[]
            expectedOutput=[]
        else:
            inputValue=inputValue.split(" ")
            inputValue = [float(i) for i in inputValue]
            expectedOutput=expectedOutput.split(" ")
            expectedOutput = [float(i) for i in expectedOutput]
        actualOutput = homework4.heapSort(inputValue)
        are_equal = all(x == y for x, y in zip(actualOutput, expectedOutput))
        if(are_equal):
            print(f"Test Case {row} : PASSED")
        else:
             print(f"Test Case {row}: Failed (Expected : {expectedOutput}, Actual: {actualOutput})")
