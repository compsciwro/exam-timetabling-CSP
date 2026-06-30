from csp_data import(
    EXAMS, OVERLAPS, TIME_SLOTS, SMALL_INSTANCE, SMALL_OVERLAPS,
    EXTENDED_INSTANCE, EXTENDED_OVERLAPS, OVERCONSTRAINED_INSTANCE, generate_domains
)
from solver_basic import is_valid

#Simple Search Strategy: Simple Backtracking
#The below simple backtracking function is adpated from Russell and Norvig's textbooks pseudocode for backtracking search.
#assigned parameter: dictionary of assigned exams and their values
#domains parameter: dictionary of all exams and their possible values
#examOrder parameter: list of exams in a fixed order
#overlap parameter: list of overlapping exams

def _backtrack_hlp(assigned, domains, examOrder, counter, overlaps, log_fn=None):
    #if every exam has an assigned value, the timetable is complete
    if len(assigned) == len(examOrder):
        return assigned
    
    #gets the next exam in line thats not been assigned. 
    examCurrent = examOrder[len(assigned)]

    #try every possible value in the current exam's domains
    for value in domains[examCurrent]:
        counter[0] += 1

        #uses is_valid function from solver_basic to check if the chosen value has any clashes
        if is_valid(examCurrent, value, assigned, overlaps):
            #if there are no clashes,then the current exam is assigned to the above value
            assigned[examCurrent] = value
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "success"})
            #by using recursion, the backtrack_hlp function is called againt to assign the next exam from the fixed order
            result = _backtrack_hlp(assigned, domains, examOrder, counter, overlaps, log_fn)
            #if a full solution is found, its returned
            if result is not None:
                return result
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "backtrack"})
            #if a full solution is not found, unassign current exam because this value didnt work and try next one
            del assigned[examCurrent]
        else:
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "fail"})
                
    return None

#this function sets up the problem and calls the recursive backtrakc search algorithm from above
#time_slots parameter: this is the slots available for the exams to be scheduled in.
#written_venues parameter: this is the venues written exams can be used in.
def S_backtracking(exams, overlaps, time_slots=None, written_venues=None, log_fn=None): #check var names before submission

    assigned = {} #empty timetable, no exams have been assigned yet
    domains = generate_domains(exams, time_slots=time_slots, written_venues=written_venues) #builds domain for each exam
    examOrder = list(exams.keys()) #exam names put into a list in a fixed order
    counter = [0]

    #calls the recursive backtracking function to find a solution
    result = _backtrack_hlp(assigned, domains, examOrder, counter, overlaps, log_fn)
    return result, counter[0]

#Complex Search Strategy 1: MRV with Degree heuristic + BT
def _mrv_backtrack_hlp(assigned, domains, counter, overlaps, log_fn=None):
    #if every exam has an assigned value, the timetable is complete
    if len(assigned) == len(domains):
        return assigned
    
    #build a list of exams that have not been assigened yet
    unassigned = [exam for exam in domains if exam not in assigned]
    examCurrent = None
    BestVal = 0
    BestDegree = 0

    #loop thru every unassigned exam
    for exam in unassigned:
        ValidVal = 0
        degree = 0

        #MRV Heuristic : count how many valid values for this exam
        for value in domains[exam]:
            if is_valid(exam, value, assigned, overlaps):
                ValidVal += 1
        
        #Degree heuristic: check how many constraints this exam has 
        for neighbor in unassigned:
            if neighbor != exam and ((exam, neighbor) in overlaps or (neighbor, exam) in overlaps):
                degree += 1

        if examCurrent is None or ValidVal < BestVal or (ValidVal == BestVal and degree > BestDegree):
            examCurrent = exam
            BestVal = ValidVal
            BestDegree = degree
        
    #same as the backtrack_hlp function, but instead of using a fixed order,
    #it uses the MRV heuristic plus the degree heuristic to choose the next exam to assign
    for value in domains[examCurrent]:
        counter[0] += 1
        if is_valid(examCurrent, value, assigned, overlaps):
            assigned[examCurrent] = value
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "success"})
            result = _mrv_backtrack_hlp(assigned, domains, counter, overlaps, log_fn)
            if result is not None:
                return result
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "backtrack"})
            del assigned[examCurrent]
        else:
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "fail"})

    return None

#this function sets up the problem and calls the recursive backtrakc search algorithm from above
def mrv_backtracking(exams, overlaps, time_slots=None, written_venues=None, log_fn=None):
    assigned = {}
    domains = generate_domains(exams, time_slots=time_slots, written_venues=written_venues)
    counter = [0]

    result = _mrv_backtrack_hlp(assigned, domains, counter, overlaps, log_fn)
    return result, counter[0]

#Complex Search Strategy 2: Forward Checking
def _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps, log_fn=None):
     #if every exam has an assigned value, the timetable is complete
    if len(assigned) == len(examOrder):
        return assigned

    #gets the next exam in line thats not been assigned.
    examCurrent = examOrder[len(assigned)]

    
    for value in list(currentDomains[examCurrent]):
        counter[0] += 1

        if is_valid(examCurrent, value, assigned, overlaps):
            assigned[examCurrent] = value
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "success"})

            savedDomains = {}
            DeadEnd = False
            for other in [exam for exam in examOrder if exam not in assigned]:
                savedDomains[other] = list(currentDomains[other])
                currentDomains[other] = [v for v in currentDomains[other] if is_valid(other, v, assigned, overlaps)]

                if not currentDomains[other]:
                    DeadEnd = True
                    break

            if not DeadEnd:
                result = _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps, log_fn)
                if result is not None:
                    return result

            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "backtrack"})
            for other, domain in savedDomains.items():
                currentDomains[other] = domain

            del assigned[examCurrent]
        else:
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "fail"})

    return None

#this function sets up the problem and calls the recursive backtrakc search algorithm from above
def forward_checking(exams, overlaps, time_slots=None, written_venues=None, log_fn=None):
    assigned = {}
    currentDomains = generate_domains(exams, time_slots=time_slots, written_venues=written_venues)
    examOrder = list(exams.keys())
    counter = [0]

    result = _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps, log_fn)
    return result, counter[0]
