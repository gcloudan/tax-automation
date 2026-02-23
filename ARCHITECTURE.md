# 🏗️ Architecture

End-to-end design of the ATO tax automation pipeline across all milestones.  
All services self-hosted on **OCI Oracle Always Free ARM VM** (Ampere A1, 4 OCPU / 24GB RAM).

---

## M3 Processing Pipeline

```mermaid
flowchart TD
    A["Incoming email"] --> B{What type?}

    B -->|plain text only| C["raw text"]
    B -->|HTML or images| D["Puppeteer :8002 — render to PNG"]
    B -->|PDF attached| E["PDF binary"]
    B -->|link to PDF| F{Public URL?}

    F -->|yes| G["n8n HTTP GET — download PDF"] --> E
    F -->|auth required| H["⚠️ Requires Manual Download"]

    C --> I["nvidia/nemotron-nano-12b-v2-vl — image to text extraction only"]
    D --> I
    E --> I

    I -->|"raw extracted text: vendor / date / line items / total"| J["Gemini 2.5 Flash — ATO tax judgment"]

    style D fill:#f3e5f5,stroke:#8e24aa
    style I fill:#e8f5e9,stroke:#43a047
    style J fill:#e8eaf6,stroke:#3949ab
    style H fill:#ffebee,stroke:#e53935
```

---

## Google Sheets Schema

| Col | Field | Source | Example |
|-----|-------|--------|---------|
| A | Date Logged | Code Node | 2025-07-12 |
| B | Vendor | Vision AI | eBay / Biggins |
| C | Amount (AUD) | Vision AI | 28.00 |
| D | ATO Code | Vision AI | D5 / Item 21 |
| E | Probability | Vision AI | 90% |
| F | Status | Vision AI | Verified |
| G | AI Reason | Vision AI | NVMe SSD for homelab server |
| H | ATO Rationale | Vision AI (M3) | Deductible under TR 2023/1... |
| I | Source Subject | Code Node | Fwd: Order confirmed: WD SN740 |
| J | Depreciation Flag | Vision AI | FALSE |
| K | Financial Year | Code Node | FY2024-25 |

---

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| n8n | 5678 | Workflow UI + orchestrator |
| pdf-service | 8001 | PyMuPDF text extraction (M2) |
| screenshotter | 8002 | Puppeteer HTML/PDF → PNG (M3) |

---

## Why Vision Over HTML Parsing

| Approach | eBay rich HTML | Image amounts | Scanned PDF | Forwarded chain | Vendor changes template |
|----------|:-:|:-:|:-:|:-:|:-:|
| Regex / text strip | ❌ | ❌ | ❌ | ❌ | ❌ |
| PyMuPDF text extract | ✅ (PDF only) | ❌ | ❌ | ❌ | ✅ |
| Browser render → Vision AI | ✅ | ✅ | ✅ | ✅ | ✅ |
