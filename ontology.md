# Examination Timetabling Ontology
## COS737 Artificial Intelligence — Part g
## Option Chosen: Option 1 (Conceptual Ontology Design)

---

## 1. Classes

| Class       | Description                                               |
|-------------|-----------------------------------------------------------|
| Exam        | An examination to be scheduled in the timetable           |
| Venue       | A room or hall where an exam is held                      |
| TimeSlot    | A specific day and time period available for scheduling   |
| ExamType    | The category of an exam (Written or Computer based)       |
| Student     | A student enrolled in one or more exams                   |
| Invigilator | A staff member who supervises an exam session             |

---

## 2. Object Properties (Relationships Between Classes)

| Property       | Domain      | Range       | Description                                               |
|----------------|-------------|-------------|-----------------------------------------------------------|
| scheduledIn    | Exam        | TimeSlot    | Assigns an exam to a specific time slot                   |
| assignedTo     | Exam        | Venue       | Assigns an exam to a specific venue                       |
| hasOverlapWith | Exam        | Exam        | Indicates two exams share enrolled students (symmetric)   |
| hasExamType    | Exam        | ExamType    | Specifies whether the exam is Written or Computer based   |
| supervisedBy   | Exam        | Invigilator | Assigns an invigilator to supervise the exam              |
| enrolledIn     | Student     | Exam        | Records which exams a student is registered for           |

---

## 3. Data Properties

| Property        | Domain      | Data Type | Description                                   |
|-----------------|-------------|-----------|-----------------------------------------------|
| hasExamCode     | Exam        | String    | The unique code identifier (e.g. CSC711)      |
| hasStudentCount | Exam        | Integer   | Number of students registered for the exam    |
| hasCapacity     | Venue       | Integer   | Maximum number of students the venue holds    |
| hasStartTime    | TimeSlot    | String    | The time the slot begins (e.g. 09:00)         |
| hasDay          | TimeSlot    | String    | The day of the time slot (e.g. Monday)        |
| hasVenueName    | Venue       | String    | The display name of the venue                 |
| hasStaffID      | Invigilator | String    | Unique identifier for the invigilator         |

---

## 4. Named Individuals

| Individual    | Class       | Key Properties                                                |
|---------------|-------------|---------------------------------------------------------------|
| CSC711        | Exam        | hasExamCode="CSC711", hasStudentCount=70, hasExamType=Written |
| CSC713        | Exam        | hasExamCode="CSC713", hasStudentCount=35, hasExamType=ComputerBased |
| HallA         | Venue       | hasVenueName="Hall A", hasCapacity=120                        |
| Lab1          | Venue       | hasVenueName="Lab 1", hasCapacity=40                          |
| T1            | TimeSlot    | hasDay="Monday", hasStartTime="09:00"                         |
| T3            | TimeSlot    | hasDay="Tuesday", hasStartTime="09:00"                        |
| Written       | ExamType    | (class instance representing the Written type)                |
| ComputerBased | ExamType    | (class instance representing the Computer based type)         |
| Invigilator01 | Invigilator | hasStaffID="INV001"                                           |

---

## 5. Extension: Invigilator Assignment

### Chosen Extension
The ontology is extended with the **Invigilator** class to represent staff members
who supervise exam sessions.

### How It Works
Each `Exam` individual is connected to an `Invigilator` individual via the
`supervisedBy` object property. An invigilator has a `hasStaffID` data property.

### Additional Constraint Supported
This extension supports the following constraint:

> An invigilator cannot supervise two exams scheduled in the same time slot.

Formally: if `Exam_A supervisedBy Invigilator_X` and `Exam_B supervisedBy Invigilator_X`,
then `Exam_A scheduledIn TimeSlot_Y` implies `Exam_B scheduledIn TimeSlot_Z` where Y ≠ Z.

This mirrors the student clash constraint already present in the CSP, but applied
to invigilators rather than students. Both are "no-conflict-in-the-same-slot" rules
on different entity types.

---

## 6. How the Ontology Connects to the CSP

| CSP Element              | Ontology Representation                                       |
|--------------------------|---------------------------------------------------------------|
| CSP Variable             | Each individual of class `Exam`                               |
| Domain value             | A pair of (`TimeSlot` individual, `Venue` individual)         |
| Assigned value           | `scheduledIn` + `assignedTo` object properties               |
| Student clash constraint | `hasOverlapWith` between two `Exam` individuals               |
| Venue capacity rule      | `hasStudentCount` (Exam) ≤ `hasCapacity` (Venue)             |
| Computer-based rule      | `hasExamType=ComputerBased` → `assignedTo=Lab1`              |
| Venue exclusivity        | No two exams share the same `scheduledIn` + `assignedTo` pair |
| Invigilator constraint   | No two exams share `supervisedBy` + `scheduledIn` values      |

The CSP solver treats variables, domains, and constraints as computational objects.
The ontology provides a formal semantic layer on top of those same concepts,
making the domain knowledge explicit, shareable, and extensible. A reasoner
operating on this ontology could in principle derive the same constraints that
the CSP solver enforces algorithmically.
