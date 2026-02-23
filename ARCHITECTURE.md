# 🏗️ Architecture

End-to-end design of the ATO tax automation pipeline across all milestones.  
All services self-hosted on **OCI Oracle Always Free ARM VM** (Ampere A1, 4 OCPU / 24GB RAM).

---

## M3 Processing Pipeline

```mermaid
flowchart LR
    A["PDF or HTML email"] --> B & C

    subgraph B["screenshotter — Puppeteer :8002"]
        B1["render headlessly"] --> B2["export PNG"]
    end

    subgraph C["pdf-service — PyMuPDF :8001"]
        C1["text extraction fallback"]
    end

    B --> D
    C --> D

    subgraph D["Vision AI — Gemini 1.5 Flash"]
        D1["read PNG like a human"] --> D2["vendor / amount / ato_code / rationale"]
    end

    style B fill:#f3e5f5,stroke:#8e24aa
    style C fill:#e8f5e9,stroke:#43a047
    style D fill:#e8eaf6,stroke:#3949ab
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
