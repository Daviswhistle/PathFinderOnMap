# Path-Finding Project

This project is a web-based map service that provides optimal route finding capabilities using Python, FastAPI, and PostGIS.

## Project Structure

- `backend/`: The backend application (FastAPI).
- `frontend/`: The frontend application (HTML, CSS, JavaScript).

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL with PostGIS extension
- Ubuntu 24.04.2 (or other Debian-based system)
- **National Standard Node-Link Data**: Download the data, and modify the path in `backend/scripts/import_data.py` to correctly insert it into the database.
- **south-korea-latest.osm.pbf**: OpenStreetMap data in PBF format.

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your database configuration in a `.env` file:**
    ```
    DATABASE_URL=postgresql://user:password@host:port/dbname
    ```

5.  **Navigate back to the project root directory:**
    ```bash
    cd ..
    ```

6.  **Run the application from the root directory:**
    ```bash
    uvicorn backend.main:app --reload
    ```

### Frontend Setup

1.  cd frontend
2.  npm install
3.  npm run dev
