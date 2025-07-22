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
- **south-korea-latest.osm.pbf**: OpenStreetMap data in PBF format. You will need to import this data into the database.

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

5.  **Import the National Standard Node-Link Data into the database:**
    Modify the path in `backend/scripts/import_data.py` to point to your downloaded node-link data, and then run the script to import the data into the database:
    ```bash
    python backend/scripts/import_data.py
    ```

6.  **Import the South Korea OpenStreetMap data (`south-korea-latest.osm.pbf`) into the database:**
    - Use the `osm2pgsql` tool to import the `.osm.pbf` file into your PostgreSQL/PostGIS database:
    ```bash
    osm2pgsql -d your_database_name -U your_database_user -H localhost -P 5432 --create --slim -G --hstore --multi-geometry south-korea-latest.osm.pbf
    ```

7.  **Navigate back to the project root directory:**
    ```bash
    cd ..
    ```

8.  **Run the application from the root directory:**
    ```bash
    uvicorn backend.main:app --reload
    ```

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required dependencies:**
    ```bash
    npm install
    ```

3.  **Run the frontend application:**
    ```bash
    npm run dev
    ```

### Data Usage and Legal Considerations

1. **Licensing and Attribution**:
   - The OpenStreetMap data used in this project is licensed under the Open Database License (ODbL). By using this data, you agree to the terms of the ODbL. You must provide appropriate attribution as required by the ODbL. Example attribution:
     ```
     Data from OpenStreetMap contributors, licensed under the Open Database License (ODbL).
     ```

2. **Data Updates and Maintenance**:
   - The `south-korea-latest.osm.pbf` file is regularly updated by OpenStreetMap. Ensure that your database reflects the latest version of this dataset to maintain accuracy.

3. **Data Privacy and Compliance**:
   - This project does not collect personal information. However, if you combine this data with other data sources, ensure compliance with data protection laws such as GDPR.

4. **Data Size and Performance**:
   - OpenStreetMap data is large and may impact performance depending on your infrastructure. Ensure that you have sufficient resources to handle the database and perform optimal queries.

5. **Acknowledgment of Data Providers**:
   - In addition to OpenStreetMap, any other public datasets used in this project must be properly acknowledged as per the respective licenses.
