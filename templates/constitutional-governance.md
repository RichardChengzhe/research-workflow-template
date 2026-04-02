# Project Constitution

Formalize which rules are immutable vs. flexible. Each project fills in its own articles (3-7 max).

---

## Articles (Immutable Unless Formally Amended)

### Article 1: [Data Integrity]

[Example: `data/raw/` is READ-ONLY. No exceptions.]

### Article 2: [Plan-First Threshold]

[Example: Any task touching >3 files or >1 hour requires plan mode.]

### Article 3: [Quality Gate]

[Example: Nothing commits below 80/100.]

### Article 4: [Verification Standard]

[Example: Every script run produces a log. Every log gets read.]

### Article 5: [Single Source of Truth]

[Example: manuscript/main.tex is authoritative. Code results must match paper claims.]

---

## Amendment Process

- **Permanent amendment:** "Amending Article X because [reason]" — requires explicit user confirmation, documented in this file
- **One-time exception:** "Overriding Article X for this task because [reason]" — state the scope, does not modify this file

---

## Preferences (Flexible)

These can be overridden without formal process:

- [Example: Prefer PDF figures over PNG]
- [Example: Use 2 decimal places for coefficients]
- [Example: Run full pipeline before PR]
