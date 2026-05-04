# Doctor Availability Scheduler Platform

Production-ready Flask + SQLite project for browsing doctors across clinics, searching roster-driven availability, and booking validated appointments with status tracking.

## Demo Login Access

- User login page: `/login/user`
- Admin login page: `/login/admin`
- Demo user credentials: `patient / patient123`
- Demo admin credentials: `admin / admin123`

## 1. Folder Structure

```text
Doctor Availability Scheduler Platform/
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- extensions.py
|   |-- models/
|   |-- routes/
|   |-- services/
|   |-- static/
|   |   |-- css/style.css
|   |   `-- js/app.js
|   `-- templates/index.html
|-- docs/
|   `-- postman_collection.json
|-- instance/
|-- requirements.txt
|-- run.py
`-- seed.py
```

## 2. System Design

### Clean Architecture

- Routes: HTTP transport, request parsing, response formatting.
- Services: business rules, validations, scheduling logic.
- Models: SQLAlchemy entities and relationships.
- Database: SQLite persistence through SQLAlchemy ORM.

### MVC Mapping

- Model: `app/models`
- View: `app/templates` + `app/static`
- Controller: `app/routes`

### Entities

- `Doctor`
- `Clinic`
- `Speciality`
- `DoctorClinicMapping`
- `DoctorLeave`
- `DoctorRoster`
- `Patient`
- `Appointment`

### Relationship Summary

- One `Doctor` belongs to one `Speciality`.
- One `Doctor` can work in many `Clinic` records through `DoctorClinicMapping`.
- One `Clinic` can have many `Doctor` records through `DoctorClinicMapping`.
- One `Doctor` has many `DoctorRoster` and `DoctorLeave` records.
- One `Patient` can have many `Appointment` records.
- One `Appointment` belongs to one `Doctor`, one `Patient`, and one `Clinic`.

### ER Diagram

```text
Speciality (name PK)
    |
    | 1..*
    v
Doctor (id PK, speciality FK -> Speciality.name)
    |\
    | \ 1..*
    |  \
    |   +--> DoctorLeave (id PK, doctor_id FK -> Doctor.id)
    |
    +--> DoctorClinicMapping (doctor_id PK/FK, clinic_id PK/FK)
    |         ^
    |         |
    |         | *..1
    |         |
    +--> DoctorRoster (id PK, doctor_id FK, clinic_id FK) ----> Clinic (id PK)
    |
    +--> Appointment (id PK, doctor_id FK, clinic_id FK, patient_id FK) <---- Patient (id PK)
```

### REST API Structure

```text
GET    /
GET    /login/user
GET    /login/admin
GET    /dashboard/user
GET    /dashboard/admin

POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/session

GET    /api/health
GET    /api/specialities

POST   /api/doctors
GET    /api/doctors?speciality=Gynecology

POST   /api/clinics
GET    /api/clinics
GET    /api/clinics/{id}
POST   /api/mappings

POST   /api/rosters
GET    /api/rosters

POST   /api/leaves

POST   /api/patients

GET    /api/availability?doctor_name=Ravi&date=2026-04-23
GET    /api/availability?speciality=Pediatrics&date=2026-04-23
GET    /api/availability?speciality=General%20Physician&date=2026-04-24&start_time=12:00&end_time=15:00

POST   /api/appointments
GET    /api/appointments/{id}
PATCH  /api/appointments/{id}/status

GET    /api/utilization?doctor_id=2&clinic_id=1&start_date=2026-04-21&end_date=2026-04-30

GET    /api/admin/patients
GET    /api/admin/appointments
POST   /api/admin/appointments/{id}/confirm
PATCH  /api/admin/appointments/{id}/status
GET    /api/admin/stats
```

## 3. Database Implementation

### Core Tables

- `doctors(id, name, speciality, email, phone, is_admin)`
- `clinics(id, name, location)`
- `doctor_clinic_mapping(doctor_id, clinic_id)`
- `doctor_leave(id, doctor_id, start_date, end_date, reason)`
- `doctor_roster(id, doctor_id, clinic_id, day, start_time, end_time)`
- `patients(id, name, contact)`
- `appointments(id, patient_id, doctor_id, clinic_id, date, time, status)`
- `specialities(name, description)`

### Constraints and Rules

- Foreign keys enforced through SQLAlchemy relationships.
- `doctor_leave.start_date <= end_date` is enforced in service logic and DB check constraint.
- `doctor_roster.start_time < end_time` is enforced in service logic and DB check constraint.
- Appointment status uses enum values: `BOOKED`, `COMPLETED`, `CANCELLED`, `NOSHOW`.
- Duplicate prevention for doctor email/phone, patient contact, clinic name+location, roster overlap, and leave overlap.

## 4. Business Rules Implemented

- Every newly created clinic automatically receives a Gynecology doctor with `is_admin=True`.
- Leave reasons are restricted to: `CONFERENCE`, `EMERGENCY`, `SICK`, `TRAINING`, `VACATION`.
- Availability search supports doctor name and speciality filters.
- Generic availability endpoint supports patient scenarios:
  - Pediatric doctor availability on a date.
  - General Physician availability inside a time range.
- Appointment lifecycle is limited to `BOOKED -> COMPLETED | CANCELLED | NOSHOW`.
- Booking prevents:
  - double booking,
  - booking during leave,
  - booking outside roster hours,
  - booking in the past,
  - booking off a 15-minute boundary.

## 5. Frontend

- Login portal served at `/`.
- Features:
  - separate user and admin login pages,
  - patient-facing availability search and booking dashboard,
  - admin-facing patient directory, appointment confirmation, status updates, and statistics dashboard.

## 6. Setup Instructions

### Step 1: Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 2: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Seed demo data

```powershell
python seed.py
```

### Step 4: Run the API and frontend

```powershell
python run.py
```

### Step 5: Open the UI

- Visit `http://127.0.0.1:5000/`
- Choose either:
  - User login at `http://127.0.0.1:5000/login/user`
  - Admin login at `http://127.0.0.1:5000/login/admin`

## 7. Sample API Requests And Responses

### Add doctor

```http
POST /api/doctors
Content-Type: application/json

{
  "name": "Dr. Seema Rao",
  "speciality": "Pediatrics",
  "email": "seema.rao@hospital.com",
  "phone": "9000000010"
}
```

```json
{
  "message": "Doctor created successfully.",
  "data": {
    "id": 5,
    "name": "Dr. Seema Rao",
    "speciality": "Pediatrics",
    "email": "seema.rao@hospital.com",
    "phone": "9000000010",
    "is_admin": false
  }
}
```

### Book appointment

```http
POST /api/appointments
Content-Type: application/json

{
  "patient_id": 1,
  "doctor_id": 2,
  "clinic_id": 1,
  "date": "2026-04-23",
  "time": "14:15"
}
```

```json
{
  "message": "Appointment booked successfully.",
  "data": {
    "id": 2,
    "patient": {
      "id": 1,
      "name": "Neha Sharma",
      "contact": "8800000001"
    },
    "doctor": {
      "id": 2,
      "name": "Dr. Ravi Mehta",
      "speciality": "Pediatrics",
      "email": "ravi.mehta@hospital.com",
      "phone": "9000000002",
      "is_admin": false
    },
    "clinic": {
      "id": 1,
      "name": "City Care Clinic",
      "location": "Park Street"
    },
    "date": "2026-04-23",
    "time": "14:15",
    "status": "BOOKED"
  }
}
```

### Track appointment status

```http
GET /api/appointments/2
```

```json
{
  "data": {
    "id": 2,
    "status": "BOOKED"
  }
}
```

### Update appointment status

```http
PATCH /api/appointments/2/status
Content-Type: application/json

{
  "status": "COMPLETED"
}
```

## 8. Demo Flow

1. Seed the database with `python seed.py`.
2. Open the UI at `http://127.0.0.1:5000/`.
3. Login as a user with `patient / patient123`.
4. Search Pediatrics availability on a Thursday date and click a displayed slot.
5. Create a patient profile and book the selected appointment.
6. Logout and login as admin with `admin / admin123`.
7. Review the patient directory and appointment queue.
8. Confirm the booked appointment and update its lifecycle status.

## 9. Notes On Logic

- Availability on a date is calculated from recurring roster windows minus leave conflicts and existing appointments.
- Utilization is `booked_slots / total_slots` across the requested date range, excluding cancelled appointments from the booked count.
- SQLite is used for simplicity, but the layering keeps the service logic portable for a future move to PostgreSQL.
