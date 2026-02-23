# 🗺️ MILESTONES

Progress tracker for the ATO tax automation pipeline.

---

## ✅ Milestone 1 — MVP "Wide Net" Triage (COMPLETE)

**Goal:** Catch everything, miss nothing. Notification-only pipeline.

- [x] Gmail Trigger polling every 60 seconds (unread only)
- [x] Raw HTML/text extraction from complex email bodies (AliExpress, Invoice2go)
- [x] OpenRouter AI triage with probability scoring
- [x] JSON parsing via Code Node
- [x] HTML summary email → taxdtran@gmail.com
- [x] Auto-mark-as-read (dedup protection)

**Limitation:** $0 amounts when invoice is PDF-only. No database. Emails sent for every catch.

---

## 🔄 Milestone 2 — PDF Extraction + Google Sheets Logging (IN PROGRESS)

**Goal:** Extract real dollar amounts from PDF attachments. Write to spreadsheet silently.

- [ ] Deploy OCI VM (ARM A1, Ubuntu 22.04)
- [ ] Bootstrap Docker + n8n + pdf-service via `bootstrap.sh`
- [ ] `pdf-service` FastAPI container live on port 8001
- [ ] n8n: conditional branch — has attachment? → call pdf-service
- [ ] n8n: merge PDF text into AI prompt
- [ ] n8n: Google Sheets node — append row on `potential_deduction == true`
- [ ] n8n: Gmail alert ONLY on `status == "Requires Manual Check"`
- [ ] Google Sheet columns A-J defined and tested
- [ ] End-to-end test: Biggins Home Services invoice → Sheet row

**Target:** Silent background logging. Only noisy when human needed.

---

## 🔮 Milestone 3 — Strict ATO Compliance + Depreciation Engine

**Goal:** Replace "Triage Nurse" AI with "Expert Accountant" AI.

- [ ] Swap to multimodal model (Gemini 1.5 Pro or Claude Sonnet via API)
- [ ] Feed raw PDF binary directly to vision model (bypass text extraction for scanned PDFs)
- [ ] Redesign system prompt: strict ATO 2024-25 ruleset
  - D5: IT equipment, software subs, homelab
  - Item 21: Rental property repairs/maintenance/insurance/rates
  - D4: Self-education if relevant
- [ ] Depreciation flag: assets > $300 AUD → flag `depreciation_required: true`
- [ ] Structured ATO rationale field: "Why this is deductible under TR 2023/1..."
- [ ] Reject non-deductibles confidently (personal groceries, etc.)
- [ ] Google Sheets: add Depreciation Flag column + ATO Rationale column
- [ ] Notion DB as alternative/additional logging target

---

## 🧮 Milestone 4 — EOFY Reporting

**Goal:** One-click tax summary at June 30.

- [ ] n8n scheduled workflow: runs June 30 each year
- [ ] Reads all rows from Google Sheet for current FY
- [ ] Groups by ATO code (D5 total, Item 21 total)
- [ ] Generates formatted PDF report (or Google Doc)
- [ ] Emails report to accountant-ready address
- [ ] Depreciation schedule summary

---

## 📊 Success Metrics

| Milestone | Key Signal |
|-----------|-----------|
| M1 ✅ | Receives email alerts for Biggins, AliExpress |
| M2 | Google Sheet has rows with real $ amounts from PDFs |
| M3 | Zero false positives sent to accountant |
| M4 | EOFY report generated automatically |
