# generate_logs.py
# Run this script once to populate output/search_logs.json.
# The dashboard reads from this file to display search trees.
# Safe to re-run — it overwrites previous entries for the same strategy+instance.

from csp_data import (EXAMS, OVERLAPS, SMALL_INSTANCE, SMALL_OVERLAPS,
                      EXTENDED_INSTANCE, EXTENDED_OVERLAPS,
                      OVERCONSTRAINED_INSTANCE)
from solver_advanced import S_backtracking, mrv_backtracking, forward_checking
from tree_logger import TreeLogger

LOG_PATH = "output/search_logs.json"

RUNS = [
    # (strategy_label, solver_fn, instance_label, exams, overlaps, time_slots, written_venues)
    ("simple_backtracking", S_backtracking,   "small",            SMALL_INSTANCE,    SMALL_OVERLAPS,   None,                     None),
    ("simple_backtracking", S_backtracking,   "full",             EXAMS,             OVERLAPS,          None,                     None),
    ("simple_backtracking", S_backtracking,   "extended",         EXTENDED_INSTANCE, EXTENDED_OVERLAPS, None,                     None),
    ("simple_backtracking", S_backtracking,   "over_constrained", EXAMS,             OVERLAPS,          OVERCONSTRAINED_INSTANCE, ["HallB"]),
    ("mrv_backtracking",    mrv_backtracking, "small",            SMALL_INSTANCE,    SMALL_OVERLAPS,   None,                     None),
    ("mrv_backtracking",    mrv_backtracking, "full",             EXAMS,             OVERLAPS,          None,                     None),
    ("mrv_backtracking",    mrv_backtracking, "extended",         EXTENDED_INSTANCE, EXTENDED_OVERLAPS, None,                     None),
    ("mrv_backtracking",    mrv_backtracking, "over_constrained", EXAMS,             OVERLAPS,          OVERCONSTRAINED_INSTANCE, ["HallB"]),
    ("forward_checking",    forward_checking, "small",            SMALL_INSTANCE,    SMALL_OVERLAPS,   None,                     None),
    ("forward_checking",    forward_checking, "full",             EXAMS,             OVERLAPS,          None,                     None),
    ("forward_checking",    forward_checking, "extended",         EXTENDED_INSTANCE, EXTENDED_OVERLAPS, None,                     None),
    ("forward_checking",    forward_checking, "over_constrained", EXAMS,             OVERLAPS,          OVERCONSTRAINED_INSTANCE, ["HallB"]),
]

if __name__ == "__main__":
    print("Generating search logs...\n")
    for strategy, solver_fn, instance, exams, overlaps, time_slots, written_venues in RUNS:
        logger = TreeLogger()
        result, steps = solver_fn(
            exams, overlaps,
            time_slots=time_slots,
            written_venues=written_venues,
            log_fn=logger.log,
        )
        logger.save(strategy, instance, result is not None, steps, path=LOG_PATH)

    print(f"\nDone. All 12 runs saved to {LOG_PATH}")
# References:
# [1] S. J. Russell and P. Norvig, Artificial Intelligence: A Modern Approach,
#     4th ed. Pearson, 2021. Ch. 6 — Search strategies used across all
#     instances: backtracking, MRV, and forward checking.
# [2] Python Software Foundation, "json — JSON encoder and decoder,"
#     Python 3.x Documentation. [Online]. Available:
#     https://docs.python.org/3/library/json.html
# [3] Python Software Foundation, "os.path — common pathname manipulations,"
#     Python 3.x Documentation. [Online]. Available:
#     https://docs.python.org/3/library/os.path.html