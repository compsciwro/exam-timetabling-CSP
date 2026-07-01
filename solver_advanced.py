from csp_data import(
    EXAMS, OVERLAPS, TIME_SLOTS, SMALL_INSTANCE, SMALL_OVERLAPS,
    EXTENDED_INSTANCE, EXTENDED_OVERLAPS, OVERCONSTRAINED_INSTANCE, generate_domains
)
from solver_basic import is_valid

#The below simple backtracking function is adpated from Russell and Norvig's textbooks pseudocode for backtracking search.
# as well as the theory for the complex search strategies

#Simple Search Strategy: Simple Backtracking
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

#Complex Search Strategy 1: Backtracking with MRV heuristic + Degree heuristic
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

    #calls the above function to find a solution
    result = _mrv_backtrack_hlp(assigned, domains, counter, overlaps, log_fn)
    return result, counter[0]

#Complex Search Strategy 2: Backtracking with Forward Checking
def _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps, log_fn=None):
     #if every exam has an assigned value, the timetable is complete
    if len(assigned) == len(examOrder):
        return assigned

    #gets the next exam in line thats not been assigned.
    examCurrent = examOrder[len(assigned)]

    #try every possible value in the current exam's domains
    for value in list(currentDomains[examCurrent]):
        counter[0] += 1

        #uses is_valid function from solver_basic to check if the chosen value has any clashes
        if is_valid(examCurrent, value, assigned, overlaps):
            assigned[examCurrent] = value
            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "success"})

            savedDomains = {} #backup of the domains so that we can comeback after pruning 
            DeadEnd = False #tracks when an exam runs out of values

            #goes through every unassigned exam 
            for other in [exam for exam in examOrder if exam not in assigned]:
                savedDomains[other] = list(currentDomains[other]) #saves current domain for backtracking purposes
                #keeps legal values only
                currentDomains[other] = [v for v in currentDomains[other] if is_valid(other, v, assigned, overlaps)]

                #if this exam has no legal options left, mark this value as a deadend to cancel the recursion
                if not currentDomains[other]:
                    DeadEnd = True
                    break
            #only go further if exam domain is not empty
            if not DeadEnd:
                result = _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps, log_fn)
                if result is not None:
                    return result #solution found

            if log_fn:
                log_fn({"exam": examCurrent, "value": str(value),
                        "step": counter[0], "status": "backtrack"})
            #put the saved domains back so a new value can start from the prevosuly saved domains
            for other, domain in savedDomains.items():
                currentDomains[other] = domain
            #delete the exam's current assignment
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

    #calls the above function to find a solution
    result = _Forward_checking_hlp(assigned, currentDomains, examOrder, counter, overlaps, log_fn)
    return result, counter[0]

#used to help code and for understanding::
#the russell and norvig textbook
#https://github.com/aimacode/aima-python/blob/master/aima/csp.py
#https://simpleai.readthedocs.io/en/latest/_modules/simpleai/search/csp.html
#https://www.cs.cmu.edu/~15281/coursenotes/constraints/
#Claude for debugging and to help understand MRV/forward checking
