# Digital Tracking Solution for Health Service Transparency (Team 1)

## Team Information
- **Mentor**: Fiston Munyampeta (mfiston2020@gmail.com | 0782009474)
- **Team Leader**: Cyprien Yankurije (yankurijecyprien76@gmail.com | 0789294965)
- **Duration**: 2 Weeks
- **Team Size**: 3-5 members

## Challenge Overview
This project is a Digital Tracking System designed to ensure transparency in the distribution of food aid for malnourished children. The platform tracks food from allocation to delivery, preventing diversion and ensuring accountability.

## Key Features

### 1. End-to-End Tracking
- Record food aid from warehouse allocation → distribution centres → beneficiaries
- Scan QR codes/barcodes at each checkpoint to log location, time, and responsible personnel

### 2. Transparency & Audit Trail
- Every transaction/modification is recorded on an immutable ledger (secure database)
- Citizens can verify food aid status via a public portal

### 3. Citizen Feedback Loop
- Beneficiaries confirm receipt via SMS/USSD/web app
- Anonymous reporting for missing/delayed supplies

### 4. Leader Dashboard
- Real-time monitoring for officials (Sector/Cell/District levels)
- Alerts for delays or irregularities (e.g., aid stuck at a checkpoint)

## Technical Implementation

### Data Science and AI/ML Features

#### Real-Time Dashboard
The dashboard is built with Plotly Dash and provides:
- Live tracking map of shipments (using Leaflet with GIS data), showing current locations of food aid trucks or packages
- Supply chain KPIs as cards:
  * Total aid dispatched vs. delivered
  * Average transit time per checkpoint
  * Number of delayed shipments
  * Number of reported issues (missing/delayed)
- Trend charts:
  * Daily shipments over time
  * Delay patterns by location/checkpoint
  * Feedback reports count and categories (anonymous complaints)
- Alerts panel:
  * Flag suspicious shipments (e.g., repeated delays or frequent lost reports)
  * Notify officials immediately when irregularities are detected

#### Fraud Detection with Machine Learning
- Uses Isolation Forest algorithm to flag shipments with unusual delay times or repeated 'lost' status
- Model inputs include:
  * Transit time between checkpoints
  * Frequency of reported issues per route
  * Number of times a shipment changes responsible personnel unexpectedly
- This automates flagging suspicious cases for officials to investigate

### Technical Requirements Implementation
- **Frontend**: React.js
- **Backend**: Python FastAPI
- **Database**: MySQL
- **Authentication**: Role-based access (citizens, distributors, officials)
- **Security**: End-to-end encryption for sensitive data
- **Deployment**: Hosted demo (locally for development)

## Prerequisites
- Python 3.8+
- Node.js 14+
- MySQL 8.0+
- Git

## Setup Instructions

### 1. Backend Setup

#### Install Python Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Dashboard and ML dependencies
pip install -r requirements-dashboard.txt
```

#### Database Setup
1. Install MySQL 8.0+ on your system
2. Create a MySQL database:
   ```sql
   CREATE DATABASE digital_aid_db;
   ```
3. Update the database credentials in `app/db_config.py` if needed:
   ```python
   DATABASE_URL = "mysql+pymysql://admin:securePass123@localhost:3306/digital_aid_db"
   ```

#### Run Database Initialization
```bash
python app/import_data.py
```

#### Start the Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or for production:
```bash
python app/main.py
```

### 2. Frontend Setup

#### Install Frontend Dependencies
```bash
cd frontend
npm install
```

#### Start the Frontend Server
```bash
npm start
```

### 3. Dashboard Setup

To run the Plotly Dash dashboard:
```bash
python app/plotydash.py
```

The dashboard will be available at http://localhost:8050

## Development

### Backend Development
- Main application file: `app/main.py`
- Database configuration: `app/db_config.py`
- Routes are defined in `app/routes/`
- Models are defined in `app/models/`
- Schemas are defined in `app/schemas/`

### Frontend Development
- Main frontend directory: `frontend/`
- Entry point: `frontend/src/index.js`
- Main component: `frontend/src/App.js`
- Components: `frontend/src/components/`

### Dashboard Development
- Main dashboard file: `app/plotydash.py`
- Alternative dashboard: `app/dashboard/dashboard.py`

## API Documentation
Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
├── app/                    # Backend FastAPI application
│   ├── main.py            # Main application entry point
│   ├── db_config.py       # Database configuration
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── routes/            # API route definitions
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── dashboard/         # Dashboard components
├── frontend/              # React frontend application
├── digital_aid_db.sql     # Database schema
├── food_aid_tracking_dataset_cleaned.csv  # Sample data
├── requirements.txt       # Core Python dependencies
├── requirements-dashboard.txt # Dashboard and ML dependencies
└── README.md             # This file
```

## Additional Scripts
- Data import script: `app/import_data.py`
- Enhanced API endpoints: `app/enhanced_main.py` (additional features)
- Dashboard application: `app/plotydash.py`

## Troubleshooting
1. If you encounter database connection errors, ensure MySQL is running and the database credentials are correct.
2. If you encounter import errors, ensure all Python dependencies are installed.
3. For CORS issues, check the origins in `app/main.py`.

## Demo Video Preparation

To create a demo video showcasing the Digital Tracking Solution:

1. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Start the dashboard**:
   ```bash
   python app/plotydash.py
   ```

4. **Record a walkthrough showing**:
   - User authentication and role-based access (citizen, distributor, official)
   - QR code generation and scanning at checkpoints
   - Real-time dashboard with live tracking map
   - Citizen feedback submission via SMS/USSD/web app
   - Fraud detection alerts and analysis
   - Audit trail verification
   - End-to-end shipment tracking workflow

## Pitch Deck Preparation

Prepare slides covering:
1. **Problem Statement**: Food aid diversion and lack of transparency in distribution
2. **Solution**: Digital tracking system with end-to-end visibility and accountability
3. **Technology Stack**: Python FastAPI, React, MySQL, Plotly Dash, Scikit-learn
4. **Key Features**:
   - QR code scanning at checkpoints
   - Real-time dashboard with live tracking
   - Fraud detection with machine learning
   - Citizen feedback loop
   - Audit trail and transparency
5. **Impact**: Improved accountability and reduced corruption in food aid distribution
6. **Scalability**: Can be extended to other regions and types of aid

## Deliverables for Hackathon

### 1. Working Prototype (Web/Mobile App)
- Food tracking workflow with QR code scanning
- Citizen feedback mechanism via SMS/USSD/web app
- Admin dashboard for officials

### 2. Dashboard
- Real-time monitoring dashboard built with Plotly Dash
- Interactive visualizations and analytics

### 3. Demo Video Preparation
To create a demo video:
1. Start the backend server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. Start the frontend: `cd frontend && npm start`
3. Start the dashboard: `python app/plotydash.py`
4. Record a walkthrough showing:
   - User authentication and role-based access
   - QR code scanning at checkpoints
   - Real-time dashboard with live tracking map
   - Citizen feedback submission
   - Fraud detection alerts
   - Audit trail verification

### 4. Pitch Deck Preparation
Prepare slides covering:
1. Problem Statement: Food aid diversion and lack of transparency
2. Solution: Digital tracking system with end-to-end visibility
3. Technology Stack: Python FastAPI, React, MySQL, Plotly Dash, Scikit-learn
4. Key Features: QR tracking, real-time dashboard, fraud detection, citizen feedback
5. Impact: Improved accountability and reduced corruption in food aid distribution
6. Scalability: Can be extended to other regions and types of aid