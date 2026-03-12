---
paths:
  - "master_supporting_docs/**"
---

# Robust PDF Processing

## The Safe Processing Workflow

**Step 1: Receive PDF Upload**
- User uploads PDF to `master_supporting_docs/supporting_papers/`
- Claude DOES NOT attempt to read it directly

**Step 2: Check PDF Properties**
```bash
pdfinfo paper_name.pdf | grep "Pages:"
ls -lh paper_name.pdf
```

**Step 3: Targeted Search First (Token-Efficient)**

Before splitting, try targeted text searches to find relevant sections without loading the full PDF into context.

**On Windows (pdftotext + grep):**
```bash
# Convert to text and search (pdftotext is available via mingw64/poppler)
pdftotext paper_name.pdf - | grep -n -i "identification strategy"

# Search with context (3 lines before/after)
pdftotext paper_name.pdf - | grep -n -i -C 3 "treatment effect"

# Search a specific page range only
pdftotext -f 10 -l 20 paper_name.pdf - | grep -i "event study"

# Search all PDFs in a directory
for f in master_supporting_docs/supporting_papers/*.pdf; do
  echo "=== $f ==="; pdftotext "$f" - | grep -l -i "difference.in.difference" 2>/dev/null
done
```

**On Linux/Mac (pdfgrep — faster, native PDF search):**
```bash
pdfgrep -n -i "identification strategy" paper_name.pdf
pdfgrep -n -C 2 "treatment effect" paper_name.pdf
pdfgrep -r -l "event study" master_supporting_docs/supporting_papers/
```

**With Python (pdfplumber — best for tables/structured content):**
```python
import pdfplumber
with pdfplumber.open("paper_name.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and "treatment effect" in text.lower():
            print(f"Page {i+1}: match found")
```

If targeted search finds what you need, read only those specific pages with the Read tool (e.g., `pages: "5-7"`). Skip to Step 6.

**Step 4: Create Subfolder and Split (for full processing)**

Only split when you need to process the entire document:

```bash
mkdir -p paper_name/

for i in {0..9}; do
  start=$((i*5 + 1))
  end=$(((i+1)*5))
  gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
     -dFirstPage=$start -dLastPage=$end \
     -sOutputFile="paper_name/paper_name_p$(printf '%03d' $start)-$(printf '%03d' $end).pdf" \
     paper_name.pdf 2>/dev/null
done
```

**Step 5: Process Chunks Intelligently**
- Read chunks ONE AT A TIME using the Read tool
- Extract key information from each chunk
- Build understanding progressively
- Don't try to hold all chunks in working memory

**Step 6: Selective Deep Reading**
- After scanning all chunks (or after pdfgrep narrows your targets), identify the most relevant sections
- Only read those sections in detail
- Skip appendices, references, or less relevant sections unless needed

## Converting Frequently-Referenced PDFs to Markdown

For docs you'll reference repeatedly (e.g., Stata manuals), convert to markdown once to avoid re-processing:

```bash
# Convert PDF to markdown with pandoc
pandoc paper_name.pdf -t markdown -o paper_name.md

# Or extract specific pages first, then convert
gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
   -dFirstPage=1 -dLastPage=20 \
   -sOutputFile=paper_name_excerpt.pdf paper_name.pdf
pandoc paper_name_excerpt.pdf -t markdown -o paper_name_excerpt.md
```

Store converted markdown in the same subfolder as the source PDF.

## Error Handling Protocol

**If a chunk fails to process:**
1. Note the problematic chunk (e.g., "Chunk p021-025 failed")
2. Try splitting into 1-2 page pieces
3. If still failing, skip and document the gap

**If splitting fails:**
1. Check if Ghostscript is installed: `gs --version`
2. Try alternative: `pdftk paper.pdf burst output paper_%03d.pdf`
3. If all else fails, ask user to upload specific page ranges manually
