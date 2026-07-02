# Dashboard
# Tabs:
#   1. Timetable       — select instance + strategy, view the generated timetable
#   2. Performance     — step-count comparison table across all instances + strategies
#   3. Over-Constrained — failure analysis with step counts per strategy
#   4. Search Tree     — Graphviz visualiser loaded from search_logs.json

import os
import json
import streamlit as st

from csp_data import (
    EXAMS, OVERLAPS,
    SMALL_INSTANCE, SMALL_OVERLAPS,
    EXTENDED_INSTANCE, EXTENDED_OVERLAPS,
    OVERCONSTRAINED_INSTANCE,
)
from solver_advanced import S_backtracking, mrv_backtracking, forward_checking
from tree_visualiser import build_graph, build_legend, get_divergence_info

# Page config 

st.set_page_config(page_title="Exam Timetabling CSP", layout="wide")

# Global CSS 

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

html, body, [class*="css"] { font-family: 'Press Start 2P', monospace; }

.stApp { background-color: #060d1a; color: #cfe8ff; }

.main-title {
    font-family: 'Press Start 2P', monospace;
    font-size: 1.8rem; text-align: center; color: #eaf6ff;
    text-shadow: 0 0 8px #2979ff, 0 0 16px #2979ff;
    margin-bottom: 0.4em; line-height: 1.6;
}
.subtitle {
    font-family: 'Press Start 2P', monospace;
    text-align: center; color: #6fb7ff;
    font-size: 0.65rem; margin-bottom: 2em; line-height: 1.8;
}
.panel {
    border: 3px solid #2979ff; border-radius: 10px;
    background-color: #0b1e3a;
    box-shadow: 0 0 20px rgba(41,121,255,0.4);
    padding: 1.5em; margin-bottom: 1.5em;
}
.panel-title {
    font-size: 1rem; color: #6fb7ff;
    border-bottom: 2px solid #2979ff;
    padding-bottom: 0.5em; margin-bottom: 1em;
}
table.timetable {
    width: 100%; border-collapse: collapse;
    font-family: 'Press Start 2P', monospace; font-size: 0.6rem;
}
table.timetable th, table.timetable td {
    border: 2px solid #1e3a5f; padding: 0.8em;
    text-align: center; color: #cfe8ff;
}
table.timetable th { background-color: #102a4c; color: #6fb7ff; }
.exam-cell {
    border-radius: 5px; padding: 0.4em; color: white;
    display: inline-block; margin: 2px;
}
.empty-cell { color: #2a4060; }
.stats-box {
    font-family: 'Press Start 2P', monospace;
    border: 2px solid #2979ff; border-radius: 8px;
    padding: 1em; text-align: center;
    background-color: #0b1e3a; color: #6fb7ff; font-size: 0.7rem;
}
.info-box {
    font-family: 'Press Start 2P', monospace;
    border: 2px solid #e65100; border-radius: 8px;
    padding: 1em; background-color: #1a0e00;
    color: #ff9800; font-size: 0.65rem; line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# Constants 

SLOT_INFO = {
    "T1": ("Monday",    "09:00"),
    "T2": ("Monday",    "14:00"),
    "T3": ("Tuesday",   "09:00"),
    "T4": ("Tuesday",   "14:00"),
    "T5": ("Wednesday", "09:00"),
}
DAYS  = ["Monday", "Tuesday", "Wednesday"]
TIMES = ["09:00", "14:00"]

VENUE_LABELS = {"HallA": "Hall A", "HallB": "Hall B", "Lab1": "Lab 1"}

MODULE_COLORS = {
    "CSC711": "#1565C0", "CSC712": "#00838F", "CSC713": "#6A1B9A",
    "CSC714": "#00695C", "CSC715": "#283593", "MAT701": "#4527A0",
    "STA701": "#0277BD", "PHY701": "#00ACC1",
    "ENG701": "#00897B", "CSC716": "#5E35B1",
}
DEFAULT_COLOR = "#1565C0"

INSTANCE_OPTIONS = ["Smaller Instance", "Full Instance", "Extended Instance"]

INSTANCE_MAP = {
    "Smaller Instance":  (SMALL_INSTANCE,    SMALL_OVERLAPS),
    "Full Instance":     (EXAMS,             OVERLAPS),
    "Extended Instance": (EXTENDED_INSTANCE, EXTENDED_OVERLAPS),
}

STRATEGY_OPTIONS = ["Simple Backtracking", "MRV", "Forward Checking"]

STRATEGY_MAP = {
    "Simple Backtracking": S_backtracking,
    "MRV":                 mrv_backtracking,
    "Forward Checking":    forward_checking,
}

LOG_PATH = "output/search_logs.json"

STRATEGY_KEYS = {
    "Simple Backtracking": "simple_backtracking",
    "MRV":                 "mrv_backtracking",
    "Forward Checking":    "forward_checking",
}
INSTANCE_KEYS = {
    "Smaller Instance":  "small",
    "Full Instance":     "full",
    "Extended Instance": "extended",
}

# Cached solver calls 

@st.cache_data
def run_solver(strategy_name, instance_name):
    """Runs solver for given strategy+instance. Cached so reruns don't re-solve."""
    exams, overlaps = INSTANCE_MAP[instance_name]
    solver_fn = STRATEGY_MAP[strategy_name]
    return solver_fn(exams, overlaps)


@st.cache_data
def run_all_performance():
    """
    Runs all 3 strategies × 3 normal instances.
    Returns list of dicts for st.dataframe().
    """
    rows = []
    for inst_name in INSTANCE_OPTIONS:
        exams, overlaps = INSTANCE_MAP[inst_name]
        row = {"Instance": inst_name}
        for strat_name in STRATEGY_OPTIONS:
            solver_fn = STRATEGY_MAP[strat_name]
            _, steps = solver_fn(exams, overlaps)
            row[strat_name] = steps
        rows.append(row)
    return rows


@st.cache_data
def run_over_constrained():
    """
    Runs all 3 strategies on the over-constrained instance.
    Returns list of dicts: strategy, steps, solved.
    """
    results = []
    for strat_name in STRATEGY_OPTIONS:
        solver_fn = STRATEGY_MAP[strat_name]
        result, steps = solver_fn(
            EXAMS, OVERLAPS,
            time_slots=OVERCONSTRAINED_INSTANCE,
            written_venues=["HallB"],
        )
        results.append({
            "Strategy": strat_name,
            "Steps":    steps,
            "Solved":   result is not None,
            "Status":   "Solution Found" if result is not None else "No Solution",
        })
    return results


@st.cache_data
def load_search_logs():
    """Loads search_logs.json if it exists. Returns empty list otherwise."""
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


# Helper: render timetable grid 

def render_timetable(assignment):
    """Renders the timetable HTML grid. assignment is {exam: (slot, venue)} or None."""
    if assignment is None:
        st.markdown(
            '<p style="color:#ff6b6b;">No valid timetable found for this instance.</p>',
            unsafe_allow_html=True,
        )
        return

    grid = {(day, time): [] for day in DAYS for time in TIMES}
    for exam, (slot, venue) in assignment.items():
        if slot in SLOT_INFO:
            day, time = SLOT_INFO[slot]
            label = f"{exam} ({VENUE_LABELS.get(venue, venue)})"
            grid[(day, time)].append((exam, label))

    html = '<table class="timetable"><tr><th></th>'
    for day in DAYS:
        html += f"<th>{day}</th>"
    html += "</tr>"

    for time in TIMES:
        html += f"<tr><th>{time}</th>"
        for day in DAYS:
            cell = grid[(day, time)]
            if cell:
                content = "".join(
                    f'<span class="exam-cell" style="background-color:'
                    f'{MODULE_COLORS.get(exam, DEFAULT_COLOR)};">{label}</span><br>'
                    for exam, label in cell
                )
            else:
                content = '<span class="empty-cell">--</span>'
            html += f"<td>{content}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


# Page header 

st.markdown('<div class="main-title">Exam Timetabling CSP</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Artificial Intelligence &nbsp;&bull;&nbsp; '
    'Constraint Satisfaction Problem &nbsp;&bull;&nbsp; COS737</div>',
    unsafe_allow_html=True,
)

# Tabs 

tab1, tab2, tab3, tab4 = st.tabs([
    "Timetable",
    "Performance",
    "Over-Constrained",
    "Search Tree",
])

 
# TAB 1 — TIMETABLE

with tab1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">SOLVER CONFIGURATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        selected_instance = st.selectbox("Problem Instance", INSTANCE_OPTIONS, key="tt_instance")
    with col2:
        selected_strategy = st.selectbox("Search Strategy", STRATEGY_OPTIONS, key="tt_strategy")

    st.markdown('</div>', unsafe_allow_html=True)

    assignment, steps = run_solver(selected_strategy, selected_instance)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">TIMETABLE</div>', unsafe_allow_html=True)
    render_timetable(assignment)
    st.markdown('</div>', unsafe_allow_html=True)

    status_text = "SOLVED" if assignment is not None else "FAILED — NO SOLUTION"
    st.markdown(
        f'<div class="stats-box">STATUS: {status_text}'
        f'&nbsp;&nbsp;|&nbsp;&nbsp;STRATEGY: {selected_strategy}'
        f'&nbsp;&nbsp;|&nbsp;&nbsp;SEARCH STEPS: {steps}</div>',
        unsafe_allow_html=True,
    )


# TAB 2 — PERFORMANCE COMPARISON

with tab2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">PERFORMANCE COMPARISON — SEARCH STEPS</div>',
                unsafe_allow_html=True)

    st.markdown(
        "Each cell shows the number of assignment attempts (search steps) "
        "required by each strategy to solve the given problem instance. "
        "Fewer steps indicates more efficient search."
    )

    with st.spinner("Running all strategies across all instances..."):
        perf_rows = run_all_performance()

    st.dataframe(perf_rows, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(
        "**Simple Backtracking** uses a fixed exam ordering with no lookahead. "
        "**MRV** always picks the exam with the fewest remaining valid values, "
        "failing earlier on bad paths. "
        "**Forward Checking** additionally prunes future exam domains after each "
        "assignment, detecting dead ends before reaching them."
    )
    st.markdown('</div>', unsafe_allow_html=True)


# TAB 3 — OVER-CONSTRAINED CASE

with tab3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">OVER-CONSTRAINED INSTANCE ANALYSIS</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="info-box">'
        'CONSTRAINTS APPLIED:<br><br>'
        '&bull; Only time slots T1&ndash;T4 are available (T5 removed)<br>'
        '&bull; All written exams must be scheduled in Hall B only<br><br>'
        'WHY THIS IS INFEASIBLE:<br><br>'
        'Hall B can host at most one exam per time slot. With only 4 slots, '
        'Hall B can accommodate at most 4 written exams. However, the base '
        'instance contains 6 written exams: CSC711, CSC712, CSC714, MAT701, '
        'STA701, and PHY701. No valid timetable can exist.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Strategy Behaviour on Infeasible Instance")

    with st.spinner("Running over-constrained case..."):
        oc_results = run_over_constrained()

    st.dataframe(oc_results, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(
        "All strategies report **No Solution**. "
        "The number of steps before failure reveals how efficiently each strategy "
        "detects infeasibility. A smarter strategy will exhaust the search space "
        "faster by pruning dead branches early."
    )
    st.markdown('</div>', unsafe_allow_html=True)


# TAB 4 — SEARCH TREE VISUALISER

with tab4:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">SEARCH TREE VISUALISER</div>', unsafe_allow_html=True)

    logs = load_search_logs()

    if not logs:
        st.warning(
            "search_logs.json not found. Run `python generate_logs.py` first "
            "to generate the search tree data."
        )
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            tree_instance = st.selectbox("Problem Instance", INSTANCE_OPTIONS, key="tree_instance")
        with col_b:
            tree_strategy = st.selectbox("Search Strategy", STRATEGY_OPTIONS, key="tree_strategy")

        inst_key  = INSTANCE_KEYS[tree_instance]
        strat_key = STRATEGY_KEYS[tree_strategy]

        matched = next(
            (e for e in logs if e["strategy"] == strat_key and e["instance"] == inst_key),
            None,
        )

        if matched is None:
            st.error(
                f"No log found for {tree_strategy} on {tree_instance}. "
                "Re-run generate_logs.py."
            )
        else:
            nodes  = matched["nodes"]
            solved = matched["solved"]
            total  = matched["total_steps"]

            status_label = "SOLVED" if solved else "NO SOLUTION"
            st.markdown(
                f'<div class="stats-box">'
                f'STRATEGY: {tree_strategy}&nbsp;&nbsp;|&nbsp;&nbsp;'
                f'INSTANCE: {tree_instance}&nbsp;&nbsp;|&nbsp;&nbsp;'
                f'TOTAL STEPS: {total}&nbsp;&nbsp;|&nbsp;&nbsp;'
                f'STATUS: {status_label}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")

            if len(nodes) > 10:
                max_display = st.slider(
                    "Max nodes to display",
                    min_value=10,
                    max_value=min(300, len(nodes)),
                    value=min(120, len(nodes)),
                    step=10,
                    help="Large trees are trimmed for readability. "
                         "Use the Smaller Instance for a full view.",
                )
            else:
                max_display = len(nodes)
                st.caption(f"Showing all {len(nodes)} nodes (tree is small enough to display in full).")

            graph = build_graph(
                nodes,
                title=f"{tree_strategy} — {tree_instance}",
                max_nodes=max_display,
            )
            st.graphviz_chart(graph.source)

            st.markdown("#### Node Colour Legend")
            legend = build_legend()
            st.graphviz_chart(legend.source)

        # Divergence analysis 
        st.markdown("---")
        st.markdown("#### Strategy Divergence Analysis")
        st.markdown(
            "Compare Simple Backtracking against MRV to find the first point "
            "where the two strategies make a different choice."
        )

        div_instance = st.selectbox(
            "Instance for divergence analysis",
            INSTANCE_OPTIONS,
            key="div_instance",
        )
        div_inst_key = INSTANCE_KEYS[div_instance]

        basic_log = next(
            (e for e in logs
             if e["strategy"] == "simple_backtracking" and e["instance"] == div_inst_key),
            None,
        )
        mrv_log = next(
            (e for e in logs
             if e["strategy"] == "mrv_backtracking" and e["instance"] == div_inst_key),
            None,
        )

        if basic_log and mrv_log:
            divergence = get_divergence_info(basic_log["nodes"], mrv_log["nodes"])
            if divergence:
                st.success(f"Divergence found at step {divergence['step']}:")
                st.markdown(
                    f"**Simple Backtracking:** {divergence['basic_exam']} = "
                    f"{divergence['basic_value']} → {divergence['basic_status']}"
                )
                st.markdown(
                    f"**MRV:** {divergence['advanced_exam']} = "
                    f"{divergence['advanced_value']} → {divergence['advanced_status']}"
                )
                st.info(divergence["explanation"])
            else:
                st.info(
                    "No divergence found — both strategies made identical choices "
                    "on this instance."
                )
        else:
            st.warning("Run generate_logs.py first to enable divergence analysis.")

    st.markdown('</div>', unsafe_allow_html=True)

# References:
# [1] Streamlit Inc., "Streamlit documentation," 2026. [Online].
#     Available: https://docs.streamlit.io/
# [2] Streamlit Inc., "Get started with Streamlit," 2026. [Online].
#     Available: https://docs.streamlit.io/get-started
# [3] J. Ellson, E. R. Gansner, L. Koutsofios, S. C. North, and G. Woodhull,
#     "Graphviz — open source graph drawing tools," Lecture Notes in Computer
#     Science, vol. 2265, pp. 483-484, Springer, 2002.
# [4] xflr6, "Graphviz — simple Python interface for Graphviz," Read the Docs,
#     2026. [Online]. Available: https://graphviz.readthedocs.io/en/stable/manual.html
# [5] Python Software Foundation, "json — JSON encoder and decoder,"
#     Python 3.x Documentation. [Online]. Available:
#     https://docs.python.org/3/library/json.html
#claude for debugging and assisstance with the dashboard design and layout, and for help with the streamlit code and styling.