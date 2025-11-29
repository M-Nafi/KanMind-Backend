# KanMind Backend

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-5.2.8-green)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

A Django REST Framework backend for a Kanban-style project management system.  
Provides user authentication, board management, task tracking, and commenting features.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication)
  - [Boards](#boards)
  - [Tasks](#tasks)
  - [Comments](#comments)
  - [Dashboard](#dashboard)
- [Project Structure](#project-structure)
- [License](#license)
- [Frontend](#frontend)

---

## Features

- **User Authentication** Token-based authentication with registration and login
- **Board Management** Create and manage project boards with team members
- **Task Tracking** Full CRUD operations for tasks with assignees, reviewers, and priorities
- **Comments** Add and manage comments on tasks
- **Permission system** Role-based access control for boards and tasks

---

## Tech Stack

- **Django 5.2.8: Web framework**
- **Django REST Framework 3.16.1: REST API toolkit**
- **Token Authentication: Built-in DRF token authentication**
- **SQLite: Database (development)**
- **CORS Headers: Cross-origin resource sharing support**

---

## Prerequisites

- Python **3.10+** or higher
- pip (Python package manager)

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/M-Nafi/KanMind-Backend.git
cd KanMind-Backend
```
 
### 2. Create a virtual environment:

```bash
python -m venv .venv
```

### 3. Activate the virtual environment:

- On macOS/Linux:
```bash
source .venv/bin/activate
```

- On Windows:
```bash
.venv\Scripts\activate
```

### 4. Install dependencies:

```bash
pip install -r requirements.txt
```

### 5. Create a .env file in the root directory:

```bash
DJANGO_SECRET_KEY=your-secret-key-here
```

### 6. Run migrations:

```bash
python manage.py migrate
```

### 7. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

### 8. Start the development server:

```bash
python manage.py runserver
```


## API Endpoints
- The API will be available at http://127.0.0.1:8000/

### Authentication
- `POST /api/registration/` – Register a new user
- `POST /api/login/` – Login user
- `GET /api/email-check/` – Check if an email is already registered

### Boards
- `GET /api/boards/` – List all accessible boards
- `POST /api/boards/` – Create a new board
- `GET /api/boards/<int:pk>/` – Retrieve board details
- `PATCH /api/boards/<int:pk>/` – Update a board
- `DELETE /api/boards/<int:pk>/` – Delete a board

### Tasks
- `GET /api/tasks/assigned-to-me/` – List tasks assigned to the user
- `GET /api/tasks/reviewing/` – List tasks the user is reviewing
- `GET /api/boards/<int:board_id>/tasks/` – List tasks in a board
- `POST /api/tasks/` – Create a new task
- `GET /api/tasks/<int:pk>/` – Retrieve task details
- `PATCH /api/tasks/<int:pk>/` – Update a task
- `DELETE /api/tasks/<int:pk>/` – Delete a task

### Comments
- `GET /api/tasks/<int:task_id>/comments/` – List comments for a task
- `POST /api/tasks/<int:task_id>/comments/` – Add a comment
- `DELETE /api/tasks/<int:task_id>/comments/<int:pk>/` – Delete a comment

### Dashboard
- `GET /api/dashboard/` – Retrieve dashboard statistics


## Project Structure
kanmind_backend/
├── auth_app/           # User authentication and management
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── models.py
│   └── ...
├── boards_app/         # Board management
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── models.py
│   └── ...
├── task_app/           # Task and comment management
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── models.py
│   └── ...
├── core/               # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── manage.py
├── requirements.txt
└── README.md


## License

This project was created as part of the continuing education program at **Developer Akademie**.  
It is licensed under the **MIT License**.

---

## Frontend

The frontend for this project was provided by **Developer Akademie**  
and is available at the following repository:

[KanMind Frontend Repository](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)