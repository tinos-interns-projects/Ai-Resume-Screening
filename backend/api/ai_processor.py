import pdfplumber
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text(file_path):
    """Extract text from PDF, DOCX, or TXT"""
    text = ""
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    return text

def clean_text(text):
    """Remove special chars, extra spaces, lowercase"""
    if not text:
        return ""
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def calculate_match_score(job_desc, resume_text):
    """TF-IDF + Cosine Similarity → Returns 0.0 to 100.0"""
    job_clean = clean_text(job_desc)
    resume_clean = clean_text(resume_text)
    
    if not job_clean or not resume_clean:
        return 0.0
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([job_clean, resume_clean])
    
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 2)

def extract_candidate_name(text):
    """Try to extract candidate name from resume text"""
    if not text:
        return "Unknown Candidate"
    
    text = text.strip()
    lines = text.split('\n')
    
    for line in lines[:5]:
        line = line.strip()
        if not line:
            continue
        
        # Pattern 1: Two capitalized words (e.g., "John Doe")
        name_match = re.match(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)', line)
        if name_match:
            return name_match.group(1)
        
        # Pattern 2: All caps name (e.g., "JOHN DOE")
        caps_match = re.match(r'^([A-Z]{2,}\s+[A-Z]{2,})', line)
        if caps_match:
            return caps_match.group(1).title()
            
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) < 50 and not any(x in line.lower() for x in ['email', 'phone', '@']):
            return line
            
    return "Unknown Candidate"