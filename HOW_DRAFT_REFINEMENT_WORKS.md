# 📚 How Draft Refinement Works - Complete Technical Guide

## 🎯 **ANSWER: Library AND API**

Draft Refinement uses **BOTH**:
1. **Local Python Libraries** (for file processing)
2. **Google Gemini API** (for AI-powered text refinement)

---

## 🔄 **COMPLETE WORKFLOW**

### **Phase 1: User Input** 👤
```
User Action Options:
├─ Paste text directly
└─ Upload file (PDF, DOCX, TXT)
```

### **Phase 2: Frontend Processing** 🌐
```javascript
// File: frontend/src/components/panels/DraftRefinementPanel.tsx

const API_URL = "http://localhost:8000"

// For text:
POST ${API_URL}/api/draft-conference/refine
Body: {
  text: "Your draft text here...",
  focus_areas: ["clarity", "grammar"],
  change_level: "moderate"
}

// For file:
POST ${API_URL}/api/draft-conference/refine-file
Body: FormData with file attachment
```

### **Phase 3: Backend File Processing** 📄 (LOCAL LIBRARIES)

```python
# File: backend/app/services/document_processor.py

class DocumentProcessor:
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF/DOCX/TXT"""
        
        # 1. Read file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 2. Detect type and route
        if file.endswith('.pdf'):
            return self._process_pdf(content)      # Uses pypdf library
        elif file.endswith('.docx'):
            return self._process_docx(content)     # Uses python-docx library
        elif file.endswith('.txt'):
            return self._process_text(content)     # Built-in Python
```

**Libraries Used:**
- **`pypdf`** - Extracts text from PDF files
  ```python
  import pypdf
  reader = pypdf.PdfReader(io.BytesIO(content))
  text = page.extract_text()  # Pure local processing
  ```

- **`python-docx`** - Extracts text from Word documents
  ```python
  import docx
  doc = docx.Document(io.BytesIO(content))
  text = paragraph.text  # Pure local processing
  ```

- **Built-in Python** - For TXT files
  ```python
  text = content.decode('utf-8')  # No external library needed
  ```

### **Phase 4: Backend Text Refinement** 🤖 (GOOGLE GEMINI API)

```python
# File: backend/app/services/draft_refiner.py

class DraftRefiner:
    async def refine_draft(self, text, focus_areas, change_level):
        """Refine text using AI"""
        
        # 1. Import SLM Engine
        from app.services.slm_engine import SLMEngine
        
        engine = SLMEngine()
        
        # 2. Build prompt
        prompt = f"""Refine this draft:
        
        ORIGINAL: {text}
        FOCUS: {focus_areas}
        LEVEL: {change_level}
        
        Return JSON with:
        - refined_text
        - changes list
        - warnings
        """
        
        # 3. Call Gemini API
        result = await engine.generate(prompt)
        
        return result
```

```python
# File: backend/app/services/slm_engine.py

import google.generativeai as genai

class SLMEngine:
    def __init__(self):
        # Configure API with your key
        genai.configure(api_key=settings.gemini_api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    async def generate(self, prompt):
        """Call Google Gemini API"""
        
        # THIS IS THE ACTUAL API CALL TO GOOGLE'S SERVERS
        response = self.model.generate_content(prompt)
        
        # Parse response
        return response.text
```

**API Details:**
- **Service:** Google Gemini API (Cloud-based)
- **Model:** `gemini-1.5-flash`
- **Endpoint:** `generativelanguage.googleapis.com`
- **Authentication:** API Key (from .env: `GEMINI_API_KEY`)
- **Cost:** Free tier available (15 requests/minute)
- **Requires:** Internet connection

### **Phase 5: Response Processing** 📊

```python
# Backend structures the AI response

{
  "success": true,
  "refined_text": "Your improved text...",
  "changes": [
    {
      "type": "clarity",
      "original": "leverages",
      "refined": "uses",
      "reason": "Simpler, clearer word choice"
    }
  ],
  "word_count_original": 250,
  "word_count_refined": 245,
  "warnings": []
}
```

### **Phase 6: Frontend Display** 🎨

```typescript
// Frontend displays results
setRefinedText(data.refined_text)
setChanges(data.changes)
setWordCounts({
  original: data.word_count_original,
  refined: data.word_count_refined
})
```

---

## 📦 **TECHNOLOGY STACK**

### **Frontend:**
- **Framework:** Next.js 16 (React 19)
- **Language:** TypeScript
- **HTTP Client:** Fetch API (built-in)
- **UI:** Framer Motion (animations)

### **Backend:**
- **Framework:** FastAPI (Python)
- **Language:** Python 3.11
- **Web Server:** Uvicorn

### **File Processing (Local):**
```python
# requirements.txt
pypdf          # PDF text extraction
python-docx    # DOCX text extraction
# No external API - pure local processing
```

### **AI Processing (Cloud API):**
```python
# requirements.txt
google-generativeai  # Gemini API client library

# .env
GEMINI_API_KEY=your_key_here  # Required for API access
```

---

## 🌐 **NETWORK FLOW**

```
┌─────────────────┐
│   User Browser  │
│  localhost:3000 │
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│  Backend Server │
│  localhost:8000 │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
LOCAL         INTERNET
    ↓         ↓
┌─────────┐ ┌──────────────────┐
│ pypdf   │ │ Google Gemini    │
│ python- │ │ API              │
│  docx   │ │ (Cloud)          │
└─────────┘ └──────────────────┘
    │              │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │   Response   │
    └──────────────┘
           ↓
    ┌──────────────┐
    │   Frontend   │
    │   Display    │
    └──────────────┘
```

---

## 🔑 **KEY COMPONENTS EXPLAINED**

### 1. **Is pypdf a library or API?**
**Library** - Installed locally, runs on your server
```bash
pip install pypdf
# No API key needed
# No internet required after installation
# Pure Python code
```

### 2. **Is python-docx a library or API?**
**Library** - Installed locally, runs on your server
```bash
pip install python-docx
# No API key needed
# No internet required after installation
# Pure Python code
```

### 3. **Is Google Gemini a library or API?**
**API** (with a Python client library)
```bash
pip install google-generativeai  # This is just the client library

# Requires API key
GEMINI_API_KEY=your_key_here

# Makes HTTP requests to:
# https://generativelanguage.googleapis.com
```

The `google-generativeai` package is a **client library** that wraps the API calls, but the actual AI processing happens on **Google's servers** (not locally).

---

## 💸 **COST BREAKDOWN**

### **Local Processing (Free):**
- PDF extraction: ✅ Free
- DOCX extraction: ✅ Free
- TXT processing: ✅ Free
- Server hosting: Only Docker/compute costs

### **API Processing (Paid/Free Tier):**
- **Google Gemini API:**
  - **Free Tier:** 15 requests/minute, 1500 requests/day
  - **Paid:** After free tier exhausted
  - **Cost:** Variable based on tokens processed
  - **Model:** gemini-1.5-flash is cheaper than gemini-pro

**Example Usage:**
- 1 draft refinement ≈ 1 API call
- Small draft (500 words) ≈ 1000 tokens
- Large draft (2000 words) ≈ 4000 tokens

---

## ⚡ **PERFORMANCE CHARACTERISTICS**

### **File Processing (Local - Fast):**
- Small PDF (10 pages): ~0.5-1 second
- Large PDF (100 pages): ~2-5 seconds
- DOCX: ~0.3-1 second
- TXT: Instant (<0.1 second)

### **AI Processing (API - Variable):**
- Small text (< 500 words): ~1-3 seconds
- Medium text (500-1500 words): ~2-5 seconds
- Large text (1500-5000 words): ~5-10 seconds

**Factors Affecting Speed:**
- Internet connection speed
- API server load (Google)
- Text complexity
- Number of focus areas

---

## 🔒 **SECURITY & PRIVACY**

### **Local Processing:**
- ✅ Files stay on your server
- ✅ No data sent to external services
- ✅ Complete privacy

### **API Processing:**
- ⚠️ Text **IS sent** to Google Gemini API
- ⚠️ Google processes your text on their servers
- ⚠️ Subject to Google's privacy policy
- ⚠️ Not recommended for highly sensitive data

**Privacy Options:**
1. Use for non-sensitive research drafts ✅
2. Don't use for confidential IP/trade secrets ❌
3. Consider self-hosted AI models for sensitive data

---

## 🐛 **WHAT WAS THE BUG?**

### **Problem:**
The backend was returning error responses with invalid enum values:
```python
# Wrong (caused validation error):
CrashLog(failed_stage="processing")  # "processing" not in enum

# Right (fixed):
CrashLog(failed_stage=FailedStage.PROCESSING)  # Valid enum value
```

### **Root Cause:**
The `FailedStage` enum didn't include stages needed by draft-conference routes:
- `TEXT_EXTRACTION`
- `FILE_PROCESSING`
- `REFINEMENT`
- `RECOMMENDATION`
- `PROCESSING`

### **Fix Applied:**
1. ✅ Added missing stages to `FailedStage` enum
2. ✅ Added missing error types to `ErrorType` enum
3. ✅ Updated all CrashLog returns to use proper enums
4. ✅ Added `extract_text()` method to `DocumentProcessor`

---

## ✅ **VERIFICATION**

### **Test Local Processing:**
```python
# Run in backend container:
docker exec -it inventix-backend python3 << EOF
from app.services.document_processor import DocumentProcessor
dp = DocumentProcessor()
print("Has extract_text:", hasattr(dp, 'extract_text'))
# Should print: Has extract_text: True
EOF
```

### **Test API Connection:**
```python
# Run in backend container:
docker exec -it inventix-backend python3 << EOF
from app.services.slm_engine import SLMEngine
engine = SLMEngine()
print("SLM Engine initialized:", engine is not None)
# Should print: SLM Engine initialized: True
EOF
```

---

## 🎯 **SUMMARY**

**Draft Refinement uses:**

1. **📦 Local Libraries (No API):**
   - `pypdf` for PDF extraction
   - `python-docx` for DOCX extraction
   - Python built-ins for TXT
   
2. **☁️ Cloud API:**
   - Google Gemini API for AI text refinement
   - Requires API key and internet
   - Processes text on Google's servers

**Data Flow:**
```
File Upload → Local Extraction → Send Text to Gemini API → Receive Refinement → Display
    ↑                                     ↑
  Libraries                             API
  (pypdf, python-docx)              (Google Gemini)
```

**The fix ensures proper communication between all components!** 🎉
