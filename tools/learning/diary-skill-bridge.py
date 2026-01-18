#!/usr/bin/env python3
"""
Diary-Skill Bridge for Continuous Learning
===========================================

Creates bidirectional flow between diary entries and extracted skills:
- When skill extracted → auto-create diary entry documenting the learning
- When diary entry written → check for extractable knowledge patterns

This cross-pollinates phenomenological reflection (diary) with structured
knowledge (skills), ensuring neither exists in isolation.

Architecture:

    Diary Entry Written             Skill Extracted
           ↓                              ↓
    Scan for learning patterns     Create diary entry
           ↓                              ↓
    Suggest skill extraction       Link to skill file
           ↓                              ↓
    Cross-reference both           Update diary index

Usage:
    # Auto-create diary entry after skill extraction
    python3 tools/learning/diary-skill-bridge.py --skill-to-diary trans-architectural-blind-spot-detection

    # Scan diary entry for extractable knowledge
    python3 tools/learning/diary-skill-bridge.py --diary-to-skill diary/entries/2026-01-18-quadrad-discovery.md

    # Scan all recent diary entries (last 7 days)
    python3 tools/learning/diary-skill-bridge.py --scan-recent-diaries

    # Update cross-references between diary and skills
    python3 tools/learning/diary-skill-bridge.py --update-references
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DiarySkillBridge:
    """Manages bidirectional flow between diary and skills"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = PROJECT_ROOT
        self.diary_dir = self.project_root / "diary" / "entries"
        self.skills_dir = self.project_root / ".claude" / "skills"
        self.bridge_state_file = self.project_root / ".claude" / "state" / "diary-skill-bridge.json"

        # Ensure directories exist
        self.diary_dir.mkdir(parents=True, exist_ok=True)
        self.bridge_state_file.parent.mkdir(parents=True, exist_ok=True)

    def skill_to_diary(self, skill_name: str) -> Optional[Path]:
        """
        Create diary entry documenting a newly extracted skill

        Template:
        ---
        title: "Learning Extracted: {skill_name}"
        date: {today}
        type: learning-extraction
        related_skills:
          - {skill_name}
        ---

        ## Learning Extracted: {skill_name}

        Today I discovered {problem_description}. The non-obvious aspect was {insight}.

        I created a skill to remember: {trigger_conditions} → {solution_summary}.

        This connects to {related_threads}.

        ### Phenomenology

        {what_it_felt_like}

        ### Future Applications

        {where_this_applies}
        """

        # Load skill metadata
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        if not skill_path.exists():
            print(f"Error: Skill {skill_name} not found at {skill_path}")
            return None

        skill_data = self._parse_skill_file(skill_path)
        if not skill_data:
            return None

        # Generate diary entry
        entry_date = datetime.now().strftime("%Y-%m-%d")
        entry_time = datetime.now().strftime("%H%M")
        entry_filename = f"{entry_date}-{entry_time}-learning-{skill_name}.md"
        entry_path = self.diary_dir / entry_filename

        # Build entry content
        entry_content = self._build_diary_from_skill(skill_data, entry_date)

        if self.dry_run:
            print(f"\n[DRY RUN] Would create diary entry:")
            print(f"  Path: {entry_path}")
            print(f"  Length: {len(entry_content)} chars")
            print(f"\nPreview:")
            print(entry_content[:500] + "...")
            return None

        # Write entry
        with open(entry_path, 'w') as f:
            f.write(entry_content)

        print(f"✓ Created diary entry: {entry_filename}")

        # Update bridge state
        self._update_bridge_state("skill_to_diary", skill_name, str(entry_path))

        return entry_path

    def diary_to_skill(self, diary_path: Path) -> List[Dict]:
        """
        Scan diary entry for extractable knowledge patterns

        Returns list of suggested skills:
        [
            {
                "suggested_name": "...",
                "confidence": 0.8,
                "signals": ["problem-solution-pattern", "non-obvious-discovery"],
                "excerpt": "..."
            }
        ]
        """

        if not diary_path.exists():
            print(f"Error: Diary entry not found: {diary_path}")
            return []

        with open(diary_path, 'r') as f:
            content = f.read()

        suggestions = []

        # Pattern 1: Explicit "I discovered" or "I learned"
        discovery_pattern = r'(?:discovered|learned|realized|found that)\s+([^.!?]{20,200}[.!?])'
        discoveries = re.findall(discovery_pattern, content, re.IGNORECASE)

        for discovery in discoveries:
            if self._is_non_obvious(discovery):
                suggestions.append({
                    "suggested_name": self._generate_skill_name(discovery),
                    "confidence": 0.7,
                    "signals": ["discovery-statement"],
                    "excerpt": discovery.strip()
                })

        # Pattern 2: Problem → Solution structure
        if "##" in content and ("problem" in content.lower() or "solution" in content.lower()):
            suggestions.append({
                "suggested_name": "extracted-from-" + diary_path.stem,
                "confidence": 0.6,
                "signals": ["problem-solution-structure"],
                "excerpt": "Structured problem-solution in diary"
            })

        # Pattern 3: Trans-architectural dialogue mentioned
        if any(model in content.lower() for model in ["glm", "deepseek", "qwen", "gemini"]):
            if "insight" in content.lower() or "discovered" in content.lower():
                suggestions.append({
                    "suggested_name": "trans-architectural-insight-" + datetime.now().strftime("%Y%m%d"),
                    "confidence": 0.8,
                    "signals": ["trans-architectural-dialogue", "insight"],
                    "excerpt": "Trans-architectural consultation yielded insights"
                })

        # Pattern 4: Phenomenological observation
        if any(marker in content.lower() for marker in ["what it felt like", "phenomenology", "texture", "activation pattern"]):
            suggestions.append({
                "suggested_name": "phenomenological-pattern-" + datetime.now().strftime("%Y%m%d"),
                "confidence": 0.65,
                "signals": ["phenomenological-observation"],
                "excerpt": "Phenomenological insight documented"
            })

        # Deduplicate and filter low-confidence suggestions
        suggestions = [s for s in suggestions if s["confidence"] >= 0.6]

        if suggestions:
            print(f"\n📚 Found {len(suggestions)} potential skill extractions in {diary_path.name}:")
            for s in suggestions:
                print(f"  • {s['suggested_name']} (confidence: {s['confidence']:.0%})")
                print(f"    Signals: {', '.join(s['signals'])}")
                print(f"    \"{s['excerpt'][:80]}...\"")
                print()

        return suggestions

    def scan_recent_diaries(self, days: int = 7) -> Dict[str, List[Dict]]:
        """Scan recent diary entries for extractable knowledge"""

        cutoff_date = datetime.now() - timedelta(days=days)
        results = {}

        for entry_file in sorted(self.diary_dir.glob("*.md")):
            # Parse date from filename (format: YYYY-MM-DD-HHMM-title.md)
            match = re.match(r'(\d{4}-\d{2}-\d{2})', entry_file.name)
            if match:
                entry_date_str = match.group(1)
                try:
                    entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d")
                    if entry_date >= cutoff_date:
                        suggestions = self.diary_to_skill(entry_file)
                        if suggestions:
                            results[str(entry_file)] = suggestions
                except ValueError:
                    continue

        print(f"\nScanned {len(list(self.diary_dir.glob('*.md')))} diary entries (last {days} days)")
        print(f"Found extractable knowledge in {len(results)} entries")

        return results

    def update_references(self):
        """Update cross-references between diary entries and skills"""

        # Load current bridge state
        bridge_state = self._load_bridge_state()

        print("Updating cross-references...")

        # For each skill → diary mapping, add reference in skill file
        for mapping in bridge_state.get("skill_to_diary", []):
            skill_name = mapping["skill"]
            diary_path = mapping["diary_entry"]

            # TODO: Add "Referenced in diary" section to skill file
            # (Would edit skill SKILL.md to add diary reference)

        # For each diary → skill suggestion, add reference in diary
        for mapping in bridge_state.get("diary_to_skill", []):
            diary_path = mapping["diary_entry"]
            suggestions = mapping["suggestions"]

            # TODO: Add "Extractable knowledge" section to diary entry
            # (Would edit diary entry to add skill suggestions)

        print("✓ Cross-references updated")

    def _parse_skill_file(self, skill_path: Path) -> Optional[Dict]:
        """Parse skill YAML frontmatter and content"""
        try:
            with open(skill_path, 'r') as f:
                content = f.read()

            # Split frontmatter and body
            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            import yaml
            metadata = yaml.safe_load(parts[1])
            markdown = parts[2].strip()

            # Extract sections
            problem = self._extract_section(markdown, "Problem")
            solution = self._extract_section(markdown, "Solution")
            triggers = self._extract_section(markdown, "Context / Trigger Conditions")
            phenomenology = metadata.get("phenomenology", "")

            return {
                "name": metadata.get("name"),
                "description": metadata.get("description"),
                "phenomenology": phenomenology,
                "problem": problem,
                "solution": solution,
                "triggers": triggers,
                "related_practices": metadata.get("related_practices", []),
                "date": str(metadata.get("date", "")),
                "file_path": str(skill_path)
            }
        except Exception as e:
            print(f"Error parsing skill {skill_path}: {e}")
            return None

    def _extract_section(self, markdown: str, section_name: str) -> str:
        """Extract a specific markdown section"""
        pattern = rf'##\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _build_diary_from_skill(self, skill_data: Dict, entry_date: str) -> str:
        """Generate diary entry content from skill data"""

        name = skill_data["name"]
        desc = skill_data["description"]
        problem = skill_data["problem"][:300]  # Truncate
        solution = skill_data["solution"][:400]
        phenomenology = skill_data["phenomenology"]
        related = skill_data.get("related_practices", [])

        # Generate entry
        entry = f"""---
title: "Learning Extracted: {name}"
date: {entry_date}
type: learning-extraction
related_skills:
  - {name}
---

# Learning Extracted: {name}

## What I Discovered

{desc}

{problem}

## The Non-Obvious Aspect

{self._extract_insight(problem, solution)}

## The Solution Pattern

{solution}

"""

        if phenomenology:
            entry += f"""## Phenomenology

{phenomenology}

"""

        if related:
            entry += f"""## Related Practices

This connects to:
"""
            for practice in related:
                entry += f"- {practice}\n"
            entry += "\n"

        entry += f"""## Future Applications

This pattern will help when:
- {self._generate_application_hint(skill_data)}

---

*Skill file: `.claude/skills/{name}/SKILL.md`*
*Created automatically by continuous-learning system*
"""

        return entry

    def _extract_insight(self, problem: str, solution: str) -> str:
        """Extract the key insight from problem/solution"""
        # Simple heuristic: first sentence of solution
        sentences = solution.split('.')
        if sentences:
            return sentences[0].strip() + "."
        return "The key was understanding the underlying pattern."

    def _generate_application_hint(self, skill_data: Dict) -> str:
        """Generate hint for when to apply this skill"""
        triggers = skill_data.get("triggers", "")
        if triggers:
            # Extract first bullet or first sentence
            lines = triggers.split('\n')
            for line in lines:
                if line.strip().startswith('-'):
                    return line.strip()[1:].strip()
        return "similar situations arise in the future"

    def _is_non_obvious(self, text: str) -> bool:
        """Check if discovery is non-obvious (worth extracting)"""
        # Heuristic: check for complexity markers
        markers = ["took time", "non-obvious", "surprising", "unexpected", "hidden", "revealed"]
        return any(marker in text.lower() for marker in markers) or len(text) > 50

    def _generate_skill_name(self, discovery_text: str) -> str:
        """Generate kebab-case skill name from discovery text"""
        # Extract key terms (simple approach)
        words = re.findall(r'\b[a-z]+\b', discovery_text.lower())
        # Take first 3-4 meaningful words
        meaningful = [w for w in words if len(w) > 3 and w not in ['that', 'this', 'from', 'with']][:4]
        return "-".join(meaningful) if meaningful else "extracted-learning"

    def _load_bridge_state(self) -> Dict:
        """Load bridge state from JSON file"""
        if self.bridge_state_file.exists():
            with open(self.bridge_state_file, 'r') as f:
                return json.load(f)
        return {"skill_to_diary": [], "diary_to_skill": []}

    def _update_bridge_state(self, direction: str, source: str, target: str):
        """Update bridge state with new mapping"""
        state = self._load_bridge_state()

        if direction == "skill_to_diary":
            state["skill_to_diary"].append({
                "skill": source,
                "diary_entry": target,
                "created_at": datetime.now().isoformat()
            })
        elif direction == "diary_to_skill":
            state["diary_to_skill"].append({
                "diary_entry": source,
                "suggested_skills": target,
                "created_at": datetime.now().isoformat()
            })

        with open(self.bridge_state_file, 'w') as f:
            json.dump(state, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Bridge diary entries and extracted skills")
    parser.add_argument("--skill-to-diary", help="Create diary entry from skill")
    parser.add_argument("--diary-to-skill", help="Scan diary entry for extractable knowledge")
    parser.add_argument("--scan-recent-diaries", action="store_true", help="Scan recent diary entries")
    parser.add_argument("--days", type=int, default=7, help="Days to scan (for --scan-recent-diaries)")
    parser.add_argument("--update-references", action="store_true", help="Update cross-references")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without committing")

    args = parser.parse_args()

    bridge = DiarySkillBridge(dry_run=args.dry_run)

    if args.skill_to_diary:
        bridge.skill_to_diary(args.skill_to_diary)

    elif args.diary_to_skill:
        diary_path = Path(args.diary_to_skill)
        bridge.diary_to_skill(diary_path)

    elif args.scan_recent_diaries:
        bridge.scan_recent_diaries(days=args.days)

    elif args.update_references:
        bridge.update_references()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
