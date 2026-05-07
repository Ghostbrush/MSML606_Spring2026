# HW6
# MSML606
# Author: Chenhongshu Yu
# UID: 116610971

# Statement: The use of external resources is clearly cited. 
# If no citation is found for any specific part of my submission, 
# it means "No external sources were used; all ideas are my own or from course lecture slides".

import csv
import ast  # For safely evaluating string representation of list
from collections import deque

class Homework6:
    #Question 1 Number of Islands
    def countIslandsUsingDFS(self, grid):
        # when not grid or empty grid, return 0
        if not grid or len(grid) == 0 or len(grid[0]) == 0:
            return 0
        
        visited = set()
        islands = 0
        rows, cols = len(grid), len(grid[0])

        # DFS to mark all connected land cells as visited
        def dfs(r, c):
            # Check boundaries, water, and visited cells
            if (r < 0 or r >= rows or 
                c < 0 or c >= cols or 
                str(grid[r][c]) == '0' or 
                (r, c) in visited):
                return
            
            visited.add((r, c))

            # Explore neighbors in 4 directions
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        # Iterate through each cell in the grid
        for r in range(rows):
            for c in range(cols):
                # If it's land and not visited, it's a new island
                if str(grid[r][c]) == '1' and (r, c) not in visited:
                    islands += 1
                    dfs(r, c)

        return islands

    # BFS using queue
    def countIslandsUsingBFS(self, grid):
        # when not grid or empty grid, return 0
        if not grid or len(grid) == 0 or len(grid[0]) == 0:
            return 0

        visited = set()
        islands = 0
        rows, cols = len(grid), len(grid[0])
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # BFS to mark all connected land cells as visited
        def bfs(start_r, start_c):
            # Init queue for BFS and mark the starting cell as visited
            queue = deque([(start_r, start_c)])
            visited.add((start_r, start_c))

            # Process the queue until it's empty
            while queue:
                r, c = queue.popleft()

                # Explore neighbors in 4 directions
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if (0 <= new_r < rows and
                        0 <= new_c < cols and
                        str(grid[new_r][new_c]) == '1' and
                        (new_r, new_c) not in visited):
                        visited.add((new_r, new_c))
                        queue.append((new_r, new_c))

        # Iterate through each cell in the grid
        for r in range(rows):
            for c in range(cols):
                # If it's land and not visited, it's a new island
                if str(grid[r][c]) == '1' and (r, c) not in visited:
                    islands += 1
                    bfs(r, c)

        return islands

    # DFS using an explicit stack
    def countIslandsUsingDFSUsingStack(self, grid):
        # when not grid or empty grid, return 0
        if not grid or len(grid) == 0 or len(grid[0]) == 0:
            return 0

        visited = set()
        islands = 0
        rows, cols = len(grid), len(grid[0])
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # DFS using an explicit stack to mark all connected land cells as visited
        def dfs_stack(start_r, start_c):
            stack = [(start_r, start_c)]
            visited.add((start_r, start_c))

            # Process the stack until it's empty
            while stack:
                r, c = stack.pop()

                # Explore neighbors in 4 directions
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if (0 <= new_r < rows and
                        0 <= new_c < cols and
                        str(grid[new_r][new_c]) == '1' and
                        (new_r, new_c) not in visited):
                        visited.add((new_r, new_c))
                        stack.append((new_r, new_c))

        # Iterate through each cell in the grid
        for r in range(rows):
            for c in range(cols):
                # If it's land and not visited, it's a new island
                if str(grid[r][c]) == '1' and (r, c) not in visited:
                    islands += 1
                    dfs_stack(r, c)

        return islands

    def performanceAnalysis(): # optional
        pass

# DO NOT MODIFY THE CODE BELOW THIS LINE

if __name__ == "__main__":
    homework6 = Homework6()
    testCasesforQuestion1 = []

    try:
        with open('testcases1.csv', 'r') as file:
            testCases = csv.reader(file)
            for row in testCases:
                if len(row) == 2:
                    testCasesforQuestion1.append(row)
    except FileNotFoundError:
        print("File Not Found")
    print("RUNNING TEST CASES FOR NUMBER OF ISLANDS:")
    for row_num, (inputValue, expectedOutput) in enumerate(testCasesforQuestion1, start=1):
        try:
            inputGrid = ast.literal_eval(inputValue.strip())
            expectedOutput = int(expectedOutput.strip())
            actualOutputDFS = homework6.countIslandsUsingDFS(inputGrid)
            if actualOutputDFS == expectedOutput:
                print(f"Test Case {row_num}: PASSED Using DFS")
            else:
                print(f"Test Case {row_num}: FAILED (Expected: {expectedOutput}, Got: {actualOutputDFS}) Using DFS")
            actualOutputBFS = homework6.countIslandsUsingBFS(inputGrid)
            if actualOutputBFS == expectedOutput:
                print(f"Test Case {row_num}: PASSED Using BFS")
            else:
                print(f"Test Case {row_num}: FAILED (Expected: {expectedOutput}, Got: {actualOutputBFS}) Using BFS")
            actualOutputDFSUsingStack = homework6.countIslandsUsingDFSUsingStack(inputGrid)
            if actualOutputDFSUsingStack == expectedOutput:
                print(f"Test Case {row_num}: PASSED Using DFS Stack")
            else:
                print(f"Test Case {row_num}: FAILED (Expected: {expectedOutput}, Got: {actualOutputDFSUsingStack}) Using DFS STack")

        except Exception as e:
            print(f"Test Case {row_num}: ERROR - {e}")
