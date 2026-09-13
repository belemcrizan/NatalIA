"""Versioned source registry. Offline metadata only; no live retrieval at render time.

A successful HTTP check of a URL is not evidence that the page supports a NatalIA claim.
"""

from __future__ import annotations

SCHEMA = "natalia-sources-1.0"

SOURCES = [
    {
        "id": "src-bipm-si-brochure",
        "author": "Bureau International des Poids et Mesures",
        "title": "The International System of Units (SI Brochure)",
        "canonical_url": "https://www.bipm.org/en/publications/si-brochure",
        "edition": "9th edition, current HTML publication",
        "locator": "SI base quantities and coherent derived units",
        "accessed": "2026-09-13",
        "supports": "Dimensional conventions and SI unit names used in educational models",
        "reuse": "Link and independently written explanation. Brochure text is not copied.",
        "derivation": "adapted",
    },
    {
        "id": "src-nist-constants",
        "author": "National Institute of Standards and Technology",
        "title": "Fundamental Physical Constants",
        "canonical_url": "https://physics.nist.gov/cuu/Constants/",
        "edition": "CODATA values as published on the NIST constants site",
        "locator": "Landing page for CODATA recommended values",
        "accessed": "2026-09-13",
        "supports": "That physical constants have reported values and uncertainties; NatalIA does not ingest the dataset",
        "reuse": "Link only. No constant table is bundled.",
        "derivation": "independent",
    },
    {
        "id": "src-mit-ocw-801sc",
        "author": "Massachusetts Institute of Technology OpenCourseWare",
        "title": "8.01SC Classical Mechanics",
        "canonical_url": "https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/",
        "edition": "Fall 2016",
        "locator": "Course home: Newtonian mechanics exposition",
        "accessed": "2026-09-13",
        "supports": "Background for idealized point-mass and oscillator teaching models",
        "reuse": "OCW terms require attribution. Course notes are not copied; explanations are original.",
        "derivation": "independent",
    },
    {
        "id": "src-openstax-up1-7-2",
        "author": "OpenStax",
        "title": "University Physics Volume 1, Section 7.2 Kinetic Energy",
        "canonical_url": "https://openstax.org/books/university-physics-volume-1/pages/7-2-kinetic-energy",
        "edition": "University Physics Volume 1",
        "locator": "Section 7.2",
        "accessed": "2026-09-13",
        "supports": "Classical kinetic-energy definition K = (1/2) m v^2 as teaching background",
        "reuse": "OpenStax CC BY 4.0. NatalIA text is independently written; quote none of the chapter.",
        "derivation": "independent",
    },
    {
        "id": "src-lean-tpil4-axioms",
        "author": "Lean theorem proving community (Theorem Proving in Lean 4)",
        "title": "Axioms and Computation",
        "canonical_url": "https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/",
        "edition": "Theorem Proving in Lean 4",
        "locator": "Chapter on axioms and computation",
        "accessed": "2026-09-13",
        "supports": "Why axiom/sorry audit is required before calling a Lean check a certificate",
        "reuse": "Link to official book. No book text is copied.",
        "derivation": "independent",
    },
    {
        "id": "src-gcp-cloud-run-contract",
        "author": "Google Cloud",
        "title": "Cloud Run container runtime contract",
        "canonical_url": "https://docs.cloud.google.com/run/docs/container-contract",
        "edition": "Cloud Run documentation",
        "locator": "Container runtime contract",
        "accessed": "2026-09-13",
        "supports": "Later deployment design only. Not used as scientific evidence.",
        "reuse": "Link. No live GCP dependency in the local product.",
        "derivation": "independent",
    },
    {
        "id": "src-natalia-maintainers",
        "author": "NatalIA maintainers",
        "title": "Original educational formalizations in this repository",
        "canonical_url": None,
        "edition": "content_version of natalia.investigations",
        "locator": "natalia/investigations.py",
        "accessed": "2026-09-13",
        "supports": "Didactic DSL payloads that are not copied from copyrighted problem sets",
        "reuse": "Same license as this repository",
        "derivation": "independent",
    },
]


def list_sources():
    return {"schema": SCHEMA, "count": len(SOURCES), "items": SOURCES}


def get_source(ident: str):
    for item in SOURCES:
        if item["id"] == ident:
            return item
    return None
