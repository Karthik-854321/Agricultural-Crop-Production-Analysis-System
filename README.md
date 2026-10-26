# Crop Production Analysis System

A Python + Streamlit dashboard for describing historical crop production, cultivated area, rainfall, and yield using CSV/Excel data and MySQL.

## Features

- Upload CSV and Excel datasets.
- Normalize common column aliases and validate required fields.
- Flag missing values, invalid years, negative measurements, and zero area.
- Calculate record-level yield (`production / cultivated_area`) where area is positive.
- Store regions, crops, and observations in MySQL.
- Filter records by crop, region, and year.
- Plot production, yield, and region comparisons.
- Export validation issues, summaries, year comparisons, and database records.
- Unit labels are stored with each record; confirm units before comparing unlike datasets.

## Folder structure

```text
crop-production-analysis/
├── app.py
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── validation.py
│   ├── analysis.py
│   └── charts.py
├── tests/
│   └── test_validation.py
├── data/
│   ├── raw/.gitkeep
│   └── processed/.gitkeep
└── reports/.gitkeep
```

## Requirements

- Python 3.10 or newer
- MySQL Server 8.0 or compatible
- Git

## Run on Windows

Open PowerShell in the project directory.

### 1. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### 2. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure MySQL

Start MySQL Server. Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set your MySQL username and password. Do not commit `.env`.

The database user needs permission to create the `crop_analysis` database and tables. The app's **Initialize database** button creates the database and tables. Alternatively, run `schema.sql` in MySQL Workbench.

### 4. Start the app

```powershell
streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`. Open it in your browser.

### 5. Upload data

The required column names are:

- `crop`
- `region`
- `year`
- `cultivated_area`
- `production`

Optional columns:

- `rainfall`
- `area_unit`
- `production_unit`
- `rainfall_unit`

Example CSV:

```csv
crop,region,year,cultivated_area,production,rainfall,area_unit,production_unit,rainfall_unit
Rice,North,2021,100,250,780,hectare,tonne,mm
Rice,North,2022,110,286,820,hectare,tonne,mm
Wheat,South,2021,90,180,620,hectare,tonne,mm
```

Upload the file in **Upload data**, review validation, and choose **Save valid rows to MySQL**. To explore a file without saving it, choose the session-upload option in the dashboard.

## Run tests

```powershell
pytest -q
```

## Push to GitHub

Create an empty repository on GitHub (do not add a README or license there if you already have them locally). Then run:

```powershell
git init
git add .
git status
git commit -m "Build crop production analysis system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/crop-production-analysis.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git says the remote already exists:

```powershell
git remote -v
git remote set-url origin https://github.com/YOUR-USERNAME/crop-production-analysis.git
```

Before committing, confirm `.env` is not listed by `git status`. If it was accidentally tracked, remove it from Git's index with `git rm --cached .env`; rotate the password if it was pushed.

## Data and interpretation notes

- Yield is a ratio. The output unit is `production unit / area unit` (for example, tonne/hectare).
- Zero or missing area prevents a valid yield calculation.
- The dashboard does not automatically convert units. Do not aggregate or compare records with different units without converting them first.
- Year-over-year percentage changes are descriptive. A previous value of zero makes percentage change undefined.
- Missing rainfall is allowed because it is optional.
- The app does not infer that rainfall caused production changes and does not provide agronomic advice.
- Uploaded rows are inserted as new observations; the current starter version does not deduplicate repeated uploads. Avoid uploading the same file twice.

## Known limitations / future improvements

- Add unit conversion and strict unit-compatibility checks.
- Add duplicate detection and an import-batch audit table.
- Add authentication and role-based access before deploying publicly.
- Add a data preview for extremely large files and database pagination.
- Add integration tests against a dedicated test MySQL database.
