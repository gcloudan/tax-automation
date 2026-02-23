# ✅ TODO — Active Tasks

> Keep this file updated. Move done items to MILESTONES.md when a milestone closes.

---

## 🔥 This Week (Milestone 2 Sprint)

- [ ] **Provision OCI VM** — ARM A1.Flex, 4 OCPU / 24GB, Ubuntu 22.04
  - Open Security List ports: 5678, 8001
  - Note static IP or set up DDNS

- [ ] **Run `bootstrap.sh`** — installs Docker, clones repo, starts services
  - Verify: `docker ps` shows `n8n` and `pdf-service` containers

- [ ] **Test pdf-service manually**
  ```bash
  curl -X POST http://YOUR_IP:8001/extract -F "file=@test_invoice.pdf" | jq .
  ```

- [ ] **Import `tax-pipeline-v2.json`** into n8n
  - Update Google Sheets credentials
  - Update OpenRouter API key in HTTP Request node

- [ ] **Create Google Sheet** `ATO Deductions 2025`
  - Columns A-J as per README schema
  - Share with Google Service Account

- [ ] **End-to-end test**
  - Forward a Biggins invoice email to your Gmail
  - Confirm: row appears in sheet, NO email sent (status = Verified)
  - Forward an ambiguous email
  - Confirm: email alert sent (status = Requires Manual Check)

---

## 📋 Backlog

- [ ] Set up Nginx reverse proxy + SSL (Certbot) for n8n HTTPS
- [ ] Add `HEALTHCHECK` to Docker services
- [ ] Rotate OpenRouter API key (current key is in workflow JSON — move to n8n env var)
- [ ] Investigate Gemini 1.5 Flash free tier for multimodal PDF reading (M3 prep)
- [ ] Add `financial_year` auto-detection to Code Node (auto-fills FY2024-25 vs FY2025-26)
- [ ] Test with scanned PDF (non-text) — verify fallback behaviour
- [ ] Add Slack/Telegram notification option as alternative to email alerts
- [ ] Document Google OAuth setup for Sheets credential

---

## 🐛 Known Issues

| Issue | Workaround | Fix |
|-------|-----------|-----|
| Free AI model can't read PDFs | Use pdf-service text extraction first | M2 |
| API key exposed in workflow JSON | Manually set in n8n env | Backlog |
| No retry if AI returns malformed JSON | Manual re-run in n8n | M3 |

---

## 💡 Ideas / Future

- Telegram bot: `/tax status` → returns running totals by ATO code
- Receipt image → OCR → deduction (for physical receipts photographed)
- Compare year-over-year deduction totals in dashboard
