from csp_data import(
    EXAMS, OVERLAPS, TIME_SLOTS, SMALL_INSTANCE, SMALL_OVERLAPS,
    EXTENDED_INSTANCE, EXTENDED_OVERLAPS, OVERCONSTRAINED_INSTANCE, generate_domains
)
from solver_basic import is_valid


def _backtrack_hlp(assigned, domains, examOrder, counter, overlaps):
    if len(assigned) == len(examOrder):
        return assigned
    
    examCurrent = examOrder[len(assigned)]

    for value in domains[examCurrent]:
        counter[0] += 1

        if is_valid(examCurrent, value, assigned, overlaps):
            assigned[examCurrent] = value
            result = _backtrack_hlp(assigned, domains, examOrder, counter, overlaps)
            if result is not None:
                return result
            del assigned[examCurrent]
    
    return None

def S_backtracking(exams, overlaps, time_slots = None, written_venues = None): #check var names before submission

    assigned = {}
    domains = generate_domains(exams, time_slots = time_slots, written_venues = written_venues)
    examOrder = list(exams.keys()) #COMEBACK AND CHECK BEFORE SUBMISSION
    counter = [0]

    result = _backtrack_hlp(assigned, domains, examOrder, counter, overlaps)
    return result, counter[0]

def _mrv_backtrack_hlp(assigned, domains, counter, overlaps):
    if len(assigned) == len(domains):
        return assigned
    #check before submission
    unassigned = [exam for exam in domains if exam not in assigned]
    examCurrent = min(unassigned, key=lambda exam: (
        sum(1 for value in domains[exam] if is_valid(exam, value, assigned, overlaps)),
        -sum(1 for other in unassigned if other != exam and ((exam, other) in overlaps or (other, exam) in overlaps))
    ))

    for value in domains[examCurrent]:
        counter[0] += 1
        #rewrite
        if is_valid(examCurrent, value, assigned, overlaps):
            assigned[examCurrent] = value
            result = _mrv_backtrack_hlp(assigned, domains, counter, overlaps)
            if result is not None:
                return result
            del assigned[examCurrent]

    return None
#rewrite
def mrv_backtracking(exams, overlaps, time_slots = None, written_venues = None):
    assigned = {}
    domains = generate_domains(exams, time_slots = time_slots, written_venues = written_venues)
    counter = [0]

    result = _mrv_backtrack_hlp(assigned, domains, counter, overlaps)
    return result, counter[0]

#redo entire forward checking function, make sure to check variable names before submission
def _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps):
    if len(assigned) == len(examOrder):
        return assigned

    examCurrent = examOrder[len(assigned)]

    for value in list(currentDomains[examCurrent]):
        counter[0] += 1

        if is_valid(examCurrent, value, assigned, overlaps):
            assigned[examCurrent] = value

            savedDomains = {}
            DeadEnd = False
            for other in [exam for exam in examOrder if exam not in assigned]:
                savedDomains[other] = list(currentDomains[other])
                currentDomains[other] = [v for v in currentDomains[other] if is_valid(other, v, assigned, overlaps)]

                if not currentDomains[other]:
                    DeadEnd = True
                    break

            if not DeadEnd:
                result = _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps)
                if result is not None:
                    return result
                
            for other, domain in savedDomains.items():
                currentDomains[other] = domain

            del assigned[examCurrent]

    return None

def forward_checking(exams, overlaps, time_slots = None, written_venues = None):
    assigned = {}
    currentDomains = generate_domains(exams, time_slots = time_slots, written_venues = written_venues)
    examOrder = list(exams.keys())
    counter = [0]

    result = _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps)
    return result, counter[0]

if __name__ == "__main__":
    print("=== Simple Backtracking ===")
    result, steps = S_backtracking(EXAMS, OVERLAPS)
    if result is None:
        print("No solution found.")
    else:
        for exam, (time, venue) in result.items():
            print(f"  {exam} -> {time}, {venue}")
    print(f"Search steps: {steps}")
    print(f"Expected: 27 | Match: {steps == 27}")

    print("\n=== MRV Backtracking ===")
    result, steps = mrv_backtracking(EXAMS, OVERLAPS)
    if result is None:
        print("No solution found.")
    else:
        for exam, (time, venue) in result.items():
            print(f"  {exam} -> {time}, {venue}")
    print(f"Search steps: {steps}")

    print("\n=== Forward Checking ===")
    result, steps = forward_checking(EXAMS, OVERLAPS)
    if result is None:
        print("No solution found.")
    else:
        for exam, (time, venue) in result.items():
            print(f"  {exam} -> {time}, {venue}")
    print(f"Search steps: {steps}")