# Tournament Tracking System

A simple, beginner-friendly tournament tracking system built with React (frontend) and Django REST Framework (backend).

## Project Features
- **User Authentication**: JWT-based login/register with roles (Admin, Team Manager, Spectator).
- **Tournament Management**: Create and track tournaments.
- **Team & Player Management**: Manage teams and their player rosters.
- **Fixture Generation**: Generate matches (Round Robin, Knockout).
- **Match & Score Management**: Record match scores.
- **Standings & Leaderboards**: Live standings based on match results.

## Folder Structure
- `backend/`: Django REST Framework API application.
- `frontend/`: React single-page application built with Vite and Tailwind CSS.

## Getting Started

### Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
