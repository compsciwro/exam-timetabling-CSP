# csp_data.py
# CSP data model for the Exam Timetabling problem (COS737)
# Stores exams, venues, time slots, overlap pairs, and generates
# valid domains for each exam (with unary constraints C1, C2 pre-applied).

TIME_SLOTS = ["T1", "T2", "T3", "T4", "T5"]

VENUES = {
    "HallA": {"capacity": 120},
    "HallB": {"capacity": 80},
    "Lab1": {"capacity": 40},
}

EXAMS = {
    "CSC711": {"student_count": 70, "type": "Written"},
    "CSC712": {"student_count": 55, "type": "Written"},
    "CSC713": {"student_count": 35, "type": "Computer based"},
    "CSC714": {"student_count": 40, "type": "Written"},
    "CSC715": {"student_count": 25, "type": "Computer based"},
    "MAT701": {"student_count": 60, "type": "Written"},
    "STA701": {"student_count": 45, "type": "Written"},
    "PHY701": {"student_count": 30, "type": "Written"},
}

OVERLAPS = [
    ("CSC711", "CSC712"),
    ("CSC711", "MAT701"),
    ("CSC712", "STA701"),
    ("CSC713", "CSC714"),
    ("CSC714", "MAT701"),
    ("CSC715", "PHY701"),
    ("MAT701", "STA701"),
    ("STA701", "PHY701"),
]


def generate_domains():
    """
    Builds the domain of valid (TimeSlot, Venue) pairs for every exam.

    Applies the two unary constraints directly during construction,
    so invalid pairs never appear in the domain:
        C1: if exam.type == "Computer based" -> venue must be Lab1
        C2: exam.student_count <= venue.capacity
    """
    domains = {}

    for exam_name, exam_info in EXAMS.items():
        valid_pairs = []

        for time_slot in TIME_SLOTS:
            for venue_name, venue_info in VENUES.items():

                # C1: computer-based exams can only go in Lab1
                if exam_info["type"] == "Computer based" and venue_name != "Lab1":
                    continue

                # C2: venue must have enough capacity
                if exam_info["student_count"] > venue_info["capacity"]:
                    continue

                valid_pairs.append((time_slot, venue_name))

        domains[exam_name] = valid_pairs

    return domains


# Quick manual test when running this file directly
if __name__ == "__main__":
    domains = generate_domains()
    for exam, values in domains.items():
        print(f"{exam}: {len(values)} valid options -> {values}")