# Challenge 1b: Multi-Collection PDF Analysis

## Overview
This repository provides a generic, modular solution for Challenge 1b of the Adobe India Hackathon 2025. It extracts and ranks relevant sections from multiple PDFs based on a given persona and job-to-be-done, outputting structured JSON for downstream use.

## Approach Explanation
- **Section Extraction:** Uses PyMuPDF to parse each PDF, extracting candidate headings/sections using heuristics (font size, boldness, text patterns).
- **Relevance Ranking:** Applies TF-IDF vectorization and cosine similarity (via scikit-learn) to rank sections by their relevance to the persona and job-to-be-done.
- **Subsection Analysis:** For the top-ranked sections, extracts and summarizes nearby text for deeper insight.
- **Generic & Modular:** Handles any collection, persona, or job without hardcoding or file-specific logic.
- **Offline & Fast:** All processing is local, with no network calls, and optimized for ≤60s runtime for 3–10 PDFs.

## Compliance & Constraints
- No internet/network calls are made at any stage.
- No hardcoded file names, paths, or logic.
- Model size is well below 1GB (no large ML model used).
- Runs on CPU (amd64), tested for 8 CPUs/16GB RAM.
- Output strictly matches the required JSON schema.

## Libraries Used
- **PyMuPDF (fitz):** PDF parsing and text extraction.
- **scikit-learn:** TF-IDF vectorization and similarity ranking.
- **numpy:** Efficient numerical operations.
- **Python Standard Library:** File and JSON operations.

## How to Build and Run
```bash
# Build the Docker image
docker build --platform=linux/amd64 -t pdf-analyst .

# Run the container (ensure input PDFs and input JSON are in /app/input)
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-analyst
```

## Troubleshooting & FAQ
- **Q:** Output JSON is missing or incomplete?
  **A:** Ensure at least 3 PDFs are present in `/app/input` and input JSON is correctly formatted.
- **Q:** Docker build fails on ARM?
  **A:** Use the `--platform=linux/amd64` flag as shown above.
- **Q:** Output not generated?
  **A:** Ensure `/app/output` is writable and `/app/input` contains the required files.

## Modularity & Extensibility
- The code is modular: section extraction, ranking, and sub-section analysis are separate functions.
- Easily extendable for new personas, jobs, or more advanced NLP techniques.
- Designed for easy integration into future hackathon rounds.

---

**Note:** This solution is fully generic, modular, and hackathon-compliant. No internet or file-specific logic is used. All dependencies are open source and installed within the Docker image. 