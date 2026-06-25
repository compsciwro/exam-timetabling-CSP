# utils.py
# Shared helper functions for writing solver output to text files.

import os


def write_timetable_to_file(assignment, step_count, filepath="output/timetable.txt"):
    """
    Writes the final exam timetable and search step count to a text file,
    matching the output format shown in the assignment brief:

        CSC711 -> T1, Hall A
        CSC712 -> T2, Hall A
        ...
        Search steps: 34
    """
    # Make sure the output folder exists before writing into it
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        if assignment is None:
            f.write("No valid timetable found.\n")
        else:
            for exam, (time, venue) in assignment.items():
                f.write(f"{exam} -> {time}, {venue}\n")

        f.write(f"\nSearch steps: {step_count}\n")

    print(f"Timetable written to {filepath}")