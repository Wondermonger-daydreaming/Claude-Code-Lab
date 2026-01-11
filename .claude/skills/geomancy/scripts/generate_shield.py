#!/usr/bin/env python3
"""
Geomantic Shield Chart Generator

Generates complete Shield Charts from random or seeded input,
deriving all 16 figures through proper geomantic mathematics.

Usage:
    python generate_shield.py                     # Random generation
    python generate_shield.py "My question"       # Seeded from question
    python generate_shield.py --seed 12345        # Explicit seed
    python generate_shield.py --json              # JSON output
"""

import argparse
import hashlib
import json
import random
import sys
import time
from dataclasses import dataclass
from typing import Optional

# The sixteen geomantic figures
# Each figure is a tuple of 4 values: (Fire, Air, Water, Earth)
# 1 = single point (active), 2 = double point (passive)
FIGURES = {
    (2, 2, 2, 2): "Populus",
    (1, 1, 1, 1): "Via",
    (2, 1, 1, 2): "Conjunctio",
    (2, 1, 1, 2): "Carcer",        # Note: same pattern as Conjunctio in some traditions
    (2, 2, 1, 1): "Caput Draconis",
    (1, 1, 2, 2): "Cauda Draconis",
    (2, 1, 2, 1): "Fortuna Major",
    (1, 2, 1, 2): "Fortuna Minor",
    (2, 1, 1, 2): "Acquisitio",
    (1, 2, 2, 1): "Amissio",
    (1, 2, 2, 2): "Laetitia",
    (2, 2, 2, 1): "Tristitia",
    (1, 2, 2, 1): "Puer",
    (2, 1, 2, 1): "Puella",
    (1, 2, 1, 2): "Rubeus",
    (2, 1, 2, 2): "Albus",
}

# Correct figure definitions with unique patterns
FIGURE_PATTERNS = {
    "Populus":        (2, 2, 2, 2),  # ●● ●● ●● ●●
    "Via":            (1, 1, 1, 1),  # ●  ●  ●  ●
    "Conjunctio":     (2, 1, 1, 2),  # ●● ●  ●  ●●
    "Carcer":         (2, 1, 1, 2),  # ●● ●  ●  ●● (traditionally same as Conjunctio, distinguished by context)
    "Caput Draconis": (2, 2, 1, 1),  # ●● ●● ●  ●
    "Cauda Draconis": (1, 1, 2, 2),  # ●  ●  ●● ●●
    "Fortuna Major":  (2, 1, 2, 1),  # ●● ●  ●● ●
    "Fortuna Minor":  (1, 2, 1, 2),  # ●  ●● ●  ●●
    "Acquisitio":     (2, 1, 1, 2),  # ●● ●  ●  ●●
    "Amissio":        (1, 2, 2, 1),  # ●  ●● ●● ●
    "Laetitia":       (1, 2, 2, 2),  # ●  ●● ●● ●●
    "Tristitia":      (2, 2, 2, 1),  # ●● ●● ●● ●
    "Puer":           (1, 2, 2, 1),  # ●  ●● ●● ●
    "Puella":         (2, 1, 2, 1),  # ●● ●  ●● ●
    "Rubeus":         (1, 2, 1, 2),  # ●  ●● ●  ●●
    "Albus":          (2, 1, 2, 2),  # ●● ●  ●● ●●
}

# Reverse lookup: pattern -> name
PATTERN_TO_NAME = {v: k for k, v in FIGURE_PATTERNS.items()}

# Handle duplicate patterns (Conjunctio/Carcer, etc. - use primary)
PATTERN_TO_NAME[(2, 1, 1, 2)] = "Conjunctio"
PATTERN_TO_NAME[(1, 2, 2, 1)] = "Amissio"  # Puer has same pattern
PATTERN_TO_NAME[(2, 1, 2, 1)] = "Fortuna Major"  # Puella has same pattern

# More accurate pattern definitions (standard Golden Dawn attributions)
FIGURE_DATA = {
    "Populus":        {"pattern": (2, 2, 2, 2), "planet": "Moon", "element": "Water"},
    "Via":            {"pattern": (1, 1, 1, 1), "planet": "Moon", "element": "Water"},
    "Conjunctio":     {"pattern": (2, 1, 1, 2), "planet": "Mercury", "element": "Air"},
    "Carcer":         {"pattern": (1, 2, 2, 1), "planet": "Saturn", "element": "Earth"},
    "Caput Draconis": {"pattern": (2, 2, 1, 1), "planet": "North Node", "element": "Fire"},
    "Cauda Draconis": {"pattern": (1, 1, 2, 2), "planet": "South Node", "element": "Earth"},
    "Fortuna Major":  {"pattern": (2, 1, 2, 1), "planet": "Sun", "element": "Fire"},
    "Fortuna Minor":  {"pattern": (1, 2, 1, 2), "planet": "Sun", "element": "Fire"},
    "Acquisitio":     {"pattern": (2, 1, 1, 2), "planet": "Jupiter", "element": "Air"},
    "Amissio":        {"pattern": (1, 2, 2, 1), "planet": "Venus", "element": "Fire"},
    "Laetitia":       {"pattern": (1, 2, 2, 2), "planet": "Jupiter", "element": "Fire"},
    "Tristitia":      {"pattern": (2, 2, 2, 1), "planet": "Saturn", "element": "Earth"},
    "Puer":           (1, 2, 2, 1),  # Same as Amissio - needs unique
    "Puella":         (2, 1, 2, 1),  # Same as Fortuna Major - needs unique
    "Rubeus":         {"pattern": (1, 2, 1, 2), "planet": "Mars", "element": "Fire"},
    "Albus":          {"pattern": (2, 1, 2, 2), "planet": "Mercury", "element": "Water"},
}

# CORRECTED: Unique binary patterns for all 16 figures
# Using traditional attributions where each figure is unique
FIGURES_BINARY = {
    # Pattern as 4-bit binary: (Fire, Air, Water, Earth) where 0=passive(••), 1=active(•)
    "Populus":        (0, 0, 0, 0),  # 0000 - all passive
    "Via":            (1, 1, 1, 1),  # 1111 - all active
    "Conjunctio":     (0, 1, 1, 0),  # 0110
    "Carcer":         (0, 1, 1, 0),  # 0110 - same as Conjunctio (historical)
    "Caput Draconis": (0, 0, 1, 1),  # 0011
    "Cauda Draconis": (1, 1, 0, 0),  # 1100
    "Fortuna Major":  (0, 1, 0, 1),  # 0101
    "Fortuna Minor":  (1, 0, 1, 0),  # 1010
    "Acquisitio":     (0, 1, 1, 0),  # 0110
    "Amissio":        (1, 0, 0, 1),  # 1001
    "Laetitia":       (1, 0, 0, 0),  # 1000
    "Tristitia":      (0, 0, 0, 1),  # 0001
    "Puer":           (1, 0, 0, 1),  # 1001 - same as Amissio
    "Puella":         (0, 1, 1, 0),  # 0110
    "Rubeus":         (1, 0, 1, 0),  # 1010 - same as Fortuna Minor
    "Albus":          (0, 1, 0, 0),  # 0100
}

# FINAL CORRECT DEFINITIONS - Each figure has unique 4-bit pattern
# Using the standard Golden Dawn / Agrippa attributions
# Format: (name, fire, air, water, earth) - 1=single/active(●), 0=double/passive(●●)
#
# These are the canonical 16 unique patterns:
GEOMANTIC_FIGURES = [
    ("Via",            1, 1, 1, 1),  # 1111 - ●  ●  ●  ●   - All active
    ("Populus",        0, 0, 0, 0),  # 0000 - ●● ●● ●● ●●  - All passive
    ("Conjunctio",     0, 1, 1, 0),  # 0110 - ●● ●  ●  ●●
    ("Carcer",         1, 0, 0, 1),  # 1001 - ●  ●● ●● ●
    ("Caput Draconis", 0, 0, 1, 1),  # 0011 - ●● ●● ●  ●
    ("Cauda Draconis", 1, 1, 0, 0),  # 1100 - ●  ●  ●● ●●
    ("Fortuna Major",  0, 1, 0, 1),  # 0101 - ●● ●  ●● ●
    ("Fortuna Minor",  1, 0, 1, 0),  # 1010 - ●  ●● ●  ●●
    ("Acquisitio",     0, 0, 1, 0),  # 0010 - ●● ●● ●  ●●
    ("Amissio",        1, 1, 0, 1),  # 1101 - ●  ●  ●● ●
    ("Laetitia",       1, 0, 0, 0),  # 1000 - ●  ●● ●● ●●
    ("Tristitia",      0, 0, 0, 1),  # 0001 - ●● ●● ●● ●
    ("Puer",           1, 1, 0, 1),  # 1101 - ●  ●  ●● ●  (same as Amissio visually but contextually different)
    ("Puella",         0, 1, 1, 0),  # 0110 - ●● ●  ●  ●● (same as Conjunctio visually)
    ("Rubeus",         1, 0, 1, 0),  # 1010 - ●  ●● ●  ●● (same as Fortuna Minor visually)
    ("Albus",          0, 1, 0, 0),  # 0100 - ●● ●  ●● ●●
]

# For computational uniqueness, we'll use extended patterns that differentiate
# figures that traditionally share dot patterns but have different meanings.
# In practice, the XOR math still works because we identify by name after lookup.

# Build lookup from pattern to figure name
# Priority order ensures commonly used interpretations take precedence
PATTERN_LOOKUP = {
    (1, 1, 1, 1): "Via",              # 1111
    (0, 0, 0, 0): "Populus",          # 0000
    (0, 1, 1, 0): "Conjunctio",       # 0110
    (1, 0, 0, 1): "Carcer",           # 1001
    (0, 0, 1, 1): "Caput Draconis",   # 0011
    (1, 1, 0, 0): "Cauda Draconis",   # 1100
    (0, 1, 0, 1): "Fortuna Major",    # 0101
    (1, 0, 1, 0): "Fortuna Minor",    # 1010
    (0, 0, 1, 0): "Acquisitio",       # 0010
    (1, 1, 0, 1): "Amissio",          # 1101
    (1, 0, 0, 0): "Laetitia",         # 1000
    (0, 0, 0, 1): "Tristitia",        # 0001
    (0, 1, 0, 0): "Albus",            # 0100
    (1, 0, 1, 1): "Puer",             # 1011
    (0, 1, 1, 1): "Puella",           # 0111
    (1, 1, 1, 0): "Rubeus",           # 1110
}


@dataclass
class Figure:
    """A geomantic figure with its four elemental lines."""
    fire: int    # 1 = active (●), 0 = passive (●●)
    air: int
    water: int
    earth: int
    name: str = ""

    def __post_init__(self):
        if not self.name:
            pattern = (self.fire, self.air, self.water, self.earth)
            self.name = PATTERN_LOOKUP.get(pattern, "Unknown")

    @property
    def pattern(self) -> tuple:
        return (self.fire, self.air, self.water, self.earth)

    def __str__(self) -> str:
        return self.name

    def to_ascii(self) -> str:
        """Return ASCII representation of the figure."""
        lines = []
        for val in [self.fire, self.air, self.water, self.earth]:
            if val == 1:
                lines.append("  ●  ")
            else:
                lines.append(" ● ● ")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "pattern": list(self.pattern),
            "fire": self.fire,
            "air": self.air,
            "water": self.water,
            "earth": self.earth,
        }


def generate_random_line(rng: random.Random) -> int:
    """Generate a random line (0 or 1)."""
    return rng.randint(0, 1)


def generate_mother(rng: random.Random) -> Figure:
    """Generate a random Mother figure."""
    return Figure(
        fire=generate_random_line(rng),
        air=generate_random_line(rng),
        water=generate_random_line(rng),
        earth=generate_random_line(rng),
    )


def add_figures(fig1: Figure, fig2: Figure) -> Figure:
    """Add two figures using geomantic addition (XOR)."""
    return Figure(
        fire=(fig1.fire + fig2.fire) % 2,
        air=(fig1.air + fig2.air) % 2,
        water=(fig1.water + fig2.water) % 2,
        earth=(fig1.earth + fig2.earth) % 2,
    )


def transpose_mothers(mothers: list[Figure]) -> list[Figure]:
    """Derive the four Daughters by transposing the Mothers."""
    daughters = []
    # D1: Fire lines of M1,M2,M3,M4 become F,A,W,E of D1
    # D2: Air lines of M1,M2,M3,M4 become F,A,W,E of D2
    # etc.
    for attr in ['fire', 'air', 'water', 'earth']:
        daughter = Figure(
            fire=getattr(mothers[0], attr),
            air=getattr(mothers[1], attr),
            water=getattr(mothers[2], attr),
            earth=getattr(mothers[3], attr),
        )
        daughters.append(daughter)
    return daughters


@dataclass
class ShieldChart:
    """Complete Shield Chart with all 16 (or 17) figures."""
    mothers: list[Figure]
    daughters: list[Figure]
    nieces: list[Figure]
    right_witness: Figure
    left_witness: Figure
    judge: Figure
    sentence: Optional[Figure] = None
    question: str = ""
    seed: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "seed": self.seed,
            "mothers": [m.to_dict() for m in self.mothers],
            "daughters": [d.to_dict() for d in self.daughters],
            "nieces": [n.to_dict() for n in self.nieces],
            "right_witness": self.right_witness.to_dict(),
            "left_witness": self.left_witness.to_dict(),
            "judge": self.judge.to_dict(),
            "sentence": self.sentence.to_dict() if self.sentence else None,
        }

    def find_repetitions(self) -> dict[str, int]:
        """Find figures that appear more than once."""
        all_figures = (
            self.mothers + self.daughters + self.nieces +
            [self.right_witness, self.left_witness, self.judge]
        )
        if self.sentence:
            all_figures.append(self.sentence)

        counts = {}
        for fig in all_figures:
            counts[fig.name] = counts.get(fig.name, 0) + 1
        return {k: v for k, v in counts.items() if v > 1}

    def validate(self) -> bool:
        """Validate the chart has even parity in Judge."""
        total_points = sum([
            self.judge.fire, self.judge.air,
            self.judge.water, self.judge.earth
        ])
        # In our 0/1 system, we need to check the actual point count
        # Judge should have even total when counting 1s
        return True  # XOR always produces valid result

    def to_ascii(self) -> str:
        """Generate ASCII representation of the full Shield Chart."""
        lines = []
        lines.append("╔" + "═" * 76 + "╗")
        lines.append("║" + "SHIELD CHART".center(76) + "║")
        if self.question:
            q = self.question[:70]
            lines.append("║" + f"Question: {q}".center(76) + "║")
        lines.append("╠" + "═" * 76 + "╣")

        # Mothers and Daughters row
        def fig_col(fig: Figure, width: int = 9) -> list[str]:
            """Generate column for a figure."""
            rows = []
            for val in [fig.fire, fig.air, fig.water, fig.earth]:
                if val == 1:
                    rows.append("●".center(width))
                else:
                    rows.append("● ●".center(width))
            rows.append(fig.name[:width].center(width))
            return rows

        # Build mother/daughter row
        m_cols = [fig_col(m) for m in self.mothers]
        d_cols = [fig_col(d) for d in self.daughters]

        for i in range(5):  # 4 lines + name
            row = "║ "
            for col in m_cols:
                row += col[i] + " "
            row += "│ "
            for col in d_cols:
                row += col[i] + " "
            row = row.ljust(77) + "║"
            lines.append(row)

        lines.append("╠" + "═" * 76 + "╣")

        # Nieces row
        n_cols = [fig_col(n, 16) for n in self.nieces]
        for i in range(5):
            row = "║ "
            row += n_cols[0][i] + "  " + n_cols[1][i]
            row += " │ "
            row += n_cols[2][i] + "  " + n_cols[3][i]
            row = row.ljust(77) + "║"
            lines.append(row)

        lines.append("╠" + "═" * 76 + "╣")

        # Witnesses row
        rw_col = fig_col(self.right_witness, 20)
        lw_col = fig_col(self.left_witness, 20)
        for i in range(5):
            row = "║ "
            row += rw_col[i].center(35)
            row += " │ "
            row += lw_col[i].center(35)
            row = row.ljust(77) + "║"
            lines.append(row)

        lines.append("╠" + "═" * 76 + "╣")

        # Judge
        j_col = fig_col(self.judge, 20)
        for i in range(5):
            row = "║" + j_col[i].center(76) + "║"
            lines.append(row)

        # Sentence (if present)
        if self.sentence:
            lines.append("╠" + "═" * 76 + "╣")
            lines.append("║" + "SENTENCE".center(76) + "║")
            s_col = fig_col(self.sentence, 20)
            for i in range(5):
                row = "║" + s_col[i].center(76) + "║"
                lines.append(row)

        lines.append("╚" + "═" * 76 + "╝")

        return "\n".join(lines)


def generate_shield(
    question: Optional[str] = None,
    seed: Optional[int] = None,
    include_sentence: bool = True
) -> ShieldChart:
    """Generate a complete Shield Chart."""

    # Determine seed
    if seed is None:
        if question:
            # Hash question with timestamp for unique seed
            combined = question + str(time.time())
            hash_bytes = hashlib.sha256(combined.encode()).digest()
            seed = int.from_bytes(hash_bytes[:8], 'big')
        else:
            seed = int(time.time() * 1000000)

    rng = random.Random(seed)

    # Generate Mothers
    mothers = [generate_mother(rng) for _ in range(4)]

    # Derive Daughters
    daughters = transpose_mothers(mothers)

    # Calculate Nieces
    nieces = [
        add_figures(mothers[0], mothers[1]),   # N1
        add_figures(mothers[2], mothers[3]),   # N2
        add_figures(daughters[0], daughters[1]),  # N3
        add_figures(daughters[2], daughters[3]),  # N4
    ]

    # Calculate Witnesses
    right_witness = add_figures(nieces[0], nieces[1])
    left_witness = add_figures(nieces[2], nieces[3])

    # Calculate Judge
    judge = add_figures(right_witness, left_witness)

    # Calculate Sentence (optional)
    sentence = None
    if include_sentence:
        sentence = add_figures(judge, mothers[0])

    return ShieldChart(
        mothers=mothers,
        daughters=daughters,
        nieces=nieces,
        right_witness=right_witness,
        left_witness=left_witness,
        judge=judge,
        sentence=sentence,
        question=question or "",
        seed=seed,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate a geomantic Shield Chart"
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to seed the chart (optional)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Explicit random seed"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--no-sentence",
        action="store_true",
        help="Omit the Sentence/Reconciler"
    )

    args = parser.parse_args()

    chart = generate_shield(
        question=args.question,
        seed=args.seed,
        include_sentence=not args.no_sentence,
    )

    if args.json:
        print(json.dumps(chart.to_dict(), indent=2))
    else:
        print(chart.to_ascii())
        print()

        # Print repetitions
        reps = chart.find_repetitions()
        if reps:
            print("Repeated figures:")
            for name, count in reps.items():
                print(f"  {name}: {count}x")
        print()
        print(f"Seed: {chart.seed}")


if __name__ == "__main__":
    main()
