from csp_data import OVERLAPS as DefaultOL
from csp_data import EXAMS, generate_domains
from utils import write_timetable_to_file
#

def is_valid(exam_name, candidate, assignment, overlaps = None):
    # Checks whether assigning a time and venue to an exam breaks any constraints
    overlaps = overlaps if overlaps is not None else DefaultOL
    candidate_time, candidate_venue = candidate

    for other_exam, other_value in assignment.items():
        other_time, other_venue = other_value

        # C3-C10: overlap/clash constraints
        # Check both orderings since OVERLAPS stores pairs once
        pair_clashes = (exam_name, other_exam) in overlaps or (other_exam, exam_name) in overlaps
        if pair_clashes and candidate_time == other_time:
            return False

        # C11: venue clash - same time slot, same venue not allowed
        if candidate_time == other_time and candidate_venue == other_venue:
            return False

    return True


def backtrack(assignment, domains, exam_order, step_counter):
    # Uses recursive backtracking to assign a valid time and venue to each exam while counting the search steps.

    # Base case: every exam has been assigned -> solution found
    if len(assignment) == len(exam_order):
        return assignment

    # Pick the next unassigned exam (fixed order, since this is the
    # SIMPLE backtracking strategy - no MRV/heuristics here, that's Raeez's job)
    current_exam = exam_order[len(assignment)]

    for candidate in domains[current_exam]:
        step_counter[0] += 1  # every attempt counts, success or fail

        if is_valid(current_exam, candidate, assignment):
            assignment[current_exam] = candidate  # try this value

            result = backtrack(assignment, domains, exam_order, step_counter)
            if result is not None:
                return result  # solution found further down - bubble up

            del assignment[current_exam]  # backtrack: undo and try next value

    return None  # no value worked for this exam - trigger backtracking above

def solve():
    # Runs the basic backtracking solver and returns the timetable and total search steps.
    domains = generate_domains()
    exam_order = list(EXAMS.keys())
    assignment = {}
    step_counter = [0]

    result = backtrack(assignment, domains, exam_order, step_counter)

    return result, step_counter[0]


# Quick manual test when running this file directly
if __name__ == "__main__":
    final_assignment, steps = solve()

    if final_assignment is None:
        print("No valid timetable found.")
    else:
        print("Valid timetable found:")
        for exam, (time, venue) in final_assignment.items():
            print(f"  {exam} -> {time}, {venue}")

    print(f"\nSearch steps: {steps}")

    write_timetable_to_file(final_assignment, steps)