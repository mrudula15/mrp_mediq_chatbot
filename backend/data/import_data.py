import pyodbc
import pandas as pd
import os

server = "LAPTOP-0OSF00UQ\\SQLEXPRESS01"
database = "synthea_db_cleaned"
driver = "{ODBC Driver 17 for SQL Server}"

try:
    # Connect to database
    conn = pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    print(f"Connected to '{database}' successfully")

    # Path to cleaned CSV files
    processed_data_path = r"C:\Users\mrudu\PycharmProjects\health-equity-LLM-chatbot\backend\data\processed"

    # Table-to-file mapping
    # Corrected insertion order to match foreign key dependencies
    table_files = {
        "patients": "patients_cleaned.csv",
        "organizations": "organizations_cleaned.csv",
        "providers": "providers_cleaned.csv",
        "payers": "payers_cleaned.csv",
        "encounters": "encounters_cleaned.csv",
        "conditions": "conditions_cleaned.csv",
        "medications": "medications_cleaned.csv",
        "claims": "claims_cleaned.csv"
    }

    # Define data type corrections
    dtype_mappings = {
        "patients": {
            "PATIENTID": str, "DEATHDATE": str, "MARITAL": str, "RACE": str,
            "ETHNICITY": str, "GENDER": str, "ADDRESS": str, "CITY": str,
            "STATE": str, "COUNTY": str, "ZIP": str,  # Ensure ZIP stays string
            "HEALTHCARE_EXPENSES": float, "HEALTHCARE_COVERAGE": float,
            "INCOME": int, "AGE": int
        },
        "conditions": {
            "PATIENTID": str, "ENCOUNTERID": str, "DESCRIPTION": str,
            "CONDITION_DURATION_DAYS": int, "CONDITION_TYPE": str
        },
        "encounters": {
            "ENCOUNTERID": str, "PATIENTID": str, "PROVIDERID": str, "PAYERID": str,
            "ENCOUNTERCLASS": str, "ENCOUNTER_DESCRIPTION": str,
            "BASE_ENCOUNTER_COST": float, "TOTAL_CLAIM_COST": float,
            "PAYER_COVERAGE": float, "OUT_OF_POCKET_COST": float,
            "COST_COVERAGE_RATIO": float, "CLAIM_PROFIT_MARGIN": float,
            "ENCOUNTER_REASON_DESCRIPTION": str, "ENCOUNTER_REASON_TYPE": str,
            "ENCOUNTER_DURATION_MINUTES": int, "ENCOUNTER_DURATION": str
        },
        "medications": {
            "PATIENTID": str, "ENCOUNTERID": str, "PAYERID": str, "MEDICATION_DESCRIPTION": str,
            "BASE_COST": float, "PAYER_COVERAGE": float, "DISPENSES": int,
            "TOTALCOST": float, "OUT_OF_POCKET_COST": float,
            "COST_COVERAGE_RATIO": float, "PER_DISPENSE_COST": float,
            "MEDICATION_REASON_DESCRIPTION": str, "MEDICATION_DURATION_DAYS": int
        },
        "claims": {
            "CLAIMID": str, "PATIENTID": str, "PROVIDERID": str,
            "PRIMARYPATIENTINSURANCEID": str, "SECONDARYPATIENTINSURANCEID": str,
            "DEPARTMENTID": str
        },
        "payers": {
            "PAYERID": str, "PAYER_NAME": str, "OWNERSHIP": str,
            "AMOUNT_COVERED": float, "AMOUNT_UNCOVERED": float
        },
        "organizations": {
            "ORGANIZATIONID": str, "NAME": str, "ADDRESS": str,
            "CITY": str, "STATE": str, "ZIP": str
        },
        "providers": {
            "PROVIDERID": str, "ORGANIZATIONID": str, "NAME": str,
            "ENCOUNTERS_COUNT": int
        }
    }

    # Process each table
    for table, filename in table_files.items():
        file_path = os.path.join(processed_data_path, filename)

        if os.path.exists(file_path):
            print(f"Inserting data into {table} from {filename}...")

            # Read CSV with defined dtypes
            df = pd.read_csv(file_path, dtype=dtype_mappings.get(table, {}))

            # Ensure proper datetime conversion with timezone preservation
            if "START" in df.columns:
                df["START"] = pd.to_datetime(df["START"], errors="coerce").dt.tz_localize(None)
            if "STOP" in df.columns:
                df["STOP"] = pd.to_datetime(df["STOP"], errors="coerce").dt.tz_localize(None)
            if "BIRTHDATE" in df.columns:
                df["BIRTHDATE"] = pd.to_datetime(df["BIRTHDATE"], errors="coerce").dt.tz_localize(None)
            if "DEATHDATE" in df.columns:
                df["DEATHDATE"] = pd.to_datetime(df["DEATHDATE"], errors="coerce").dt.tz_localize(None)

            # Convert float columns properly
            float_cols = [col for col, dtype in dtype_mappings[table].items() if dtype == float]
            for col in float_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")  # Convert invalid to NaN
                df[col] = df[col].fillna(0).astype(float)  # Replace NaN with 0
                df[col] = df[col].round(2)  # Round to 2 decimal places

            # Prepare SQL query for bulk insert
            columns = ", ".join(df.columns)
            placeholders = ", ".join(["?" for _ in df.columns])
            insert_sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            # Convert DataFrame to list of tuples for executemany()
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]

            # Execute bulk insert
            cursor.executemany(insert_sql, data)
            conn.commit()
            print(f"✅ {len(data)} rows inserted into {table}")

        else:
            print(f"⚠ CSV file not found: {file_path}")

    cursor.close()
    conn.close()
    print("✅ All data inserted successfully!")

except Exception as e:
    print("Database connection failed:", e)
