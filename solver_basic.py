from csp_data import OVERLAPS
from csp_data import EXAMS, generate_domains
from utils import write_timetable_to_file


def is_valid(exam_name, candidate, assignment):
    """
    Checks whether assigning `candidate` (a (time, venue) tuple) to
    `exam_name` violates any constraint, given the exams already
    assigned in `assignment` (a dict: exam_name -> (time, venue)).
    """
    candidate_time, candidate_venue = candidate

    for other_exam, other_value in assignment.items():
        other_time, other_venue = other_value

        # C3-C10: overlap/clash constraints
        # Check both orderings since OVERLAPS stores pairs once
        pair_clashes = (exam_name, other_exam) in OVERLAPS or (other_exam, exam_name) in OVERLAPS
        if pair_clashes and candidate_time == other_time:
            return False

        # C11: venue clash - same time slot, same venue not allowed
        if candidate_time == other_time and candidate_venue == other_venue:
            return False

    return True


def backtrack(assignment, domains, exam_order, step_counter):
    """
    Recursive backtracking search.

    assignment: dict of exam_name -> (time, venue) assigned so far
    domains: dict of exam_name -> list of valid (time, venue) options
    exam_order: list of exam names, defining the fixed assignment order
    step_counter: a list with one element [count], used so the count
                   persists across recursive calls (mutable trick)
    """

    # Base case: every exam has been assigned -> solution found
    if len(assignment) == len(exam_order):
        return assignment

    # Pick the next unassigned exam (fixed order, since this is the
    # SIMPLE strategy - no MRV/heuristics here, that's Member 2's job)
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
    """
    Sets up the CSP and runs basic backtracking search.

    Returns a tuple: (assignment, step_count)
        assignment: dict of exam_name -> (time, venue), or None if no
                     solution exists
        step_count: total number of assignment attempts made
    """
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