# 🧪 Draft Refinement Testing - Sample Inputs

## 📋 Test 1: Basic Text Refinement

### Input:
Open http://localhost:3000 → Navigate to Draft Refinement panel

**Paste this text:**
```
This paper presents a novel approach to machine learning for data processing. We use innovative techniques that are very good and effective. The results shows that our method is better than existing approaches. We achieved significant improvements in performance metrics.
```

**Settings:**
- Focus Areas: ✓ Clarity, ✓ Grammar, ✓ Precision
- Change Level: Moderate

**Click:** "Refine Draft"

### Expected Result:
- Should fix "shows" → "show"
- Should improve vague phrases like "very good" → more specific
- Should enhance "innovative techniques" with precision
- Should see changes listed with reasons

---

## 📋 Test 2: Section-Specific Refinement

### Using API (PowerShell):
```powershell
$body = @{
    section_text = "This study investigates machine learning algorithms. We analyzed various datasets and found interesting patterns. The results are promising."
    section_type = "abstract"
    target_improvements = @("clarity", "structure")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/draft-conference/refine-section" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Using cURL (CMD):
```bash
curl -X POST http://localhost:8000/api/draft-conference/refine-section ^
  -H "Content-Type: application/json" ^
  -d "{\"section_text\": \"This study investigates machine learning algorithms. We analyzed various datasets and found interesting patterns. The results are promising.\", \"section_type\": \"abstract\", \"target_improvements\": [\"clarity\", \"structure\"]}"
```

### Expected Result:
```json
{
  "success": true,
  "refined": "This study investigates machine learning algorithms for...",
  "improvements_made": ["Enhanced clarity", "Improved structure"],
  "preserved_elements": ["Core claims", "Methodology"],
  "suggestions": ["Consider adding specific metrics"]
}
```

---

## 📋 Test 3: File Upload & Refinement

### Step 1: Create Test File
Create `test_draft.txt` with this content:
```
INTRODUCTION

Machine learning has revolutionized data science. This paper explores new techniques for improving model accuracy. We developed a method that combines multiple algorithms to achieve better results.

Our approach uses deep learning and traditional statistical methods together. The experiments showed that our method outperforms existing solutions. We tested on several datasets and got good results.

METHODOLOGY

We collected data from various sources. The preprocessing steps included cleaning and normalization. Feature extraction was performed using standard techniques.

Model training involved hyperparameter tuning. We used cross-validation to ensure robustness. The evaluation metrics included accuracy, precision, and recall.
```

### Step 2: Test in Frontend
1. Go to http://localhost:3000
2. Navigate to Draft Refinement
3. Click "Upload PDF, DOCX, or TXT"
4. Select `test_draft.txt`
5. Choose focus areas: Clarity, Flow, Precision
6. Click "Refine Draft"

### Expected Result:
- Text extracted successfully
- Refinement suggestions appear
- Can see changes in detail
- Word count shows original vs refined

---

## 📋 Test 4: Split View Comparison

### After Test 3:
1. Scroll to results section
2. Click **"Compare"** button (next to "Refined")
3. Should see side-by-side view:
   - Left: Original text
   - Right: Refined text

### Visual Check:
- Both columns should be equal width
- Text should be scrollable
- Easy to spot differences

---

## 📋 Test 5: Export in Different Formats

### After any successful refinement:

#### Test TXT Export:
1. Click "Export" dropdown
2. Select "Text (.txt)"
3. File downloads as `refined_draft.txt`
4. Open file - should contain both original and refined text

#### Test DOCX Export:
1. Click "Export" dropdown
2. Select "Word (.docx)"
3. File downloads as `refined_draft.docx`
4. Open in Word - should be properly formatted with headings

#### Test PDF Export (requires reportlab):
1. First ensure reportlab is installed:
   ```powershell
   cd backend
   pip install reportlab
   ```
2. Click "Export" dropdown
3. Select "PDF (.pdf)"
4. File downloads as `refined_draft.pdf`
5. Open in PDF reader - should have professional formatting

---

## 📋 Test 6: Accept/Reject Individual Changes

### Steps:
1. Refine any text (use Test 1 input)
2. Scroll to "View Detailed Changes"
3. Click to expand changes list
4. For each change, click the ✓ or ✗ button:
   - ✓ = Green = Accepted
   - ✗ = Red = Rejected

### Visual Check:
- Accepted changes: Green background, checkmark icon
- Rejected changes: Red background, X icon
- Can toggle back and forth by clicking again

---

## 📋 Test 7: Batch File Processing (API)

### Step 1: Create Multiple Test Files

**file1.txt:**
```
This is a draft about artificial intelligence. AI is very important in modern technology.
```

**file2.txt:**
```
Machine learning algorithms are widely used. They help solve complex problems effectively.
```

**file3.txt:**
```
Data science combines statistics and programming. It enables data-driven decision making.
```

### Step 2: Test with PowerShell
```powershell
$files = @{
    'files' = Get-Item 'file1.txt', 'file2.txt', 'file3.txt'
    'focus_areas' = 'clarity,precision'
    'change_level' = 'moderate'
}

Invoke-WebRequest -Uri "http://localhost:8000/api/draft-conference/refine-batch" `
    -Method Post `
    -Form $files
```

### Expected Result:
```json
[
  {
    "filename": "file1.txt",
    "success": true,
    "original_text": "This is a draft about...",
    "refined_text": "This document examines...",
    "changes_count": 3,
    "word_count_original": 12,
    "word_count_refined": 14
  },
  {
    "filename": "file2.txt",
    "success": true,
    ...
  },
  {
    "filename": "file3.txt",
    "success": true,
    ...
  }
]
```

---

## 📋 Test 8: Check Service Status

### PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/draft-conference/status"
```

### CMD:
```bash
curl http://localhost:8000/api/draft-conference/status
```

### Expected Output:
```json
{
  "service": "draft-conference",
  "status": "operational",
  "engine": "ANTIGRAVITY",
  "capabilities": [
    "draft_refinement",
    "file_upload_refinement",
    "conference_recommendation",
    "section_refinement",
    "batch_processing",
    "export_formats"
  ],
  "supported_formats": [".pdf", ".docx", ".txt"],
  "export_formats": ["txt", "docx", "pdf"]
}
```

---

## 📋 Test 9: Different Change Levels

### Light Changes:
```
This paper presents our research findings. We conducted experiments and analyzed the results. The data supports our hypothesis.
```
- Set Change Level: **Light**
- Expected: Minimal changes, only obvious errors

### Moderate Changes:
Same text, set Change Level: **Moderate**
- Expected: Balanced improvements, better flow

### Thorough Changes:
Same text, set Change Level: **Thorough**
- Expected: Comprehensive refinement, restructuring

---

## 📋 Test 10: Error Handling

### Test Invalid File Type:
1. Try to upload `.jpg` or `.png` file
2. Expected: Error message about unsupported format

### Test Empty Text:
1. Leave text area empty
2. Click "Refine Draft"
3. Expected: "Please enter draft text or upload a file"

### Test Very Short Text:
```
Hello world.
```
- Expected: May fail validation (min 20 chars required)

---

## ✅ Quick Verification Checklist

After running all tests, verify:

- [ ] Basic text refinement works
- [ ] File upload (TXT, DOCX, PDF) works
- [ ] Section refinement endpoint responds
- [ ] Split view displays correctly
- [ ] Export TXT works
- [ ] Export DOCX works
- [ ] Export PDF works (if reportlab installed)
- [ ] Accept/reject changes works
- [ ] Batch processing handles multiple files
- [ ] Error messages are clear
- [ ] Mobile responsive (resize browser)
- [ ] Backend auto-reloads on changes
- [ ] No console errors in browser

---

## 🐛 Troubleshooting

### Backend not responding?
```powershell
# Check if running
curl http://localhost:8000/health

# Restart backend
cd d:\vibecraft-2.01\vibecraft-2.0\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend not showing changes?
```powershell
# Check browser console (F12)
# Restart frontend
cd d:\vibecraft-2.01\vibecraft-2.0\frontend
npm run dev
```

### PDF export fails?
```powershell
# Install reportlab
cd d:\vibecraft-2.01\vibecraft-2.0\backend
pip install reportlab
```

---

## 🎯 Success Criteria

All features working correctly if:
1. ✅ Can refine text and see improvements
2. ✅ Can upload files and extract text
3. ✅ Can switch between refined/compare views
4. ✅ Can export in all 3 formats
5. ✅ Can accept/reject individual changes
6. ✅ API endpoints respond correctly
7. ✅ No breaking of existing functionality

---

**Happy Testing! 🚀**
