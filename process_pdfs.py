import os
import json
import fitz 
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def extract_sections_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        sections = []
        page_num = 1
        
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            font_size = span["size"]
                            flags = span.get("flags", 0)
                            is_bold = flags & 2**4
                            
                            # Identify section headings
                            if (len(text) > 3 and len(text) < 200 and 
                                (font_size > 12 or is_bold) and 
                                not text.endswith('.') and 
                                (text.isupper() or text[0].isupper())):
                                
                                sections.append({
                                    "document": os.path.basename(pdf_path),
                                    "section_title": text,
                                    "page_number": page_num,
                                    "content": text,  
                                    "full_path": pdf_path  
                                })
            
            page_num += 1
        
        doc.close()
        return sections
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

def rank_sections_by_relevance(sections, persona, job_to_be_done):
    """Rank sections by relevance to persona and job"""
    if not sections:
        return []
    
   
    corpus = [section["content"] for section in sections]
    
 
    query = f"{persona} {job_to_be_done}"
    
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(corpus + [query])
    
    
    query_vector = tfidf_matrix[-1]
    similarities = cosine_similarity(query_vector, tfidf_matrix[:-1]).flatten()
    
 
    ranked_sections = []
    for i, section in enumerate(sections):
        ranked_sections.append({
            **section,
            "importance_rank": int(similarities[i] * 100) 
        })
    
    
    ranked_sections.sort(key=lambda x: x["importance_rank"], reverse=True)
    return ranked_sections

def extract_subsections(ranked_sections):
    """Extract detailed subsections from top-ranked sections"""
    subsection_analysis = []
    
    for section in ranked_sections[:5]:  
        pdf_path = section["full_path"]  
        try:
            doc = fitz.open(pdf_path)
            page = doc[section["page_number"] - 1]
            
            
            text_blocks = page.get_text("dict")["blocks"]
            refined_text = ""
            
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(text) > 10:
                                refined_text += text + " "
            
            doc.close()
            
            subsection_analysis.append({
                "document": section["document"],
                "refined_text": refined_text[:500] + "..." if len(refined_text) > 500 else refined_text,
                "page_number": section["page_number"]
            })
            
        except Exception as e:
            print(f"Error extracting subsections from {pdf_path}: {e}")
    
    return subsection_analysis

def process_collections():
    base_dir = Path("/app")
    output_dir = base_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)


    collections = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("Collection_")]
    if not collections:
        print("No collection folders found.")
        return

    for collection in collections:
        print(f"Processing {collection.name}")
        input_dir = collection / "PDFs"
        if not input_dir.exists():
            print(f"No PDFs folder in {collection.name}, skipping.")
            continue
        pdf_files = list(input_dir.glob("*.pdf"))
        if len(pdf_files) < 3:
            print(f"Error: Found only {len(pdf_files)} PDFs in {collection.name}. Minimum 3 required.")
            continue
   
        persona = "Default Persona"
        job_to_be_done = "Default Job"
        input_json = collection / "challenge1b_input.json"
        if input_json.exists():
            with open(input_json, "r", encoding="utf-8") as f:
                input_data = json.load(f)
                persona = input_data.get("persona", {}).get("role", persona)
                job_to_be_done = input_data.get("job_to_be_done", {}).get("task", job_to_be_done)
        
        all_sections = []
        for pdf_file in pdf_files:
            sections = extract_sections_from_pdf(str(pdf_file))
            all_sections.extend(sections)
        if not all_sections:
            print(f"No sections extracted from PDFs in {collection.name}.")
            continue
        
        ranked_sections = rank_sections_by_relevance(all_sections, persona, job_to_be_done)
  
        subsection_analysis = extract_subsections(ranked_sections)
      
        input_data = {
            "documents": [{"filename": os.path.basename(str(p)), "title": os.path.splitext(os.path.basename(str(p)))[0]} for p in pdf_files],
            "persona": {"role": persona},
            "job_to_be_done": {"task": job_to_be_done}
        }
     
        output_data = {
            "metadata": {
                "input_documents": [doc["filename"] for doc in input_data["documents"]],
                "persona": persona,
                "job_to_be_done": job_to_be_done
            },
            "extracted_sections": ranked_sections,
            "subsection_analysis": subsection_analysis
        }
      
        output_file = output_dir / f"output_{collection.name}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
       
        input_file = output_dir / f"input_{collection.name}.json"
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f, indent=2, ensure_ascii=False)
        print(f"Processed {len(pdf_files)} PDFs in {collection.name}")
        print(f"Extracted {len(all_sections)} sections in {collection.name}")
        print(f"Ranked {len(ranked_sections)} sections in {collection.name}")
        print(f"Generated {len(subsection_analysis)} subsection analyses in {collection.name}")

if __name__ == "__main__":
    print("Starting multi-collection PDF analysis (all collections)")
    process_collections()
    print("Completed multi-collection PDF analysis (all collections)") 