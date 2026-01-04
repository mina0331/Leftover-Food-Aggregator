# Leftover Food Aggregator

A full-stack Django web application that aggregates real-time leftover food events from campus organizations, enabling students to easily discover available food through role-based access, secure authentication, and dynamic filtering.

---

## 🚀 Features

- **Role-Based Authentication**
  - Google OAuth login for students and campus organizations
  - Separate dashboards based on user roles

- **Event Aggregation**
  - Centralized listing of leftover food events posted by organizations
  - Real-time availability and event metadata

- **Dynamic Filtering & Sorting**
  - Filter events by organization, cuisine type, and date
  - Efficient query-based filtering using Django ORM

- **Relational Data Modeling**
  - PostgreSQL-backed models for users, organizations, events, cuisines, and allergens
  - Enforced data integrity through foreign keys and constraints

- **Media Storage**
  - Scalable image and media storage using AWS S3

- **Deployment**
  - Deployed on Heroku with production-ready settings

---

## 🛠️ Tech Stack

- **Backend:** Django, Python  
- **Database:** PostgreSQL  
- **Authentication:** Google OAuth  
- **Cloud & Deployment:** Heroku, AWS S3  
- **Frontend:** Django Templates, HTML, CSS  
- **Version Control:** Git, GitHub  

---

## 📐 Architecture Overview

- Django MVC-style architecture
- REST-style request handling via Django views
- ORM-driven database access for maintainability and performance
- Cloud-based static and media asset management

---

## 🧪 Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/leftover-food-aggregator.git
   cd leftover-food-aggregator
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Run local server**
  ```bash
  python manage.py migrate
  python manage.py runserver

  
  

