# Global Patent Intelligence Data Pipeline

A project that builds a data system that collects, cleans, stores, and analyzes large-scale patent data.

## Getting Started

1. **Activate the Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

You can run the entire pipeline at once or execute individual steps.

### Run the Full Pipeline
To execute the complete end-to-end process (Extract data -> Clean and Load -> Generate Reports):
```bash
python main.py
```

### Run Individual Scripts
If you want to run specific steps individually, you can execute the scripts from the `scripts/` folder:

- **Extract data**: `python scripts/extract.py`
- **Clean and Load data into database**: `python scripts/clean.py`
- **Generate Reports (JSON/CSV)**: `python scripts/report.py`

### Launch the Dashboard
To start the interactive analytics dashboard, run:
```bash
streamlit run dashboard.py
```
