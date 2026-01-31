# Structured Extraction Schema (Post-Extraction)

This schema is produced by the deterministic extraction stage and feeds the
structuring stage. It is domain-agnostic and supports both patent and
research pipelines.

## JSON Schema (Draft 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://draftpatenai.local/schemas/extraction.json",
  "title": "ExtractionResult",
  "type": "object",
  "required": [
    "document_id",
    "source_type",
    "language",
    "metadata",
    "pages",
    "blocks",
    "tables",
    "figures",
    "references",
    "annotations",
    "provenance_index"
  ],
  "properties": {
    "document_id": { "type": "string" },
    "source_type": { "type": "string", "enum": ["pdf", "text"] },
    "language": { "type": "string", "minLength": 2, "maxLength": 8 },
    "metadata": {
      "type": "object",
      "required": ["title", "authors", "created_at", "checksum"],
      "properties": {
        "title": { "type": "string" },
        "authors": { "type": "array", "items": { "type": "string" } },
        "created_at": { "type": "string", "format": "date-time" },
        "checksum": { "type": "string" },
        "source_filename": { "type": "string" }
      },
      "additionalProperties": false
    },
    "pages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["page_number", "width", "height"],
        "properties": {
          "page_number": { "type": "integer", "minimum": 1 },
          "width": { "type": "number" },
          "height": { "type": "number" },
          "rotation": { "type": "integer" }
        },
        "additionalProperties": false
      }
    },
    "blocks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["block_id", "page_number", "block_type", "text", "bbox"],
        "properties": {
          "block_id": { "type": "string" },
          "page_number": { "type": "integer", "minimum": 1 },
          "block_type": {
            "type": "string",
            "enum": ["title", "heading", "paragraph", "list", "table", "figure", "equation", "footer", "header", "caption"]
          },
          "text": { "type": "string" },
          "bbox": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": { "type": "number" }
          },
          "provenance_id": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "tables": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["table_id", "page_number", "cells", "bbox"],
        "properties": {
          "table_id": { "type": "string" },
          "page_number": { "type": "integer", "minimum": 1 },
          "bbox": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": { "type": "number" }
          },
          "cells": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["row", "col", "text"],
              "properties": {
                "row": { "type": "integer", "minimum": 0 },
                "col": { "type": "integer", "minimum": 0 },
                "text": { "type": "string" },
                "rowspan": { "type": "integer", "minimum": 1 },
                "colspan": { "type": "integer", "minimum": 1 },
                "provenance_id": { "type": "string" }
              },
              "additionalProperties": false
            }
          },
          "caption": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "figures": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["figure_id", "page_number", "bbox"],
        "properties": {
          "figure_id": { "type": "string" },
          "page_number": { "type": "integer", "minimum": 1 },
          "bbox": {
            "type": "array",
            "minItems": 4,
            "maxItems": 4,
            "items": { "type": "number" }
          },
          "caption": { "type": "string" },
          "provenance_id": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "references": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["ref_id", "text", "provenance_id"],
        "properties": {
          "ref_id": { "type": "string" },
          "text": { "type": "string" },
          "doi": { "type": "string" },
          "url": { "type": "string" },
          "provenance_id": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "annotations": {
      "type": "object",
      "required": ["citations", "equations", "claims_markers"],
      "properties": {
        "citations": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["text", "provenance_id"],
            "properties": {
              "text": { "type": "string" },
              "provenance_id": { "type": "string" }
            },
            "additionalProperties": false
          }
        },
        "equations": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["latex", "provenance_id"],
            "properties": {
              "latex": { "type": "string" },
              "provenance_id": { "type": "string" }
            },
            "additionalProperties": false
          }
        },
        "claims_markers": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["text", "provenance_id"],
            "properties": {
              "text": { "type": "string" },
              "provenance_id": { "type": "string" }
            },
            "additionalProperties": false
          }
        }
      },
      "additionalProperties": false
    },
    "provenance_index": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["page_number", "start_offset", "end_offset"],
        "properties": {
          "page_number": { "type": "integer", "minimum": 1 },
          "start_offset": { "type": "integer", "minimum": 0 },
          "end_offset": { "type": "integer", "minimum": 0 },
          "source_text": { "type": "string" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

## Example (Truncated)

```json
{
  "document_id": "doc_9f3b8a6f",
  "source_type": "pdf",
  "language": "en",
  "metadata": {
    "title": "Adaptive Radar Signal Filtering",
    "authors": ["J. Lee", "M. Patel"],
    "created_at": "2026-01-31T14:22:03Z",
    "checksum": "sha256:7b68ef2c...",
    "source_filename": "radar_filtering.pdf"
  },
  "pages": [
    { "page_number": 1, "width": 612, "height": 792, "rotation": 0 }
  ],
  "blocks": [
    {
      "block_id": "b1",
      "page_number": 1,
      "block_type": "title",
      "text": "Adaptive Radar Signal Filtering",
      "bbox": [72, 720, 540, 760],
      "provenance_id": "p1s0e35"
    },
    {
      "block_id": "b2",
      "page_number": 1,
      "block_type": "paragraph",
      "text": "We describe a filter that reduces clutter...",
      "bbox": [72, 620, 540, 700],
      "provenance_id": "p1s36e112"
    }
  ],
  "tables": [
    {
      "table_id": "t1",
      "page_number": 2,
      "bbox": [72, 400, 540, 520],
      "cells": [
        { "row": 0, "col": 0, "text": "SNR (dB)", "provenance_id": "p2s10e18" },
        { "row": 0, "col": 1, "text": "Accuracy", "provenance_id": "p2s19e28" },
        { "row": 1, "col": 0, "text": "10", "provenance_id": "p2s29e31" },
        { "row": 1, "col": 1, "text": "0.91", "provenance_id": "p2s32e36" }
      ],
      "caption": "Table 1. Filtering performance."
    }
  ],
  "figures": [
    {
      "figure_id": "f1",
      "page_number": 3,
      "bbox": [72, 300, 540, 520],
      "caption": "Figure 1. Block diagram of the filter.",
      "provenance_id": "p3s0e40"
    }
  ],
  "references": [
    {
      "ref_id": "r1",
      "text": "Smith A. (2020) Radar Filtering...",
      "doi": "10.1000/xyz123",
      "provenance_id": "p10s15e58"
    }
  ],
  "annotations": {
    "citations": [
      { "text": "[1]", "provenance_id": "p4s220e223" }
    ],
    "equations": [
      { "latex": "y_t = \\alpha x_t + (1-\\alpha) y_{t-1}", "provenance_id": "p5s90e118" }
    ],
    "claims_markers": [
      { "text": "Claim 1.", "provenance_id": "p7s0e7" }
    ]
  },
  "provenance_index": {
    "p1s0e35": { "page_number": 1, "start_offset": 0, "end_offset": 35, "source_text": "Adaptive Radar Signal Filtering" },
    "p1s36e112": { "page_number": 1, "start_offset": 36, "end_offset": 112, "source_text": "We describe a filter that reduces clutter..." }
  }
}
```

