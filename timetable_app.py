# timetable_app.py
# Streamlit GUI displaying the generated exam timetable.
# Themed to match the project's pixel-art blue dashboard style.
# (Member 3 builds a separate app for the search tree visualiser.)

import streamlit as st
from solver_basic import solve

st.set_page_config(page_title="Exam Timetabling CSP", layout="wide")

# ---------- Pixel-art blue theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

html, body, [class*="css"]  {
    font-family: 'Press Start 2P', monospace;
}

.stApp {
    background-color: #060d1a;
    color: #cfe8ff;
}

.main-title {
    font-family: 'Press Start 2P', monospace;
    font-size: 1.8rem;
    text-align: center;
    color: #eaf6ff;
    text-shadow: 0 0 8px #2979ff, 0 0 16px #2979ff;
    margin-bottom: 0.4em;
    line-height: 1.6;
}

.subtitle {
    font-family: 'Press Start 2P', monospace;
    text-align: center;
    color: #6fb7ff;
    font-size: 0.65rem;
    margin-bottom: 2em;
    line-height: 1.8;
}

.panel {
    border: 3px solid #2979ff;
    border-radius: 10px;
    background-color: #0b1e3a;
    box-shadow: 0 0 20px rgba(41,121,255,0.4);
    padding: 1.5em;
    margin-bottom: 1.5em;
}

.panel-title {
    font-size: 1rem;
    color: #6fb7ff;
    border-bottom: 2px solid #2979ff;
    padding-bottom: 0.5em;
    margin-bottom: 1em;
}

table.timetable {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Press Start 2P', monospace;
    font-size: 0.6rem;
}

table.timetable th, table.timetable td {
    border: 2px solid #1e3a5f;
    padding: 0.8em;
    text-align: center;
    color: #cfe8ff;
}

table.timetable th {
    background-color: #102a4c;
    color: #6fb7ff;
}

.exam-cell {
    border-radius: 5px;
    padding: 0.4em;
    color: white;
    display: inline-block;
    margin: 2px;
}

.empty-cell {
    color: #2a4060;
}

.stats-box {
    font-family: 'Press Start 2P', monospace;
    border: 2px solid #2979ff;
    border-radius: 8px;
    padding: 1em;
    text-align: center;
    background-color: #0b1e3a;
    color: #6fb7ff;
    font-size: 0.7rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="main-title">Exam Timetabling CSP</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Artificial Intelligence &nbsp;\u2022&nbsp; '
    'Constraint Satisfaction Problem &nbsp;\u2022&nbsp; Streamlit Dashboard</div>',
    unsafe_allow_html=True,
)

# ---------- Time slot -> Day/Time mapping (from the assignment brief) ----------
SLOT_INFO = {
    "T1": ("Monday", "09:00"),
    "T2": ("Monday", "14:00"),
    "T3": ("Tuesday", "09:00"),
    "T4": ("Tuesday", "14:00"),
    "T5": ("Wednesday", "09:00"),
}

DAYS = ["Monday", "Tuesday", "Wednesday"]
TIMES = ["09:00", "14:00"]

VENUE_LABELS = {
    "HallA": "Hall A",
    "HallB": "Hall B",
    "Lab1": "Lab 1",
}

# ---------- Per-module colour palette ----------
# Cool-toned palette (teals, purples, indigos, cyans) chosen to stay
# complementary to the navy/blue dashboard theme rather than clash with it.
MODULE_COLORS = {
    "CSC711": "#1565C0",  # blue
    "CSC712": "#00838F",  # teal
    "CSC713": "#6A1B9A",  # purple
    "CSC714": "#00695C",  # deep teal/green
    "CSC715": "#283593",  # indigo
    "MAT701": "#4527A0",  # deep purple
    "STA701": "#0277BD",  # light blue
    "PHY701": "#00ACC1",  # cyan
}

DEFAULT_MODULE_COLOR = "#1565C0"  # fallback for any exam not in the palette

# ---------- Run the solver ----------
assignment, steps = solve()

# ---------- Build lookup: (day, time) -> list of "exam (venue)" strings ----------
grid = {(day, time): [] for day in DAYS for time in TIMES}

if assignment:
    for exam, (slot, venue) in assignment.items():
        day, time = SLOT_INFO[slot]
        label = f"{exam} ({VENUE_LABELS[venue]})"
        grid[(day, time)].append((exam, label))

# ---------- Render timetable panel ----------
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">TIMETABLE</div>', unsafe_allow_html=True)

if assignment is None:
    st.markdown(
        '<p style="color:#ff6b6b;">No valid timetable found for this instance.</p>',
        unsafe_allow_html=True,
    )
else:
    table_html = '<table class="timetable"><tr><th></th>'
    for day in DAYS:
        table_html += f"<th>{day}</th>"
    table_html += "</tr>"

    for time in TIMES:
        table_html += f"<tr><th>{time}</th>"
        for day in DAYS:
            cell_exams = grid[(day, time)]
            if cell_exams:
                cell_content = "".join(
                    f'<span class="exam-cell" style="background-color:{MODULE_COLORS.get(exam, DEFAULT_MODULE_COLOR)};">{label}</span><br>'
                    for exam, label in cell_exams
                )
            else:
                cell_content = '<span class="empty-cell">--</span>'
            table_html += f"<td>{cell_content}</td>"
        table_html += "</tr>"

    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Status panel ----------
st.markdown('<div class="stats-box">', unsafe_allow_html=True)
if assignment is None:
    st.markdown(f"STATUS: FAILED&nbsp;&nbsp;|&nbsp;&nbsp;SEARCH STEPS: {steps}", unsafe_allow_html=True)
else:
    st.markdown(f"STATUS: SOLVED&nbsp;&nbsp;|&nbsp;&nbsp;SEARCH STEPS: {steps}", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)