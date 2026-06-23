# COS737 Exam Timetabling CSP

<p align="center">
  <img 
    src="https://github.com/user-attachments/assets/a54345d4-789f-49b1-aaa3-d4b8e76bea65" 
    alt="Exam Timetabling CSP Banner" 
    width="100%"
  />
</p>

<p align="center">
  <strong>Artificial Intelligence • Constraint Satisfaction Problems • Exam Scheduling • Python • Streamlit • Course Work </strong>
</p>

---

## Overview

This repository contains our solution for the COS737 Artificial Intelligence assignment.

The project focuses on solving an **examination timetabling problem** using a **Constraint Satisfaction Problem (CSP)** approach. The system assigns exams to valid time slots and venues while satisfying the required scheduling constraints.

The assignment also includes search strategy comparison, performance analysis, an over-constrained case, a Streamlit dashboard for screen output, a search tree visualiser, and an ontology for the exam timetabling domain.

---

## Problem Description

The university needs to schedule exams into available time slots and venues.

The timetable must satisfy the following rules:

- Students with overlapping exams cannot write those exams in the same time slot.
- A venue cannot host more than one exam in the same time slot.
- A venue must have enough capacity for the assigned exam.
- Computer-based exams must be scheduled in Lab 1.

---

## Features

- CSP formulation of the exam timetabling problem
- Python-based CSP solver
- Basic backtracking search
- Advanced search strategies
- Search-step counting
- Streamlit dashboard for screen output
- GUI display of generated timetables
- Text file output for generated timetables and results
- Performance comparison across different problem instances
- Over-constrained problem analysis
- Search tree visualiser inside the dashboard
- Ontology design for the exam timetabling domain

---

## Technologies

- Python
- Streamlit
- Graphviz
- JSON
- Markdown

---

## Dashboard

The project uses a **Streamlit dashboard** as the main visual interface.

The dashboard displays:

- Generated examination timetable
- Search strategy used
- Number of search steps performed
- Performance comparison results
- Over-constrained case results
- Search tree visualisations
- Ontology summary

The solver still writes the required timetable and results to text files inside the `output/` folder.

---

## Search Strategies

The project compares a simple search strategy with more advanced CSP search strategies.

### Simple Strategy

- Basic Backtracking Search

### Advanced Strategies

- Minimum Remaining Values (MRV)
- Forward Checking

The strategies are compared using the number of search steps performed during the search process.

---

## Problem Instances

The solver is tested on four versions of the problem:

| Instance | Description |
|---|---|
| Smaller Instance | Uses the first five exams only |
| Full Instance | Uses all eight exams from the shared base instance |
| Extended Instance | Adds two additional exams to the full instance |
| Over-Constrained Instance | An infeasible version used to test failure detection |

---

## Search Tree Visualiser

The Streamlit dashboard includes a search tree visualiser that displays how the solver explores possible assignments.

Each node in the tree records:

- Exam being assigned
- Value attempted
- Whether the assignment succeeded or failed
- Whether the node led to backtracking
- Search step number

The visualiser shows the search tree for:

- Basic Backtracking
- At least one advanced search strategy

Successful, failed, and backtracking nodes are visually distinguished.

---

## Ontology

The project includes a conceptual ontology for the examination timetabling domain.

The ontology represents concepts such as:

- Exam
- Venue
- Time Slot
- Exam Type
- Student
- Department
- Invigilator

The ontology is connected to the CSP by showing how the main scheduling concepts and relationships support the constraints used by the solver.

---

## Project Structure

```text
COS737-Exam-Timetabling-CSP/
│
├── assets/
│   └── banner.png
│
├── app.py
├── csp_data.py
├── solver_basic.py
├── solver_advanced.py
├── experiments.py
├── tree_logger.py
├── tree_visualiser.py
├── utils.py
│
├── output/
│   ├── timetable.txt
│   ├── performance_results.txt
│   └── search_logs.json
│
├── screenshots/
│   ├── dashboard_timetable.png
│   ├── performance_comparison.png
│   ├── search_tree_basic.png
│   ├── search_tree_advanced.png
│   └── ontology.png
│
├── report/
│   └── COS737_Report.pdf
│
└── README.md
```
## Authors & Contributions

| Author | Role | Main Contributions |
|---|---|---|
| **Rolande Solomons** | CSP & Basic Solver Lead | CSP formulation, data model, constraint checker, simple backtracking solver, timetable output, and text file generation. |
| **Raeez Ahmed** | Search Strategy & Testing Lead | MRV, Forward Checking, experiment runner, performance comparison, search-step analysis, and over-constrained testing. |
| **Mohamed Yusuf Kathree** | Dashboard, Visualiser & Ontology Lead | Streamlit dashboard, GUI output, search tree visualiser, screenshots, ontology design, and demo video support. |

All members contributed to the final report, testing, documentation, and project presentation.
