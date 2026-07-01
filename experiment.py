from csp_data import(
    EXAMS, OVERLAPS, SMALL_INSTANCE, SMALL_OVERLAPS,
    EXTENDED_INSTANCE, EXTENDED_OVERLAPS, OVERCONSTRAINED_INSTANCE,
)
import os
from solver_advanced import S_backtracking, mrv_backtracking, forward_checking

#store all the problem scenarios  and search strategies in a list of tuples
SCENARIOS = [ ("Small", SMALL_INSTANCE, SMALL_OVERLAPS, None, None),
              ("Full", EXAMS, OVERLAPS, None, None),
              ("Extended", EXTENDED_INSTANCE, EXTENDED_OVERLAPS, None, None),
              ("OverConstrained",EXAMS, OVERLAPS, OVERCONSTRAINED_INSTANCE, ["HallB"] )] #overconstrained scenario using limited time slots and venue hallB

SEARCH_STRATS = [("Simple Backtracking", S_backtracking),
                 ("MRV (Minimum Remaining Values)", mrv_backtracking),
                 ("Forward Checking", forward_checking)]


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True) #created results folder if it doesnt exist
    #the below code creates a table of the results (different search strats)
    header = f"{"Scenario":<20} {"Simple Backtracking":>22} {"BT + MRV with Degree":>22} {"BT + Forward Checking":>22}"
    div = "-" * len(header)
    print(header)
    print(div)
    lines = [header, div]

for name, exams, overlaps, time_slots, written_venues in SCENARIOS: #loops through each scenario
    cols = [] #creates a list to store the results for each search strategy
    #below loops through each search strategy 
    for _, fn in SEARCH_STRATS:
        results, steps = fn(exams, overlaps, time_slots=time_slots, written_venues=written_venues)
        condition = "Solution Found" if results is not None else "No Solution" #checks if a solution was found or not
        cols.append(f"{steps} ({condition})") #combines the number of steps and if there was a solution and adds it to the table cols list
    row = f"{name:<20} {cols[0]:>22} {cols[1]:>22} {cols[2]:>22}"
    print(row)
    lines.append(row)

#below code writes the results to a text file in the results folder
with open("results/results.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("\nResults written to results.txt")

#used to help code :
#claude for debugging and assisstance in understading how to set up the for loops
#https://www.w3schools.com/python/python_tuples.asp
#https://www.geeksforgeeks.org/python/writing-to-file-in-python/
#https://www.geeksforgeeks.org/python/create-a-directory-in-python/