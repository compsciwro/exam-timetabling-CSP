from csp_data import(
    EXAMS, OVERLAPS, SMALL_INSTANCE, SMALL_OVERLAPS,
    EXTENDED_INSTANCE, EXTENDED_OVERLAPS, OVERCONSTRAINED_INSTANCE,
)
import os
from solver_advanced import S_backtracking, mrv_backtracking, forward_checking

SCENARIOS = [ ("Small Instance", SMALL_INSTANCE, SMALL_OVERLAPS, None, None),
              ("Full Instance", EXAMS, OVERLAPS, None, None),
              ("Extended Instance", EXTENDED_INSTANCE, EXTENDED_OVERLAPS, None, None),
              ("Over-Constrained Instance",EXAMS, OVERLAPS, OVERCONSTRAINED_INSTANCE, ["HallB"] )]

SEARCH_STRATS = [("Simple Backtracking", S_backtracking),
                 ("MRV (Minimum Remaining Values)", mrv_backtracking),
                 ("Forward Checking", forward_checking)]

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    
    header = f"{"Scenario":<20} {"Simple Backtracking": >12} {"MRV": >12} {"Forward Checking": >12}"
    div = "-" * len(header)
    print(header)
    print(div)
    lines = [header,div]

for name, exams, overlaps, time_slots, written_venues in SCENARIOS:
    cols = []
    for _, fn in SEARCH_STRATS:
        results, steps = fn(exams, overlaps, time_slots=time_slots, written_venues=written_venues)
        condition = "Solution Found" if results is not None else "No Solution"
        cols.append(f"{steps} ({condition})")
    row = f"{name:<20} {cols[0]:>12} {cols[1]:>12} {cols[2]:>20}"
    print(row)
    lines.append(row)

with open("results/results.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
print("\nResults written to results.txt")