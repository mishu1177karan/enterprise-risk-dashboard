# 🛡️ Enterprise Risk Dashboard

> A Streamlit-based interactive risk management platform built on ERM best practices.  
> Developed as part of a Risk Management internship project at Aviva India.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)
![Domain](https://img.shields.io/badge/Domain-Insurance%20%7C%20ERM-navy)

---

## 📌 Overview

This project implements a fully functional **Enterprise Risk Management (ERM) dashboard** using Python and Streamlit. It allows risk managers to:

- **Log and track risks** across strategic, operational, financial, cyber, compliance, and CAT categories
- **Visualise risk exposure** on an interactive 5×5 heat map
- **Prioritise risks** by score (Likelihood × Impact) with colour-coded severity levels
- **Track mitigation status** across the risk lifecycle
- **Export professional PDF reports** for board and management submission

---

## 🏗️ ERM Framework

This dashboard is aligned with globally recognised ERM frameworks:

| Framework | Alignment |
|-----------|-----------|
| **ISO 31000:2018** | Risk identification, assessment, treatment, and monitoring |
| **COSO ERM 2017** | Integration of risk with strategy and performance |
| **IRDAI Guidelines** | Risk categories relevant to Indian insurance regulation |
| **Solvency II / ORSA** | Quantitative risk scoring and capital linkage concepts |

### Risk Scoring Matrix

The dashboard uses a standard **5×5 Likelihood × Impact** matrix:

```
Score = Likelihood (1–5) × Impact (1–5)

 ≥ 16  →  CRITICAL  (immediate escalation required)
 10–15 →  HIGH      (senior management attention)
  5–9  →  MEDIUM    (management monitoring)
  < 5  →  LOW       (routine monitoring)
```

### Risk Categories Covered

| Category | Examples |
|----------|----------|
| Strategic | Market disruption, M&A failure, product strategy |
| Operational | Process failure, fraud, business continuity |
| Financial | Adverse claims, investment losses, liquidity |
| Compliance / Regulatory | IRDAI non-compliance, GDPR, AML/KYC |
| Cyber / Technology | Data breach, ransomware, system outage |
| Reputational | Mis-selling, brand damage, social media |
| Environmental / CAT | Flood, earthquake, cyclone exposure |
| HR / People | Key person loss, talent shortage, misconduct |
| Third-Party / Supply Chain | TPA failure, vendor risk, outsourcing |

---

## 🚀 Features

### 📊 Dashboard
- Live KPI metrics (total, critical, high, mitigated counts)
- Interactive **5×5 Risk Heat Map** (Plotly) with risk IDs plotted by score
- **Donut chart** — risk distribution by category
- **Priority bar ranking** with colour-coded score bars
- Mitigation status bar chart

### ➕ Add Risk
- Form-based risk entry with all ERM fields
- Real-time risk score preview before submission
- Auto-generated Risk ID (R001, R002 …)

### 📋 Risk Register
- Full tabular risk register with multi-column filters
- Edit mitigation status, likelihood, impact, and controls inline
- Delete risks from the register

### 📄 Export Report (PDF)
- Auto-generated **board-ready PDF** using `fpdf2`
- Includes: Executive Summary, KPI table, Top 10 risk priority table, full detailed risk profiles
- Organisation name, date, and prepared-by customisation
- Confidentiality footer

---

## 📂 Project Structure

```
enterprise-risk-dashboard/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
└── assets/                 # (optional) screenshots / logos
    └── screenshot.png
```

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/enterprise-risk-dashboard.git
cd enterprise-risk-dashboard

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📸 Screenshots

| Dashboard | Heat Map | PDF Report |
|-----------|----------|------------|
| KPI cards + heat map | 5×5 likelihood-impact matrix | Board-ready PDF export |

---

## 💡 Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Risk Quantification** | Likelihood × Impact scoring with 4-tier classification |
| **Risk Heat Map** | Plotly heatmap with annotated cell-level risk IDs |
| **IBNR Thinking** | Risk register includes date_added for trend analysis |
| **Mitigation Lifecycle** | 5-stage status: Not Started → In Progress → Implemented / Accepted / Transferred |
| **Escalation Triggers** | Critical risks auto-flagged for board visibility |
| **Reporting** | FPDF2-based PDF generation mimicking management risk reports |

---

## 🔗 Relevance to Insurance & Risk Management

This project directly applies concepts from:
- **PGDM (Liability Insurance)** — CGL, D&O, Cyber, and Workers Compensation risk categories included in sample data
- **Aviva Risk Management internship** — enterprise risk register format aligned with insurer ERM practices
- **IRDAI Solvency / ORSA guidelines** — risk scoring aligned with regulatory capital thinking

---

## 📈 Possible Extensions

- [ ] Connect to a SQLite / PostgreSQL database for persistence
- [ ] Add Monte Carlo simulation for financial risk quantification
- [ ] Integrate CAT model outputs (PML, AAL) as risk scores
- [ ] Role-based access (Risk Owner vs CRO view)
- [ ] Email alert when a new Critical risk is added
- [ ] Time-series view of risk score evolution

---

## 🧑‍💻 Author

Mishu Kumar 

---

## 📄 License

MIT License — free to use, modify, and distribute.
