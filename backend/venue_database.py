"""
Venue Knowledge Base for Inventix AI - Phase 7

Static, curated dataset of academic venues for recommendation.
Version-controlled and deterministic.

Venues are categorized by:
- Type: CONFERENCE, JOURNAL, WORKSHOP
- Domains: AI, ML, NLP, CV, MEDICAL, BIOTECH, etc.
- Scope: broad description of what they accept
"""
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass

VENUE_DATABASE_VERSION = "1.0.0"


class VenueType(str, Enum):
    CONFERENCE = "CONFERENCE"
    JOURNAL = "JOURNAL"
    WORKSHOP = "WORKSHOP"


@dataclass
class Venue:
    """Academic venue for publication."""
    name: str
    short_name: str
    venue_type: VenueType
    domains: List[str]
    scope: str
    submission_formats: List[str]
    typical_topics: List[str]
    tier_hint: str  # "flagship", "top", "notable", "emerging" - NOT ranking
    research_focus: bool  # True if primarily research
    patent_relevant: bool  # True if patent-like work is accepted


# ============== Venue Database ==============

VENUES: List[Venue] = [
    # ===== AI/ML Conferences =====
    Venue(
        name="Conference on Neural Information Processing Systems",
        short_name="NeurIPS",
        venue_type=VenueType.CONFERENCE,
        domains=["AI", "ML", "DEEP_LEARNING", "OPTIMIZATION", "THEORY"],
        scope="Machine learning, artificial intelligence, neural networks, optimization, statistics",
        submission_formats=["full_paper", "spotlight", "poster"],
        typical_topics=["deep learning", "reinforcement learning", "optimization", "theory", "applications"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="International Conference on Machine Learning",
        short_name="ICML",
        venue_type=VenueType.CONFERENCE,
        domains=["AI", "ML", "DEEP_LEARNING", "THEORY", "OPTIMIZATION"],
        scope="Machine learning algorithms, theory, and applications",
        submission_formats=["full_paper", "poster"],
        typical_topics=["supervised learning", "unsupervised learning", "deep learning", "optimization"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="International Conference on Learning Representations",
        short_name="ICLR",
        venue_type=VenueType.CONFERENCE,
        domains=["AI", "ML", "DEEP_LEARNING", "REPRESENTATION_LEARNING"],
        scope="Deep learning, representation learning, neural networks",
        submission_formats=["full_paper", "poster"],
        typical_topics=["deep learning", "transformers", "generative models", "self-supervised"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="AAAI Conference on Artificial Intelligence",
        short_name="AAAI",
        venue_type=VenueType.CONFERENCE,
        domains=["AI", "ML", "NLP", "ROBOTICS", "PLANNING"],
        scope="Broad AI including reasoning, planning, NLP, vision, robotics",
        submission_formats=["full_paper", "short_paper"],
        typical_topics=["AI systems", "knowledge representation", "planning", "NLP", "vision"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="International Joint Conference on Artificial Intelligence",
        short_name="IJCAI",
        venue_type=VenueType.CONFERENCE,
        domains=["AI", "ML", "MULTI_AGENT", "PLANNING", "KNOWLEDGE"],
        scope="Broad AI research, multi-agent systems, planning, knowledge representation",
        submission_formats=["full_paper"],
        typical_topics=["multi-agent", "game theory", "planning", "knowledge", "reasoning"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=False
    ),

    # ===== NLP Conferences =====
    Venue(
        name="Annual Meeting of the Association for Computational Linguistics",
        short_name="ACL",
        venue_type=VenueType.CONFERENCE,
        domains=["NLP", "COMPUTATIONAL_LINGUISTICS", "AI"],
        scope="Natural language processing, computational linguistics, language understanding",
        submission_formats=["long_paper", "short_paper"],
        typical_topics=["language models", "parsing", "semantics", "dialogue", "translation"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="Conference on Empirical Methods in Natural Language Processing",
        short_name="EMNLP",
        venue_type=VenueType.CONFERENCE,
        domains=["NLP", "AI", "ML"],
        scope="Empirical methods for NLP, data-driven approaches",
        submission_formats=["long_paper", "short_paper"],
        typical_topics=["language models", "information extraction", "sentiment", "QA"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="North American Chapter of the ACL",
        short_name="NAACL",
        venue_type=VenueType.CONFERENCE,
        domains=["NLP", "AI"],
        scope="NLP research with emphasis on North American community",
        submission_formats=["long_paper", "short_paper"],
        typical_topics=["language models", "NLU", "NLG", "applications"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=False
    ),

    # ===== Computer Vision =====
    Venue(
        name="Conference on Computer Vision and Pattern Recognition",
        short_name="CVPR",
        venue_type=VenueType.CONFERENCE,
        domains=["COMPUTER_VISION", "AI", "ML", "IMAGE_PROCESSING"],
        scope="Computer vision, pattern recognition, image processing",
        submission_formats=["full_paper", "poster"],
        typical_topics=["object detection", "segmentation", "3D vision", "video", "generative"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="International Conference on Computer Vision",
        short_name="ICCV",
        venue_type=VenueType.CONFERENCE,
        domains=["COMPUTER_VISION", "AI", "3D_VISION"],
        scope="Computer vision and related fields",
        submission_formats=["full_paper", "poster"],
        typical_topics=["3D reconstruction", "tracking", "recognition", "scene understanding"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="European Conference on Computer Vision",
        short_name="ECCV",
        venue_type=VenueType.CONFERENCE,
        domains=["COMPUTER_VISION", "AI"],
        scope="Computer vision research",
        submission_formats=["full_paper"],
        typical_topics=["visual recognition", "motion", "3D", "video analysis"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=True
    ),

    # ===== Medical/Health =====
    Venue(
        name="Medical Image Computing and Computer Assisted Intervention",
        short_name="MICCAI",
        venue_type=VenueType.CONFERENCE,
        domains=["MEDICAL", "COMPUTER_VISION", "AI", "HEALTHCARE"],
        scope="Medical image analysis, computer-assisted intervention, healthcare AI",
        submission_formats=["full_paper"],
        typical_topics=["medical imaging", "segmentation", "diagnosis", "surgery planning"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="Journal of the American Medical Informatics Association",
        short_name="JAMIA",
        venue_type=VenueType.JOURNAL,
        domains=["MEDICAL", "HEALTHCARE", "INFORMATICS", "AI"],
        scope="Medical informatics, healthcare IT, clinical decision support",
        submission_formats=["research_article", "case_study", "review"],
        typical_topics=["clinical informatics", "EHR", "decision support", "health AI"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="Nature Medicine",
        short_name="Nat Med",
        venue_type=VenueType.JOURNAL,
        domains=["MEDICAL", "BIOTECH", "HEALTHCARE"],
        scope="High-impact medical research, clinical studies, therapeutics",
        submission_formats=["article", "letter", "review"],
        typical_topics=["clinical research", "therapeutics", "diagnostics", "translational"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),

    # ===== Biotech/Bioinformatics =====
    Venue(
        name="Intelligent Systems for Molecular Biology",
        short_name="ISMB",
        venue_type=VenueType.CONFERENCE,
        domains=["BIOTECH", "BIOINFORMATICS", "AI", "ML"],
        scope="Computational biology, bioinformatics, molecular biology AI",
        submission_formats=["full_paper", "highlight_track"],
        typical_topics=["genomics", "proteomics", "drug discovery", "sequence analysis"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="Bioinformatics (Oxford)",
        short_name="Bioinformatics",
        venue_type=VenueType.JOURNAL,
        domains=["BIOTECH", "BIOINFORMATICS", "COMPUTATIONAL_BIOLOGY"],
        scope="Computational methods for biological data",
        submission_formats=["original_paper", "application_note"],
        typical_topics=["sequence analysis", "structural biology", "systems biology"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=True
    ),

    # ===== Software/Systems =====
    Venue(
        name="ACM SIGSOFT International Symposium on Foundations of Software Engineering",
        short_name="FSE",
        venue_type=VenueType.CONFERENCE,
        domains=["SOFTWARE_ENGINEERING", "AI", "SYSTEMS"],
        scope="Software engineering foundations, tools, and practices",
        submission_formats=["research_paper", "tool_paper"],
        typical_topics=["testing", "verification", "program analysis", "AI for SE"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="International Conference on Software Engineering",
        short_name="ICSE",
        venue_type=VenueType.CONFERENCE,
        domains=["SOFTWARE_ENGINEERING", "SYSTEMS"],
        scope="Software engineering research and practice",
        submission_formats=["technical_paper", "seip_paper"],
        typical_topics=["software development", "testing", "maintenance", "AI4SE"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),

    # ===== Workshops =====
    Venue(
        name="NeurIPS Workshop Track",
        short_name="NeurIPS-WS",
        venue_type=VenueType.WORKSHOP,
        domains=["AI", "ML"],
        scope="Focused workshops on emerging ML topics",
        submission_formats=["extended_abstract", "short_paper"],
        typical_topics=["emerging topics", "focused domains", "new directions"],
        tier_hint="notable",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="ICML Workshop Track",
        short_name="ICML-WS",
        venue_type=VenueType.WORKSHOP,
        domains=["AI", "ML"],
        scope="Focused workshops on specific ML areas",
        submission_formats=["extended_abstract", "short_paper"],
        typical_topics=["specialized topics", "emerging areas"],
        tier_hint="notable",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="ACL Workshop Track",
        short_name="ACL-WS",
        venue_type=VenueType.WORKSHOP,
        domains=["NLP", "AI"],
        scope="Specialized NLP workshops",
        submission_formats=["short_paper", "extended_abstract"],
        typical_topics=["specialized NLP", "low-resource", "applications"],
        tier_hint="notable",
        research_focus=True,
        patent_relevant=False
    ),

    # ===== Journals =====
    Venue(
        name="Journal of Machine Learning Research",
        short_name="JMLR",
        venue_type=VenueType.JOURNAL,
        domains=["ML", "AI", "THEORY"],
        scope="Machine learning algorithms, theory, and applications",
        submission_formats=["research_article"],
        typical_topics=["ML theory", "algorithms", "statistical learning"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="Transactions on Machine Learning Research",
        short_name="TMLR",
        venue_type=VenueType.JOURNAL,
        domains=["ML", "AI", "DEEP_LEARNING"],
        scope="Machine learning research with faster review cycle",
        submission_formats=["research_article"],
        typical_topics=["deep learning", "empirical ML", "applications"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="IEEE Transactions on Pattern Analysis and Machine Intelligence",
        short_name="TPAMI",
        venue_type=VenueType.JOURNAL,
        domains=["COMPUTER_VISION", "ML", "AI"],
        scope="Pattern analysis, machine intelligence, computer vision",
        submission_formats=["research_article", "survey"],
        typical_topics=["vision", "pattern recognition", "ML algorithms"],
        tier_hint="flagship",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="Nature Communications",
        short_name="Nat Commun",
        venue_type=VenueType.JOURNAL,
        domains=["GENERAL", "BIOTECH", "AI", "MEDICAL"],
        scope="Broad scientific research with high impact",
        submission_formats=["article"],
        typical_topics=["interdisciplinary", "significant findings", "broad interest"],
        tier_hint="top",
        research_focus=True,
        patent_relevant=True
    ),
    Venue(
        name="Scientific Reports",
        short_name="Sci Rep",
        venue_type=VenueType.JOURNAL,
        domains=["GENERAL", "AI", "MEDICAL", "BIOTECH"],
        scope="Primary research across natural sciences",
        submission_formats=["article"],
        typical_topics=["original research", "replication studies", "negative results"],
        tier_hint="notable",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="PLOS ONE",
        short_name="PLOS ONE",
        venue_type=VenueType.JOURNAL,
        domains=["GENERAL", "MEDICAL", "BIOTECH", "AI"],
        scope="Primary research with sound methodology",
        submission_formats=["research_article"],
        typical_topics=["primary research", "methodologically sound"],
        tier_hint="notable",
        research_focus=True,
        patent_relevant=False
    ),

    # ===== Preprint Servers (for refinement recommendations) =====
    Venue(
        name="arXiv",
        short_name="arXiv",
        venue_type=VenueType.WORKSHOP,  # Treated as workshop-level for recommendations
        domains=["AI", "ML", "NLP", "COMPUTER_VISION", "GENERAL"],
        scope="Preprint server for early dissemination",
        submission_formats=["preprint"],
        typical_topics=["any research topic", "early results", "work in progress"],
        tier_hint="emerging",
        research_focus=True,
        patent_relevant=False
    ),
    Venue(
        name="bioRxiv",
        short_name="bioRxiv",
        venue_type=VenueType.WORKSHOP,
        domains=["BIOTECH", "MEDICAL", "BIOINFORMATICS"],
        scope="Preprint server for life sciences",
        submission_formats=["preprint"],
        typical_topics=["biology", "medicine", "bioinformatics"],
        tier_hint="emerging",
        research_focus=True,
        patent_relevant=False
    ),
]


def get_all_venues() -> List[Venue]:
    """Get all venues in the database."""
    return VENUES


def get_venues_by_domain(domain: str) -> List[Venue]:
    """Get venues that match a specific domain."""
    domain_upper = domain.upper()
    return [v for v in VENUES if domain_upper in v.domains]


def get_venues_by_type(venue_type: VenueType) -> List[Venue]:
    """Get venues of a specific type."""
    return [v for v in VENUES if v.venue_type == venue_type]


def get_venue_domains() -> List[str]:
    """Get all unique domains across venues."""
    domains = set()
    for venue in VENUES:
        domains.update(venue.domains)
    return sorted(list(domains))


def search_venues(keywords: List[str]) -> List[Venue]:
    """
    Search venues by keywords.
    
    Matches against: name, short_name, scope, typical_topics, domains.
    """
    keywords_lower = [k.lower() for k in keywords]
    matches = []
    
    for venue in VENUES:
        score = 0
        searchable = (
            venue.name.lower() + " " +
            venue.short_name.lower() + " " +
            venue.scope.lower() + " " +
            " ".join(venue.typical_topics) + " " +
            " ".join(venue.domains).lower()
        )
        
        for kw in keywords_lower:
            if kw in searchable:
                score += 1
        
        if score > 0:
            matches.append((venue, score))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches]
