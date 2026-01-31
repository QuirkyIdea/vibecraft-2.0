# DraftPatenAI Architecture

## Goals
- Convert uploaded PDFs or pasted text into publication-ready drafts for:
  - Patent filing
  - Academic research paper publication
- Use deterministic extraction and structuring.
- Use LLM APIs only for controlled, section-wise drafting.
- Prevent hallucinations by grounding generation in extracted facts.

## High-Level System Design

### Core Services
- API Service (FastAPI): orchestrates uploads, pipeline runs, and draft retrieval.
- Extraction Service: deterministic extraction from PDF/text with explicit provenance.
- Structuring Service: rule-based segmentation into domain-specific sections.
- Drafting Service: section-wise LLM calls with strict prompts and schemas.
- Post-Processing Service: format normalization, citations, consistency checks.
- Storage Service: document store and artifacts (raw, structured, generated).

### Data Flow (Pipeline)
1. **Ingest**
   - Accept PDF upload or pasted text.
   - Persist raw input and metadata.
2. **Extract**
   - Deterministic parsing:
     - PDF text extraction + layout blocks.
     - Section candidates, tables, references.
   - Generate provenance map (source offsets and page references).
3. **Structure**
   - Rule-based segmentation into canonical sections.
   - Output: structured JSON with required fields for each section.
4. **Draft (LLM)**
   - Generate each section independently.
   - LLM prompts receive only:
     - Structured section inputs.
     - Constraints: no fabrication, cite provenance.
   - Validate output against schemas.
5. **Post-Process**
   - Consistency checks across sections.
   - Formatting to target templates.
   - Flag missing evidence and uncertainty.
6. **Deliver**
   - Produce downloadable draft document and JSON artifacts.

## Section-Wise Generation Strategy
- **Patent Draft**
  - Title, Abstract, Background, Summary, Brief Description of Drawings,
    Detailed Description, Claims.
- **Academic Draft**
  - Title, Abstract, Introduction, Related Work, Methods, Results,
    Discussion, Conclusion, References.
- Each section has:
  - Schema definition.
  - Deterministic constraints.
  - LLM prompt template.
  - Validation and post-processing rules.

## Reliability and Safety Controls
- LLM usage is scoped to rewriting and organizing extracted facts.
- All outputs must reference extracted facts via provenance IDs.
- Missing facts:
  - Output placeholders and warnings instead of fabrication.
- Deterministic constraints enforced with:
  - JSON schema validation.
  - Rule-based completeness checks.
  - Mandatory citations to source spans.

## Storage Model
- **Raw Inputs**: original PDF or text.
- **Extracted**: parsed blocks, tables, references.
- **Structured**: canonical section JSON.
- **Drafted**: section outputs + LLM metadata.
- **Post-Processed**: final assembled draft.

## Scalability Considerations
- Stateless API nodes.
- Background worker for pipeline execution.
- Object storage for large artifacts.
- Database for metadata and state.

## Key Interfaces
- REST API:
  - `POST /v1/ingest`
  - `POST /v1/pipelines/{type}/run`
  - `GET /v1/drafts/{id}`
  - `GET /v1/artifacts/{id}`
- Internal events:
  - `extract.complete`, `structure.complete`, `draft.complete`.

