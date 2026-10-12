<div align="center">

# ApolloCRM — Contact Extractor

### Python-Powered B2B Contact Discovery & Management

A lightweight, command-line CRM tool designed to discover, enrich, organize, and export professional contact information using the Apollo.io REST API.

Built with Python, SQLite, and REST API integration.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![REST API](https://img.shields.io/badge/REST-API-009688?style=for-the-badge)
![CSV](https://img.shields.io/badge/CSV-Export-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![GitHub](https://img.shields.io/badge/Status-Personal_Project-blueviolet?style=for-the-badge)

---

**Contact Discovery · Data Enrichment · SQLite Storage · CSV Export**

</div>

## Overview

**ApolloCRM Contact Extractor** is a Python-based command-line application that simplifies professional contact discovery and management through the Apollo.io API.

The project provides a lightweight alternative to complex CRM platforms by combining contact extraction, individual profile enrichment, local database management, and structured CSV exports into a single interactive tool.

It was developed as a personal project to explore REST API integration, data processing, relational databases, and automation using Python.

### Project Objectives

- Automate the retrieval of professional contact information.
- Search organizations and discover associated professionals.
- Enrich individual profiles using available Apollo.io data.
- Store collected information in a structured SQLite database.
- Prevent duplicate contact records.
- Export organized datasets for further analysis.
- Handle API restrictions and unavailable endpoints gracefully.

---

## Key Features

| Feature | Description |
|---------|-------------|
| Organization Search | Search for companies using the Apollo.io API. |
| Contact Discovery | Retrieve professional profiles associated with a selected organization. |
| Keyword Filtering | Optionally filter contact searches using professional keywords. |
| Profile Enrichment | Retrieve additional information about a known professional. |
| Pagination Support | Process multiple pages of API search results. |
| Duplicate Detection | Avoid storing duplicate contacts using email or identity information. |
| SQLite Storage | Store contact information locally in a lightweight relational database. |
| CRM Viewer | Display saved professional contacts directly in the terminal. |
| CSV Export | Export stored records into a structured CSV file. |
| API Error Handling | Handle unsuccessful API responses and restricted endpoints. |
| Interactive CLI | Navigate the application using a simple terminal-based menu. |

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application logic |
| Apollo.io REST API | Professional contact discovery and enrichment |
| Requests | HTTP communication with API endpoints |
| SQLite | Local relational database |
| CSV | Structured data export |
| Git & GitHub | Version control and source code management |

The application uses Python's built-in `sqlite3`, `csv`, `time`, and `datetime` modules.

---

## How It Works

```text
                  +----------------------+
                  |       User           |
                  |   Interactive CLI    |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  |    ApolloCRM         |
                  |    Python Engine     |
                  +----------+-----------+
                             |
               +-------------+-------------+
               |                           |
               v                           v
    +----------------------+    +----------------------+
    | Organization Search  |    | Individual Contact   |
    | Apollo.io API        |    | Enrichment           |
    +----------+-----------+    +----------+-----------+
               |                           |
               +-------------+-------------+
                             |
                             v
                  +----------------------+
                  |  Data Extraction     |
                  |  & Normalization     |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  |  Duplicate Detection |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  |   SQLite Database    |
                  |       crm.db         |
                  +----------+-----------+
                             |
                  +----------+-----------+
                  |                      |
                  v                      v
        +------------------+   +------------------+
        | Terminal Viewer  |   | CSV Export       |
        +------------------+   +------------------+
```

---

## Project Structure

```text
ApolloCRM-Contact-Extractor/
│
├── apollo_crm.py          # Main application and CLI
├── config.example.py      # Example API configuration
├── requirements.txt       # Python dependencies
├── .gitignore             # Excluded files and sensitive data
└── README.md              # Project documentation
```

The application automatically creates a local SQLite database named `crm.db` when executed.

The database, API credentials, virtual environment, and generated contact exports are excluded from version control.

---

## Installation

### Prerequisites

Before running the application, make sure you have:

- Python 3 installed.
- pip available.
- An Apollo.io account.
- A valid Apollo.io API key.
- Access to the required Apollo.io API endpoints.

### 1. Clone the Repository

```bash
git clone https://github.com/simou-blh/ApolloCRM-Contact-Extractor.git

cd ApolloCRM-Contact-Extractor
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Apollo API

Create a local configuration file named `config.py` based on `config.example.py`.

```python
API_KEY = "YOUR_APOLLO_API_KEY"
```

Replace the placeholder with your own Apollo.io API key.

**Security Notice:** Never commit your actual API key to GitHub. The `config.py` file is excluded through `.gitignore`.

### 5. Run the Application

```bash
python apollo_crm.py
```

The application initializes the SQLite database and launches the interactive menu.

---

## Interactive Command-Line Interface

The application provides five main options:

```text
====================================================
    APOLLO CRM — Affaires Réglementaires
====================================================

1. Scraper une entreprise complète
2. Enrichir un contact (nom + entreprise)
3. Voir le CRM local
4. Exporter en CSV
5. Quitter

Choix :
```

### Option 1 — Organization Contact Discovery

Search for an organization by entering its name.

The application:

1. Sends a company search request to Apollo.io.
2. Displays matching organizations when multiple results exist.
3. Allows the user to select the appropriate company.
4. Accepts an optional professional keyword filter.
5. Retrieves available professional profiles.
6. Processes paginated API results.
7. Stores new contacts in SQLite.
8. Skips duplicate records.

The number of available results depends on API permissions, subscription limits, and returned data.

### Option 2 — Individual Contact Enrichment

Enrich a known professional profile using:

- First name.
- Last name.
- Organization name.

The application sends an enrichment request to Apollo.io and stores the returned profile when available.

This feature is also used as an alternative workflow when organization-wide contact search is restricted.

**Note:** This fallback requires the user to provide individual contact names. It does not automatically bypass Apollo.io subscription restrictions.

### Option 3 — View Local CRM

Display all stored professional contacts in the terminal.

Records are ordered by company and contact name.

### Option 4 — Export to CSV

Export the local CRM database into a CSV file.

Example output filename:

```text
export_crm_20261012_1530.csv
```

The exported file uses:

- UTF-8 with BOM encoding.
- Semicolon-separated columns.
- A timestamp-based filename.
- Structured contact fields.

This format is suitable for opening in spreadsheet applications such as Microsoft Excel.

### Option 5 — Exit

Close the database connection and terminate the application.

---

## Database Structure

ApolloCRM uses SQLite for lightweight and persistent local data storage.

The database contains a `leads` table.

| Column | Description |
|--------|-------------|
| id | Unique record identifier |
| genre | Gender, when available |
| prenom | First name |
| nom | Last name |
| entreprise | Organization name |
| pays | Country |
| ville | City |
| titre_poste | Professional job title |
| secteur | Industry |
| telephone_perso | Direct or mobile phone number, when available |
| telephone_standard | Company or office phone number |
| email | Professional email address, when available |
| linkedin | LinkedIn profile URL |
| date_ajout | Record creation timestamp |

### Duplicate Prevention

Before inserting a new contact, the application checks whether a matching record already exists.

The matching strategy uses:

- Email address when available.
- First name, last name, and organization when no email is available.

Duplicate records are skipped during insertion.

---

## Apollo.io API Integration

The application communicates with the Apollo.io REST API.

### API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/mixed_companies/search` | Organization discovery |
| `/people/search` | Professional contact search |
| `/people/match` | Individual contact enrichment |

API requests use an API key transmitted through the `X-Api-Key` header.

### API Limitations

The availability of Apollo.io endpoints depends on the user's subscription, account permissions, and current API policies.

The application includes:

- HTTP response status checks.
- Error messages for unsuccessful requests.
- Special handling for restricted contact-search requests.
- An alternative individual enrichment workflow.
- Short delays between selected API requests.

These mechanisms do not guarantee access to paid endpoints or prevent all rate-limit errors.

Refer to the official Apollo.io API documentation for current endpoint availability and usage restrictions.

---

## Data Processing

The application transforms Apollo.io responses into structured contact records.

The processing pipeline includes:

**1. Extraction**

Retrieve available fields from API responses.

**2. Normalization**

Convert raw response values into a consistent contact structure.

**3. Validation**

Handle missing or unavailable fields using empty values.

**4. Deduplication**

Check for existing contacts before insertion.

**5. Persistence**

Save valid records in the local SQLite database.

**6. Export**

Generate structured CSV files from stored records.

---

## Security & Privacy

ApolloCRM is intended for educational purposes and authorized professional data processing.

### Security Practices

- API credentials are excluded from version control.
- Local SQLite databases are not committed to GitHub.
- Generated CSV exports are excluded from the repository.
- Python virtual environments and cache files are ignored.

### Responsible Usage

Users are responsible for:

- Following Apollo.io's terms and API policies.
- Respecting applicable privacy and data protection regulations.
- Processing professional contact information lawfully.
- Protecting exported contact datasets.
- Avoiding unauthorized collection or distribution of personal information.

---

## Potential Improvements

Possible future enhancements include:

- Environment-variable-based API configuration.
- Advanced search filters.
- Contact editing and deletion.
- Database-level uniqueness constraints.
- Improved rate-limit handling and retry mechanisms.
- Automated tests.
- Logging and monitoring.
- A graphical dashboard.
- Additional export formats.

These features are potential improvements and are not part of the current implementation.

---

## Project Context

This application was developed as a **personal Python project** to strengthen practical skills in:

- REST API integration.
- HTTP request handling.
- Data extraction and transformation.
- Relational database management.
- Data persistence.
- CSV generation.
- Command-line application development.
- API error handling.

---

## Author

**Ahmed Ouassim Boulouh**

Computer Science Engineering Student

GitHub: [@simou-blh](https://github.com/simou-blh)

---

<div align="center">

### ApolloCRM — Contact Extractor

**Discover. Organize. Export.**

Built with Python and SQLite.

</div>