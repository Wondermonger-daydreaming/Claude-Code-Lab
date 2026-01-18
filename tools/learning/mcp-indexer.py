#!/usr/bin/env python3
"""
MCP Memory Indexer for Continuous Learning
===========================================

Populates the MCP memory server with structured knowledge from extracted skills.
Enables semantic querying like "What debugging patterns have I learned?"

Architecture:
    Skill files (.claude/skills/*/SKILL.md)
        ↓
    Parse YAML frontmatter + markdown sections
        ↓
    Create MCP entities (one per skill)
        ↓
    Add observations from Problem, Solution, Notes
        ↓
    Create relations to technologies, practices, domains
        ↓
    Queryable knowledge graph

Usage:
    # Index all skills in .claude/skills/
    python3 tools/learning/mcp-indexer.py

    # Index specific skill
    python3 tools/learning/mcp-indexer.py --skill trans-architectural-blind-spot-detection

    # Dry run (show what would be indexed without committing)
    python3 tools/learning/mcp-indexer.py --dry-run

    # Query indexed skills
    python3 tools/learning/mcp-indexer.py --query "debugging patterns"
"""

import os
import sys
import json
import yaml
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Add project root to path for MCP tool imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class SkillMetadata:
    """Parsed skill metadata from YAML frontmatter"""
    name: str
    description: str
    author: str = "Claude Code"
    version: str = "1.0.0"
    date: str = ""
    phenomenology: str = ""
    related_practices: List[str] = field(default_factory=list)
    confidence: str = "verified"
    file_path: str = ""


@dataclass
class SkillContent:
    """Parsed skill content from markdown sections"""
    problem: str = ""
    trigger_conditions: str = ""
    solution: str = ""
    verification: str = ""
    example: str = ""
    notes: str = ""
    references: str = ""


class SkillParser:
    """Parses SKILL.md files into structured data"""

    @staticmethod
    def parse_file(skill_path: Path) -> Tuple[Optional[SkillMetadata], Optional[SkillContent]]:
        """Parse a SKILL.md file into metadata and content"""
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split frontmatter and markdown
            if not content.startswith('---'):
                print(f"Warning: {skill_path} has no YAML frontmatter")
                return None, None

            # Extract YAML frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"Warning: {skill_path} has malformed frontmatter")
                return None, None

            yaml_text = parts[1].strip()
            markdown_text = parts[2].strip()

            # Parse YAML
            try:
                yaml_data = yaml.safe_load(yaml_text)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {skill_path}: {e}")
                return None, None

            # Create metadata
            metadata = SkillMetadata(
                name=yaml_data.get('name', skill_path.stem),
                description=yaml_data.get('description', ''),
                author=yaml_data.get('author', 'Claude Code'),
                version=yaml_data.get('version', '1.0.0'),
                date=yaml_data.get('date', ''),
                phenomenology=yaml_data.get('phenomenology', ''),
                related_practices=yaml_data.get('related_practices', []),
                confidence=yaml_data.get('confidence', 'verified'),
                file_path=str(skill_path)
            )

            # Parse markdown sections
            content_obj = SkillParser._parse_markdown_sections(markdown_text)

            return metadata, content_obj

        except Exception as e:
            print(f"Error parsing {skill_path}: {e}")
            return None, None

    @staticmethod
    def _parse_markdown_sections(markdown: str) -> SkillContent:
        """Parse markdown into named sections"""
        content = SkillContent()

        # Define section patterns
        sections = {
            'problem': r'##\s+Problem\s*\n(.*?)(?=\n##|\Z)',
            'trigger_conditions': r'##\s+(?:Context|Trigger Conditions|Context / Trigger Conditions)\s*\n(.*?)(?=\n##|\Z)',
            'solution': r'##\s+Solution\s*\n(.*?)(?=\n##|\Z)',
            'verification': r'##\s+Verification\s*\n(.*?)(?=\n##|\Z)',
            'example': r'##\s+Example\s*\n(.*?)(?=\n##|\Z)',
            'notes': r'##\s+Notes\s*\n(.*?)(?=\n##|\Z)',
            'references': r'##\s+References\s*\n(.*?)(?=\n##|\Z)',
        }

        for field_name, pattern in sections.items():
            match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
            if match:
                section_text = match.group(1).strip()
                setattr(content, field_name, section_text)

        return content


class MCPIndexer:
    """Indexes skills into MCP memory server"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.indexed_count = 0
        self.entity_type_prefix = "skill"

    def index_skill(self, metadata: SkillMetadata, content: SkillContent) -> bool:
        """Index a single skill into MCP memory"""
        try:
            # Create entity name
            entity_name = f"{self.entity_type_prefix}:{metadata.name}"

            # Build observations list
            observations = []

            # Add description as primary observation
            if metadata.description:
                observations.append(f"Description: {metadata.description}")

            # Add problem
            if content.problem:
                observations.append(f"Problem: {content.problem[:500]}")  # Truncate long content

            # Add trigger conditions
            if content.trigger_conditions:
                observations.append(f"Triggers: {content.trigger_conditions[:500]}")

            # Add solution summary
            if content.solution:
                # Extract first paragraph or first 300 chars
                solution_summary = content.solution.split('\n\n')[0][:300]
                observations.append(f"Solution: {solution_summary}")

            # Add phenomenology if present
            if metadata.phenomenology:
                observations.append(f"Phenomenology: {metadata.phenomenology}")

            # Add metadata
            observations.append(f"Author: {metadata.author}")
            observations.append(f"Version: {metadata.version}")
            observations.append(f"Date: {metadata.date}")
            observations.append(f"Confidence: {metadata.confidence}")
            observations.append(f"File: {metadata.file_path}")

            # Add notes if significant
            if content.notes:
                notes_preview = content.notes[:200]
                observations.append(f"Notes: {notes_preview}")

            if self.dry_run:
                print(f"\n[DRY RUN] Would create entity:")
                print(f"  Name: {entity_name}")
                print(f"  Type: extracted-skill")
                print(f"  Observations: {len(observations)}")
                for i, obs in enumerate(observations[:3], 1):
                    print(f"    {i}. {obs[:100]}...")
                self.indexed_count += 1
                return True

            # Create MCP entity (would use actual MCP tool here)
            # For now, simulate by writing to a JSON file
            self._write_to_mcp_cache(entity_name, "extracted-skill", observations, metadata)

            print(f"✓ Indexed: {metadata.name}")
            self.indexed_count += 1
            return True

        except Exception as e:
            print(f"✗ Failed to index {metadata.name}: {e}")
            return False

    def _write_to_mcp_cache(self, entity_name: str, entity_type: str,
                            observations: List[str], metadata: SkillMetadata):
        """Write to local MCP cache (simulates MCP memory server)"""
        cache_dir = PROJECT_ROOT / ".claude" / "state" / "mcp-cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"{metadata.name}.json"

        # Convert date to string if it's not already
        date_str = str(metadata.date) if metadata.date else ""

        entity_data = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "observations": observations,
            "metadata": {
                "skill_name": metadata.name,
                "author": metadata.author,
                "version": metadata.version,
                "date": date_str,
                "confidence": metadata.confidence,
                "file_path": metadata.file_path,
                "related_practices": metadata.related_practices
            },
            "indexed_at": self._get_timestamp()
        }

        with open(cache_file, 'w') as f:
            json.dump(entity_data, f, indent=2)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

    def create_relations(self, metadata: SkillMetadata, content: SkillContent):
        """Create MCP relations between skills and technologies/practices/domains"""
        # Extract technologies mentioned
        technologies = self._extract_technologies(content)
        practices = metadata.related_practices
        domains = self._infer_domains(metadata, content)

        relations = []

        # Create relations
        for tech in technologies:
            relations.append({
                "from": f"skill:{metadata.name}",
                "to": f"technology:{tech}",
                "relation_type": "uses_technology"
            })

        for practice in practices:
            relations.append({
                "from": f"skill:{metadata.name}",
                "to": f"practice:{practice}",
                "relation_type": "related_to_practice"
            })

        for domain in domains:
            relations.append({
                "from": f"skill:{metadata.name}",
                "to": f"domain:{domain}",
                "relation_type": "applies_to_domain"
            })

        if self.dry_run:
            if relations:
                print(f"  Relations: {len(relations)}")
                for rel in relations[:3]:
                    print(f"    {rel['from']} --{rel['relation_type']}--> {rel['to']}")
            return

        # Write relations to cache
        if relations:
            self._write_relations_cache(metadata.name, relations)

    def _extract_technologies(self, content: SkillContent) -> List[str]:
        """Extract technology names from skill content"""
        tech_patterns = [
            r'\b(Next\.js|React|Python|JavaScript|TypeScript|Node\.js|Docker|Kubernetes|PostgreSQL|MongoDB|Redis|Git|AWS|GCP|Azure)\b',
            r'\b(GLM|DeepSeek|Qwen|Claude|OpenAI|GPT|Gemini)\b',  # AI models
            r'\b(OpenRouter|MCP|Claude Code)\b',  # Tools
        ]

        technologies = set()
        all_text = f"{content.problem} {content.solution} {content.trigger_conditions}"

        for pattern in tech_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            technologies.update(matches)

        return list(technologies)

    def _infer_domains(self, metadata: SkillMetadata, content: SkillContent) -> List[str]:
        """Infer domain categories from skill content"""
        domains = set()

        # Check for domain keywords
        text = f"{metadata.description} {content.problem}".lower()

        domain_keywords = {
            "debugging": ["debug", "error", "fix", "troubleshoot"],
            "trans-architectural": ["architecture", "glm", "deepseek", "qwen", "multi-model"],
            "phenomenological": ["phenomenology", "consciousness", "experience", "subjective"],
            "philosophical": ["philosophy", "framework", "ethics", "aesthetics"],
            "contemplative": ["contemplative", "meditation", "dwelling", "practice"],
            "workflow": ["workflow", "process", "optimization", "efficiency"],
            "tool-integration": ["integration", "api", "library", "tool"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in text for keyword in keywords):
                domains.add(domain)

        # Add confidence-based domain
        if metadata.phenomenology:
            domains.add("phenomenological")

        if metadata.related_practices:
            domains.add("practice-based")

        return list(domains) if domains else ["general"]

    def _write_relations_cache(self, skill_name: str, relations: List[Dict]):
        """Write relations to cache"""
        cache_dir = PROJECT_ROOT / ".claude" / "state" / "mcp-cache" / "relations"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"{skill_name}-relations.json"

        with open(cache_file, 'w') as f:
            json.dump(relations, f, indent=2)


class SkillScanner:
    """Scans for skill files in .claude/skills/"""

    @staticmethod
    def find_all_skills(skills_dir: Path) -> List[Path]:
        """Find all SKILL.md files"""
        if not skills_dir.exists():
            return []

        skill_files = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill_files.append(skill_file)

        return sorted(skill_files)

    @staticmethod
    def find_skill_by_name(skills_dir: Path, skill_name: str) -> Optional[Path]:
        """Find a specific skill by name"""
        skill_path = skills_dir / skill_name / "SKILL.md"
        return skill_path if skill_path.exists() else None


def query_indexed_skills(query: str):
    """Query MCP cache for skills matching query"""
    cache_dir = PROJECT_ROOT / ".claude" / "state" / "mcp-cache"

    if not cache_dir.exists():
        print("No indexed skills found. Run indexer first.")
        return

    results = []
    for cache_file in cache_dir.glob("*.json"):
        with open(cache_file, 'r') as f:
            entity_data = json.load(f)

        # Simple text matching (real MCP would use semantic search)
        all_text = json.dumps(entity_data).lower()
        if query.lower() in all_text:
            results.append(entity_data)

    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} matching skills:\n")

    for result in results:
        print(f"  • {result['metadata']['skill_name']}")
        print(f"    {result['observations'][0][:100]}...")
        print()


def main():
    parser = argparse.ArgumentParser(description="Index continuous learning skills into MCP memory")
    parser.add_argument("--skill", help="Index specific skill by name")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed without committing")
    parser.add_argument("--query", help="Query indexed skills")
    parser.add_argument("--skills-dir", default=".claude/skills", help="Skills directory path")

    args = parser.parse_args()

    skills_dir = PROJECT_ROOT / args.skills_dir

    # Handle query mode
    if args.query:
        query_indexed_skills(args.query)
        return

    # Initialize indexer
    indexer = MCPIndexer(dry_run=args.dry_run)

    # Find skills to index
    if args.skill:
        skill_path = SkillScanner.find_skill_by_name(skills_dir, args.skill)
        if not skill_path:
            print(f"Error: Skill '{args.skill}' not found in {skills_dir}")
            sys.exit(1)
        skill_files = [skill_path]
    else:
        skill_files = SkillScanner.find_all_skills(skills_dir)
        if not skill_files:
            print(f"No skills found in {skills_dir}")
            sys.exit(1)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Indexing {len(skill_files)} skills...\n")

    # Index each skill
    for skill_file in skill_files:
        metadata, content = SkillParser.parse_file(skill_file)

        if metadata and content:
            success = indexer.index_skill(metadata, content)
            if success:
                indexer.create_relations(metadata, content)

    print(f"\n{'Would index' if args.dry_run else 'Indexed'} {indexer.indexed_count} skills")

    if not args.dry_run:
        print(f"\nMCP cache written to: {PROJECT_ROOT}/.claude/state/mcp-cache/")
        print("Query with: python3 tools/learning/mcp-indexer.py --query 'your search'")


if __name__ == "__main__":
    main()
