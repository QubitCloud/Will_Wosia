# Wosia Wangu — Tanzania Will Form System

A bilingual (Swahili/English) web application for capturing Last Will & Testament
information compliant with Tanzania's Law of Succession Act (Cap. 865).

---

## Features

- **Bilingual** — Full Swahili + English toggle, instant switch
- **6-Step wizard** — Testator → Assets → Beneficiaries → Executor → Wishes → Review
- **Tanzania-specific** — NIDA ID, Right of Occupancy land law, Islamic Will option,
  Tanganyika Law Society witness requirements
- **Dynamic asset blocks** — Add unlimited properties, bank accounts, vehicles
- **Beneficiary shares** — Percentage-based allocation per beneficiary
- **Signature block** — Pre-formatted for advocate + 2 witnesses (Sec. 11, Cap. 865)
- **Printable review** — Clean summary page with legal disclaimer

---

## Setup

```bash
cd wosia_app
pip install -r requirements.txt
python app.py
```

Open: http://localhost:5050

---

## Legal Compliance References

| Requirement                  | Legal Basis                              |
|------------------------------|------------------------------------------|
| Testator must be 18+         | Law of Succession Act, Cap. 865, Sec. 9  |
| Two adult, non-beneficiary   | Law of Succession Act, Cap. 865, Sec. 11 |
| witnesses required           |                                          |
| Islamic Will option          | Law of Succession Act, Cap. 865, Sec. 2  |
| Land = Right of Occupancy    | Land Act, Cap. 113                       |
| Minor children → trustee     | Law of Succession Act, Cap. 865, Sec. 29 |
| Advocate must be registered  | Advocates Act, Cap. 341                  |

---

## Data

Submissions saved as JSON in `submissions/` folder.
Format: `will_<REF_ID>.json`

---

## Recommended Extensions

1. **PDF export** — Use `weasyprint` or `pdfkit` to generate printable PDF
2. **Email confirmation** — Send ref number via Beem Africa SMS API
3. **Lawyer directory** — Link to TLS-registered advocate lookup
4. **AI assistant** — Embed Claude API for guided Q&A on will sections
