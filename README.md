# 🧾 tax-automation

> **Automated ATO Tax Deduction Pipeline** — OCI Oracle Free VM + n8n + PDF Microservice

A self-hosted, private pipeline that intercepts Gmail receipts, extracts PDF invoice data, triages them against ATO rules, and logs verified deductions to Google Sheets — fully automated, zero cloud costs (OCI Always Free tier).

---

## 📁 Repo Tree

```
tax-automation/
├── README.md                        ← You are here
├── MILESTONES.md                    ← V1 → V2 → V3 roadmap
├── TODO.md                          ← Active task checklist
├── .env.example                     ← All secrets template (never commit .env)
├── .gitignore
│
├── docker-compose.yml               ← Runs n8n + pdf-service together
│
├── scripts/
│   ├── bootstrap.sh                 ← ONE-SHOT OCI VM setup (run as ubuntu user)
│   └── healthcheck.sh               ← Verifies all services are up
│
├── pdf-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py                      ← FastAPI: accepts PDF → returns extracted text/JSON
│
└── n8n/
    └── workflows/
        ├── tax-triage-v1.json       ← Current MVP (email → AI → notify)
        └── tax-pipeline-v2.json     ← Target (+ PDF parsing + Google Sheets write)
```

---

## 🏗️ Architecture

```
Gmail (unread emails, every 60s)
    │
    ▼
n8n [Gmail Trigger]
    │
    ├─ Has PDF attachment? ──YES──► n8n [HTTP → pdf-service:8001/extract]
    │                                        │
    │                                        ▼
    │                               FastAPI (PyMuPDF)
    │                               Returns: { text, pages, amounts_found }
    │                                        │
    └─────────────────────────────────────────┤
                                             ▼
                                    n8n [HTTP → OpenRouter AI]
                                    (Arcee / Gemini / Claude)
                                             │
                                             ▼
                                    n8n [Code Node: parse JSON]
                                             │
                                    ┌────────┴─────────┐
                              potential?              not potential
                              probability > 10%       skip
                                    │
                                    ▼
                           n8n [Google Sheets]   ← LOGS ROW
                                    │
                           status == "Requires Manual Check"?
                                    │
                                   YES
                                    ▼
                           n8n [Gmail: send alert]
                                    │
                                    ▼
                           n8n [Mark email as read]
```

**OCI Free Tier Resources Used:**
- 1x AMD VM.Standard.E2.1.Micro (n8n + pdf-service via Docker)
- OR 1x Ampere A1 ARM VM (4 OCPU / 24GB RAM — much better, use this)

---

## 🚀 Quick Start (Bootstrap)

### 1. Provision your OCI VM

In OCI Console:
- Shape: `VM.Standard.A1.Flex` → 4 OCPU, 24GB RAM (Always Free ARM)
- OS: Ubuntu 22.04
- Open ports: 5678 (n8n), 8001 (pdf-service) in Security List

### 2. SSH in and run bootstrap

```bash
ssh ubuntu@YOUR_OCI_IP
git clone https://github.com/YOU/tax-automation.git
cd tax-automation
cp .env.example .env
nano .env                    # Fill in your secrets
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

### 3. Verify everything is up

```bash
./scripts/healthcheck.sh
```

### 4. Import n8n workflow

- Open `http://YOUR_OCI_IP:5678`
- Settings → Import from file → `n8n/workflows/tax-pipeline-v2.json`

### 5. Set up Google Sheets

- Create a Sheet named `ATO Deductions 2025`
- Share it with your Google Service Account email
- Copy the Sheet ID from the URL into `.env`

---

## 🔐 Secrets (.env.example)

See `.env.example` for all required variables. **Never commit `.env`.**

---

## 📡 PDF Service API

Once running, test it:

```bash
curl -X POST http://localhost:8001/extract \
  -F "file=@/path/to/invoice.pdf" \
  | jq .
```

Returns:
```json
{
  "text": "Full extracted text...",
  "page_count": 2,
  "amounts_aud": [125.00, 450.00],
  "vendor_hint": "Biggins Home Services"
}
```

---

## 🧩 n8n Google Sheets Node (Drop-in JSON)

Import this node into your workflow after the `Code in JavaScript` node.  
**Only fires when `potential_deduction == true`.**

See `n8n/workflows/tax-pipeline-v2.json` for the complete updated workflow.

### Google Sheets Column Schema

| Col | Field | Example |
|-----|-------|---------|
| A | Date Logged | 2025-07-01 |
| B | Vendor | Biggins Home Services |
| C | Amount (AUD) | 450.00 |
| D | ATO Code | Item 21 |
| E | Probability | 90% |
| F | Status | Verified |
| G | AI Reason | Plumbing repair rental property |
| H | Source Email Subject | Invoice #1042 |
| I | Depreciation Flag | FALSE |
| J | Financial Year | FY2024-25 |

---

## 🔧 Updating

```bash
git pull
docker-compose pull
docker-compose up -d
```
