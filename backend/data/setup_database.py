import pyodbc

server = "LAPTOP-0OSF00UQ\\SQLEXPRESS01"
database = "synthea_db_cleaned"
driver = "{ODBC Driver 17 for SQL Server}"

try:
    conn = pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{database}') CREATE DATABASE {database}")
    print(f"Database '{database}' is ready")

    conn.close()
    conn = pyodbc.connect(
        f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    print(f"Connected to '{database}' successfully")

    tables_sql = [
        # 1️⃣ Patients table (no dependencies)
        """
        CREATE TABLE patients (
            patientid VARCHAR(50) CONSTRAINT pk_patients PRIMARY KEY,
            birthdate DATE NOT NULL,
            deathdate DATE NULL,
            first VARCHAR(100) NULL,
            last VARCHAR(100) NULL,
            marital VARCHAR(20) NULL,
            race VARCHAR(50) NULL,
            ethnicity VARCHAR(50) NULL,
            gender CHAR(1) NOT NULL CONSTRAINT chk_gender CHECK (gender IN ('M', 'F')),
            address VARCHAR(255) NULL,
            city VARCHAR(100) NULL,
            state VARCHAR(50) NULL,
            county VARCHAR(100) NULL,
            zip VARCHAR(10) NULL,
            healthcare_expenses FLOAT NULL,
            healthcare_coverage FLOAT NULL,
            income INT NULL,
            age INT NOT NULL CONSTRAINT chk_age CHECK (age >= 0)
        );
        """,
        # 2️⃣ Organizations table (used by providers)
        """
        CREATE TABLE organizations (
            organizationid VARCHAR(50) CONSTRAINT pk_organizations PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address VARCHAR(255) NULL,
            city VARCHAR(100) NULL,
            state VARCHAR(50) NULL,
            zip VARCHAR(20) NULL
        );
        """,
        # 3️⃣ Providers table (depends on organizations)
        """
        CREATE TABLE providers (
            providerid VARCHAR(50) CONSTRAINT pk_providers PRIMARY KEY,
            organizationid VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            encounters_count INT NOT NULL CONSTRAINT chk_encounters_count CHECK (encounters_count >= 0),
            CONSTRAINT fk_providers_organization FOREIGN KEY (organizationid) REFERENCES organizations(organizationid)
        );
        """,
        # 4️⃣ Payers table (used by encounters, medications, claims)
        """
        CREATE TABLE payers (
            payerid VARCHAR(50) CONSTRAINT pk_payers PRIMARY KEY,
            payer_name VARCHAR(255) NOT NULL,
            ownership VARCHAR(50) NOT NULL,
            amount_covered FLOAT NOT NULL,
            amount_uncovered FLOAT NOT NULL
        );
        """,
        # 5️⃣ Encounters table (depends on patients, providers, payers)
        """
        CREATE TABLE encounters (
            encounterid VARCHAR(50) CONSTRAINT pk_encounters PRIMARY KEY,
            start DATETIME NOT NULL,
            stop DATETIME NULL,
            patientid VARCHAR(50) NOT NULL,
            providerid VARCHAR(50) NULL,
            payerid VARCHAR(50) NULL,
            encounterclass VARCHAR(50) NOT NULL,
            encounter_description VARCHAR(255) NOT NULL,
            base_encounter_cost FLOAT NOT NULL,
            total_claim_cost FLOAT NOT NULL,
            payer_coverage FLOAT NULL,
            encounter_reason_description VARCHAR(255) NULL,
            encounter_reason_type VARCHAR(50) NULL,
            encounter_duration_minutes INT NULL CONSTRAINT chk_encounter_duration CHECK (encounter_duration_minutes >= 0),
            encounter_duration VARCHAR(50) NULL,
            out_of_pocket_cost FLOAT NOT NULL,
            cost_coverage_ratio FLOAT NULL,
            claim_profit_margin FLOAT NULL,
            CONSTRAINT fk_encounters_patient FOREIGN KEY (patientid) REFERENCES patients(patientid),
            CONSTRAINT fk_encounters_provider FOREIGN KEY (providerid) REFERENCES providers(providerid),
            CONSTRAINT fk_encounters_payer FOREIGN KEY (payerid) REFERENCES payers(payerid)
        );
        """,
        # 6️⃣ Conditions table (depends on patients, encounters)
        """
        CREATE TABLE conditions (
            patientid VARCHAR(50) NOT NULL,
            encounterid VARCHAR(50) NOT NULL,
            start DATE NOT NULL,
            stop DATE NULL,
            description VARCHAR(255) NOT NULL,
            condition_duration_days INT NULL CONSTRAINT chk_condition_duration CHECK (condition_duration_days >= 0),
            condition_type VARCHAR(50) NOT NULL,
            CONSTRAINT fk_conditions_patient FOREIGN KEY (patientid) REFERENCES patients(patientid),
            CONSTRAINT fk_conditions_encounter FOREIGN KEY (encounterid) REFERENCES encounters(encounterid)
        );
        """,
        # 7️⃣ Medications table (depends on patients, encounters, payers)
        """
        CREATE TABLE medications (
            start DATETIMEOFFSET NOT NULL,
            stop DATETIMEOFFSET NULL,
            patientid VARCHAR(50) NOT NULL,
            payerid VARCHAR(50) NULL,
            encounterid VARCHAR(50) NOT NULL,
            medication_description VARCHAR(255) NOT NULL,
            base_cost FLOAT NOT NULL,
            payer_coverage FLOAT NULL,
            dispenses INT NULL CONSTRAINT chk_dispenses CHECK (dispenses >= 0),
            totalcost FLOAT NOT NULL,
            medication_reason_description VARCHAR(255) NULL,
            medication_duration_days INT NULL CONSTRAINT chk_medication_duration CHECK (medication_duration_days >= 0),
            out_of_pocket_cost FLOAT NOT NULL,
            cost_coverage_ratio FLOAT NULL,
            per_dispense_cost FLOAT NULL,
            CONSTRAINT fk_medications_patient FOREIGN KEY (patientid) REFERENCES patients(patientid),
            CONSTRAINT fk_medications_encounter FOREIGN KEY (encounterid) REFERENCES encounters(encounterid),
            CONSTRAINT fk_medications_payer FOREIGN KEY (payerid) REFERENCES payers(payerid)
        );
        """,
        # 8️⃣ Claims table (depends on patients, providers, payers)
        """
        CREATE TABLE claims (
            claimid VARCHAR(50) CONSTRAINT pk_claims PRIMARY KEY,
            patientid VARCHAR(50) NOT NULL,
            providerid VARCHAR(50) NOT NULL,
            primarypatientinsuranceid VARCHAR(50) NULL,
            secondarypatientinsuranceid VARCHAR(50) NULL,
            departmentid VARCHAR(50) NULL,
            CONSTRAINT fk_claims_patient FOREIGN KEY (patientid) REFERENCES patients(patientid),
            CONSTRAINT fk_claims_provider FOREIGN KEY (providerid) REFERENCES providers(providerid),
            CONSTRAINT fk_claims_primarypayer FOREIGN KEY (primarypatientinsuranceid) REFERENCES payers(payerid),
            CONSTRAINT fk_claims_secondarypayer FOREIGN KEY (secondarypatientinsuranceid) REFERENCES payers(payerid)
        );
        """
    ]

    for sql in tables_sql:
        try:
            cursor.execute(sql)
            conn.commit()  # Ensure the table is actually created
            print("Table created successfully")
        except pyodbc.Error as e:
            print("Error creating table:", e)

    cursor.close()
    conn.close()
    print("All tables created successfully")

except Exception as e:
    print("Database connection failed:", e)
