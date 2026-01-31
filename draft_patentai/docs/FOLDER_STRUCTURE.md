# Backend Folder Structure

```
docs/
  ARCHITECTURE.md
  FOLDER_STRUCTURE.md
scripts/
  dev/                 # Local run helpers
  migration/           # Data migrations
src/
  api/
    v1/                # Versioned API routes
    dependencies.py    # Auth, rate limits, request context
    schemas.py         # API request/response models
  config/
    settings.py        # Environment config
    logging.py         # Logging configuration
  core/
    pipeline.py        # Orchestration primitives
    errors.py          # Domain exceptions
    schemas.py         # Shared dataclasses/schemas
  models/
    patent/            # Patent-specific domain models
    academic/          # Academic-specific domain models
  pipelines/
    patent.py          # Patent pipeline definition
    academic.py        # Academic pipeline definition
  prompts/
    patent/            # Section prompt templates
    academic/
  services/
    extraction.py      # Deterministic extraction
    structuring.py     # Rule-based structuring
    drafting.py        # LLM interface + section drivers
    postprocess.py     # Formatting and QA checks
  storage/
    repository.py      # Persistence interface
    file_store.py      # Filesystem/S3 storage
  utils/
    pdf.py             # PDF parsing helpers
    text.py            # Text normalization
    provenance.py      # Source span mapping
tests/
  unit/
  integration/
```

## Notes
- `src/core` is framework-agnostic logic shared across pipelines.
- `src/services` implement deterministic stages plus LLM wrapper.
- `src/pipelines` wires domain-specific flows.
- `src/models` define section schemas for validation.

