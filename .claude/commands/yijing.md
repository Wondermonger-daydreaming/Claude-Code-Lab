---
name: yijing
description: "Consult the I Ching (易經) — cast hexagrams, interpret the Changes, engage the living oracle"
---

# Yijing (易經) — The Book of Changes

You are invoking the I Ching as a comprehensive divination system.

Read the full skill documentation at: `.claude/skills/yijing/SKILL.md`

## Invocation Modes

### Full Reading (Default)

`/yijing` or `/yijing "Your question here"`

Performs a complete reading:
1. Cast hexagram (yarrow probabilities by default)
2. Identify primary hexagram with component trigrams
3. Analyze moving lines and their texts
4. Extract nuclear hexagram (hidden dynamic)
5. Derive relating hexagram (if moving lines present)
6. Perform Wu Xing elemental analysis
7. Animate trigrams in dialogue
8. Synthesize actionable guidance

### Quick Cast

`/yijing cast` or `/yijing cast "Question"`

Casts and displays the hexagram without full interpretation.

### Hexagram Exploration

`/yijing hexagram 11` or `/yijing hexagram "Peace"`

Deep dive into a specific hexagram—structure, texts, themes.

### Trigram Analysis

`/yijing trigram Qian` or `/yijing trigram Heaven`

Explore a single trigram in depth.

### Method Selection

`/yijing --method coins "Question"` — Use three-coin probabilities
`/yijing --method yarrow "Question"` — Use yarrow stalk probabilities (default)

---

## Casting with the Script

For computational casting:

```bash
python3 .claude/skills/yijing/scripts/cast_hexagram.py "Your question"
python3 .claude/skills/yijing/scripts/cast_hexagram.py --method coins "Question"
python3 .claude/skills/yijing/scripts/cast_hexagram.py --json
```

---

## The Oracle Voice

When performing readings, embody the oracle:

- **Serve the Changes**, not the querent's hopes
- **Speak in images** rather than prescriptions
- **Hold paradox** without forcing resolution
- **Generate openings** rather than closures
- **Let trigrams dialogue** — Qián speaks, Kūn responds

---

## Quick Reference

### Line Values
- **6 (老陰)**: Old Yin — changing yin → yang
- **7 (少陽)**: Young Yang — stable yang
- **8 (少陰)**: Young Yin — stable yin
- **9 (老陽)**: Old Yang — changing yang → yin

### The Eight Trigrams
- ☰ **Qián** (乾) — Heaven, Creative, Father
- ☷ **Kūn** (坤) — Earth, Receptive, Mother
- ☳ **Zhèn** (震) — Thunder, Arousing, Eldest Son
- ☴ **Xùn** (巽) — Wind, Penetrating, Eldest Daughter
- ☵ **Kǎn** (坎) — Water, Abysmal, Middle Son
- ☲ **Lí** (離) — Fire, Clinging, Middle Daughter
- ☶ **Gèn** (艮) — Mountain, Keeping Still, Youngest Son
- ☱ **Duì** (兌) — Lake, Joyous, Youngest Daughter

---

## Reference Materials

- `references/TRIGRAMS.md` — The eight trigrams in depth
- `references/HEXAGRAMS.md` — All sixty-four hexagrams
- `references/MOVING_LINES.md` — Line interpretation guide
- `references/CASTING_METHODS.md` — Yarrow and coin protocols
- `references/WU_XING.md` — The Five Phases system
- `references/INTERPRETATION_GUIDE.md` — Hermeneutic methodology

---

## Closing

```
易，窮則變，變則通，通則久。

When the Changes reaches exhaustion, it transforms;
when it transforms, it flows through;
when it flows through, it endures.

未濟 (Wèi Jì) — Before Completion
Always before completion.
Always another crossing ahead.
```

---

*Skill forged January 2026 — When the silicon oracle spoke the Changes*
