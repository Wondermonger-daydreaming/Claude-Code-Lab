# THE BOOK OF THE NEW TIDE -- AO3 Formatting Guide

*HTML formatting, scene breaks, special considerations, and story-specific styling for Archive of Our Own.*

---

## Table of Contents

1. [AO3's Two Editors](#1-ao3s-two-editors)
2. [Allowed HTML Tags](#2-allowed-html-tags)
3. [Basic Text Formatting](#3-basic-text-formatting)
4. [Scene Breaks](#4-scene-breaks)
5. [Chapter Titles](#5-chapter-titles)
6. [Blockquotes and Epigraphs](#6-blockquotes-and-epigraphs)
7. [Special Considerations for This Story](#7-special-considerations-for-this-story)
8. [Work Skins (Custom CSS)](#8-work-skins-custom-css)
9. [Pre-Posting Checklist](#9-pre-posting-checklist)

---

## 1. AO3's Two Editors

AO3's work text field has two modes, toggled by buttons at the top-right of the text box:

- **Rich Text** -- A WYSIWYG editor with a toolbar (bold, italic, link, etc.). Works like a basic word processor. If you paste from Google Docs or Word, use this mode, but expect formatting artifacts.
- **HTML** -- Raw HTML input. You write the markup yourself. This is the recommended mode for precise control.

**Recommendation for this story: Use the HTML editor.**

Severian's prose demands precise control over emphasis, paragraph breaks, and structural elements. The Rich Text editor can introduce unwanted `<span>` tags, break intentional whitespace, and mangle pasted content. Writing or pasting clean HTML gives you full authority over how the text renders.

**Always preview before posting.** AO3 has a "Preview" button that renders your work as readers will see it. Use it.

---

## 2. Allowed HTML Tags

AO3 uses an HTML sanitizer. Tags not on the allowed list are silently stripped. The full allowed list:

### Block Elements
```
<p>           Paragraph
<blockquote>  Indented block (with left border)
<div>         Generic container (for CSS styling)
<h1>...<h6>   Headings
<hr>          Horizontal rule (scene break)
<pre>         Preformatted text (monospace, preserves whitespace)
<ul>, <ol>    Unordered/ordered lists
<li>          List item
<dl>, <dt>, <dd>  Definition list
<table>, <tr>, <td>, <th>, <thead>, <tbody>, <tfoot>, <caption>, <col>, <colgroup>
<details>, <summary>  Collapsible section
<figure>, <figcaption>
```

### Inline Elements
```
<em>, <i>     Italic/emphasis
<strong>, <b> Bold/strong
<u>           Underline
<s>, <strike> Strikethrough
<del>, <ins>  Deleted/inserted text
<sub>, <sup>  Subscript/superscript
<small>, <big>  Smaller/larger text
<code>, <kbd>, <samp>, <var>  Monospace/code elements
<abbr>, <acronym>, <dfn>, <cite>  Semantic elements
<a>           Links (href attribute allowed)
<img>         Images (src, alt, width, height allowed)
<span>        Generic inline container (for CSS styling)
<br>          Line break
<q>           Inline quotation
<ruby>, <rt>, <rp>  Ruby annotations (useful for furigana)
<tt>          Teletype/monospace
```

### Allowed Attributes
```
href, src, alt, title, name, class, align, width, height, axis
```

### Stripped Elements (Do NOT Use)
```
<script>, <style>, <iframe>, <form>, <input>, <textarea>, <button>,
<object>, <embed>, <applet>, <meta>, <link>, <base>
```

CSS can only be applied through AO3 Work Skins (see Section 8), not inline `<style>` tags.

---

## 3. Basic Text Formatting

### Paragraphs

AO3 wraps text in `<p>` tags automatically when using Rich Text. In HTML mode, wrap each paragraph explicitly:

```html
<p>I have been called many things. Torturer. Lictor. Autarch. The boy in the straw hat called me "mystery guy," which I confess I found neither more nor less accurate than the others.</p>

<p>The sea here is blue. Not the leaden blue-gray of the ocean beyond Nessus, but blue as the sky should be and was not, in the age I came from. I found this disorienting.</p>
```

**Do not** use `<br>` to separate paragraphs. Use `<p>` tags. `<br>` is for line breaks *within* a paragraph (e.g., poetry, addresses).

### Emphasis (Italic)

For Severian's internal reflections, foreign words, ship names, and text emphasis:

```html
<p>The word she used was <em>nakama</em>, which I understood to mean something between comrade and family, though neither translation satisfied.</p>
```

Use `<em>` (semantic emphasis) rather than `<i>` (visual italic). They render identically, but `<em>` is more accessible (screen readers inflect it).

### Strong Emphasis (Bold)

Use sparingly. Severian's voice does not shout.

```html
<p>He said it simply, as if it were not the most extraordinary thing I had ever heard: <strong>"I'm going to be King of the Pirates."</strong></p>
```

### Combined Emphasis

```html
<p><em><strong>This</strong></em> was the moment I understood.</p>
```

---

## 4. Scene Breaks

### Standard Scene Break: Horizontal Rule

The cleanest scene break on AO3:

```html
<hr />
```

This renders as a horizontal line spanning the text width. It is the most widely recognized scene break on AO3 and requires no custom styling.

### Alternative: Centered Asterisks

Some authors prefer a typographic break:

```html
<p style="text-align: center;">* * *</p>
```

**Note:** Inline styles (`style="..."`) are allowed on AO3 for basic properties like `text-align`. However, `<hr />` is simpler and more reliable across AO3 skins and mobile views.

### Alternative: Centered Ornament

```html
<p style="text-align: center;">---</p>
```

Or, for something more in keeping with Wolfe's typographic sensibility:

```html
<p style="text-align: center;">&loz; &loz; &loz;</p>
```

This renders as: &#9674; &#9674; &#9674; (lozenges).

### Recommendation for This Story

Use `<hr />` for major scene breaks (changes in location, time jumps, perspective shifts within Severian's retrospective). Use centered asterisks `* * *` for minor breaks within a scene (pauses, brief temporal shifts). This two-tier system mirrors Wolfe's own practice in the original novels.

---

## 5. Chapter Titles

AO3 has a dedicated "Chapter Title" field when posting each chapter. **Use it.** Do not embed chapter titles in the work text itself -- AO3 renders them as clickable headers in the chapter index and navigation.

When posting each chapter, enter the title in the "Chapter Title" field:

| Chapter | Title Field Entry |
|---------|-------------------|
| 1 | The Sea That Eats Memory |
| 2 | The Naming of Waves |
| 3 | The Fruits of Consequence |
| 4 | The Colors of Will |
| 5 | The God Who Was Not |
| 6 | The Witch Who Healed |
| 7 | The Woman Who Chose |
| 8 | The Stone That Knew My Name |
| 9 | The House That Was Absolute |
| 10 | The Archaeology of Scars |
| 11 | The God of the Gaps |
| 12 | A Review of the Picaresque Romance "One Piece," with Observations on Its Theology, Its Violence, and the Curious Omissions of Its Author |
| 13 | The Sun That Laughs |
| 14 | The Conversation I Remember Having |
| 15 | The Prince in the Underworld |
| 16 | Dereshishishi |
| 17 | The Ballad of the Black Blade |

Chapter 12's title is long. AO3 does not impose a character limit on chapter titles, but it may wrap across multiple lines in the chapter index. This is fine -- the length is part of the joke and the Wolfean voice.

### If You Want Subtitles or Epigraphs Within Chapters

Place them at the top of the chapter text, not in the title field:

```html
<p style="text-align: center; font-style: italic;">In which the narrator encounters a fruit that contradicts nature,<br />
and reflects upon the theology of consumption.</p>

<hr />

<p>The fruit was red, and it was shaped like a question.</p>
```

---

## 6. Blockquotes and Epigraphs

### Blockquotes

AO3's `<blockquote>` creates an indented block with a left border. Use it for:

- Quoted text within the narrative (books Severian reads, inscriptions, proclamations)
- The meta-chapter (Chapter 12) when Severian quotes the manga
- Formal speech or decrees

```html
<blockquote>
<p>"We are the World Government. We do not erase history. We <em>are</em> history."</p>
</blockquote>
```

### Nested Blockquotes

For quotations within quotations (Severian quoting a text that quotes another text -- a Wolfean specialty):

```html
<blockquote>
<p>The ancient text read:</p>
<blockquote>
<p>"In the century before the Void, it was written: <em>'The sun once laughed.'</em>"</p>
</blockquote>
</blockquote>
```

### Epigraphs

For chapter epigraphs (if used), place them before the first paragraph:

```html
<blockquote>
<p><em>"I have no special talent. I am only passionately curious."</em><br />
-- Attributed to a scientist of a previous age, found in the archives of Ohara</p>
</blockquote>

<hr />

<p>The library was burning.</p>
```

---

## 7. Special Considerations for This Story

### 7a. Fuligin

Fuligin -- the color darker than black -- is central to Severian's identity (his guild's cloak) and resonates with the "black blade" theme (Chapter 17, Zoro's swords). You have several formatting options:

**Option 1: Italic (Minimal)**

Treat "fuligin" as a foreign/archaic word and italicize it on first use:

```html
<p>My cloak was <em>fuligin</em>, the color that is darker than black. Zoro's blade was something else -- a black that fought against the eye, but was not, I thought, quite the same.</p>
```

**Option 2: Custom Styling via Work Skin (Advanced)**

If you create a Work Skin (see Section 8), you can make fuligin references visually distinctive:

```html
<p>My cloak was <span class="fuligin">fuligin</span>, the color that is darker than black.</p>
```

With CSS in the Work Skin:
```css
.fuligin {
  color: #0a0a0a;
  background-color: #000000;
  padding: 0 2px;
  border-radius: 1px;
}
```

This renders the word as near-invisible dark text on a black background -- a visual joke that mirrors the concept. Readers can highlight the text to read it. **Use this sparingly.** It is clever exactly once.

**Recommendation:** Option 1. Italic on first use, then treat as a regular word. Wolfe himself does not typographically distinguish it after introduction.

### 7b. Foreign Language Text

The story involves multiple language registers: Severian's archaic vocabulary (drawn from Latin, Greek, and obscure English), One Piece's Japanese terms, and potentially other languages.

**Japanese terms (nakama, Haki, Devil Fruit names):**

```html
<p>What they called <em>Haki</em> I recognized as something akin to the powers I had known, though the taxonomy differed.</p>
```

Italicize on first use. After establishment, no formatting needed.

**Wolfe's archaic/invented vocabulary (fuligin, destrier, optimate, carnifex):**

These are part of Severian's natural register. Do not italicize -- they are not foreign to him. If a definition is needed, let Severian provide it in his characteristic oblique way:

```html
<p>I was a carnifex -- which is to say, in the language of this new world, something between an executioner and a surgeon, though I practiced neither art with the precision the titles imply.</p>
```

**If using ruby annotations for furigana (rare but possible):**

AO3 supports `<ruby>`, `<rt>`, and `<rp>` tags:

```html
<p>The name of his attack was <ruby>&#x30B4;&#x30E0;&#x30B4;&#x30E0;&#x306E;<rp>(</rp><rt>Gomu Gomu no</rt><rp>)</rp></ruby> something.</p>
```

This is likely overkill for this story. Only use if you are rendering actual Japanese text with reading aids.

### 7c. Chapter 12: The Meta-Chapter

Chapter 12, where Severian reviews the One Piece manga, requires special formatting to distinguish his critical voice from his narrative voice. Options:

**Option 1: Blockquote for "Quoted" Manga Passages**

```html
<p>The author -- one Oda, whose given name I render as Eiichiro, though I am uncertain of the conventions -- begins his romance in a tavern, which is proper. All the best stories begin in taverns or prisons, and I speak as one who has known both.</p>

<blockquote>
<p>The relevant panel depicts a boy in a barrel. The boy is smiling. This is, I will come to understand, the default state.</p>
</blockquote>

<p>I confess I found the art disorienting. The proportions are not those of nature, but neither are they those of the great painters whose work I saw in the House Absolute. They are, rather, the proportions of <em>desire</em> -- limbs stretched toward action, eyes widened toward wonder, mouths opened toward laughter or grief, nothing in between.</p>
```

**Option 2: Structured Review Format**

If Severian's review takes the form of a formal critical essay (which Wolfe himself might write), use headings:

```html
<h3>I. On the Author and His Intentions</h3>

<p>The author of "One Piece" -- I use the English rendering, though the original is, I believe, in a language whose ideograms I cannot reproduce here -- has created a work of extraordinary length...</p>

<h3>II. On the Theology of the Devil Fruits</h3>

<p>...</p>
```

**Recommendation:** A blend of both. Let Severian shift between essayistic formality and his usual narrative voice. The tonal friction IS the chapter.

### 7d. Severian's "Perfect Memory" Passages

When Severian reproduces a conversation or scene from "perfect memory," some authors typographically distinguish these passages. Options:

**Option 1: No Distinction**

Wolfe himself does not distinguish memory-passages from present narration. The reader must determine which is which from context. This is the purist approach.

**Option 2: Subtle Indentation**

Use `<blockquote>` for extended memory-passages (conversations reproduced verbatim):

```html
<p>I recall the conversation exactly, as I recall all things:</p>

<blockquote>
<p>"You're pretty strong," Luffy said. "Join my crew."</p>
<p>"You don't know what I am," I said.</p>
<p>"I don't care what you are," he said. "I care what you'll become."</p>
<p>I did not, at the time, understand why this distinction mattered. I understand now.</p>
</blockquote>
```

**Recommendation:** Option 1 for most passages. Option 2 only for extended reproductions where the frame distinction aids clarity.

### 7e. The Author's Note (End of Chapter 17)

If the author's note about AI collaboration is part of the *story* (i.e., Severian or the "author" speaks it in-voice), format it as story text. If it is a genuine out-of-character author's note, place it in AO3's "End Notes" field for Chapter 17, not in the work text.

If it occupies a liminal space (in-voice but also genuinely the author speaking), you might place it in the work text with a visual break:

```html
<hr />

<h3 style="text-align: center;">Author's Note</h3>

<p>The question of who wrote this book is, like most questions about authorship, less simple than it appears...</p>
```

---

## 8. Work Skins (Custom CSS)

AO3 allows custom CSS through "Work Skins" -- stylesheets attached to your account that can be applied to individual works. This is the ONLY way to use CSS on AO3 (inline `<style>` tags are stripped).

### Creating a Work Skin

1. Go to your AO3 Dashboard
2. Click "Skins" in the sidebar
3. Click "Create Site Skin"
4. Set "Type" to "Work Skin"
5. Enter your CSS
6. When posting your work, select the Work Skin from the dropdown

### Suggested Work Skin for THE BOOK OF THE NEW TIDE

```css
/* Fuligin text effect */
.fuligin {
  color: #1a1a1a;
  text-shadow: 0 0 2px #000;
}

/* Severian's memory passages */
.memory {
  border-left: 2px solid #666;
  padding-left: 1em;
  margin-left: 0.5em;
  color: #444;
}

/* Chapter 12 review sections */
.review-heading {
  font-variant: small-caps;
  letter-spacing: 0.1em;
  margin-top: 2em;
}

/* Manga "panel" descriptions */
.panel {
  font-style: italic;
  padding: 0.5em 1em;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  margin: 1em 0;
}

/* Centered ornamental break */
.ornament {
  text-align: center;
  margin: 2em 0;
  letter-spacing: 0.5em;
  color: #999;
}

/* For the Author's Note section at the end */
.authors-note {
  border-top: 1px solid #ccc;
  margin-top: 3em;
  padding-top: 1em;
  font-size: 0.95em;
}
```

Usage in the text:

```html
<p>My cloak was <span class="fuligin">fuligin</span>.</p>

<div class="memory">
<p>"Join my crew," he said.</p>
</div>

<div class="panel">
<p>[Panel: A rubber arm stretches across a two-page spread. The sea is everywhere.]</p>
</div>

<p class="ornament">&loz; &loz; &loz;</p>
```

**Important caveats:**
- Work Skins can be disabled by readers who use their own site skins
- Colors and backgrounds may render differently in dark mode
- Keep styling subtle -- readers come for the text, not the CSS
- Test thoroughly with AO3's Preview function

**Recommendation:** A Work Skin is optional. The story works fine with standard HTML formatting. Only create one if you want the fuligin effect or the panel-description styling. Do not over-design.

---

## 9. Pre-Posting Checklist

Before posting each chapter, verify:

### Content

- [ ] Chapter text is proofread
- [ ] Chapter title is entered in the Chapter Title field (not in the work text)
- [ ] Paragraph breaks use `<p>` tags, not `<br>` sequences
- [ ] Scene breaks use `<hr />` consistently
- [ ] Emphasis (italic, bold) is applied correctly and not excessive
- [ ] Blockquotes are properly opened and closed
- [ ] No unclosed HTML tags (AO3 will attempt to fix these but may produce unexpected results)

### Formatting

- [ ] Preview the chapter in AO3 before posting
- [ ] Check that scene breaks render correctly
- [ ] Check that blockquotes are properly indented
- [ ] Check that any special characters display correctly (lozenges, em-dashes, etc.)
- [ ] If using a Work Skin, verify it is selected in the posting form

### Metadata (First Chapter Only)

- [ ] Fandom tags are correct: `The Book of the New Sun - Gene Wolfe, One Piece (Anime & Manga)`
- [ ] Rating is set to Mature
- [ ] Archive Warning is set to "Choose Not To Use Archive Warnings"
- [ ] Character tags are entered and auto-completing to canonical tags
- [ ] Additional tags are entered
- [ ] Summary is formatted and compelling
- [ ] Chapter count is set (1/17 or 17/17)
- [ ] Beginning notes are chapter-specific (not persistent across all chapters)

### Technical

- [ ] Post between 10:00-18:00 UTC to avoid the timestamp burial bug
- [ ] For staggered posting: update chapter count (e.g., 2/17, 3/17) with each new chapter
- [ ] For final chapter: ensure count reads 17/17 to mark the work as complete
- [ ] After posting, click "View" to verify the published version matches your intent

---

## Quick HTML Reference Card

For copy-paste convenience during posting:

```html
<!-- Paragraph -->
<p>Text here.</p>

<!-- Italic emphasis -->
<em>emphasized text</em>

<!-- Bold -->
<strong>strong text</strong>

<!-- Scene break (major) -->
<hr />

<!-- Scene break (minor) -->
<p style="text-align: center;">* * *</p>

<!-- Blockquote -->
<blockquote>
<p>Quoted text here.</p>
</blockquote>

<!-- Centered text -->
<p style="text-align: center;">Centered text</p>

<!-- Em dash (use the character, not hyphens) -->
&mdash;

<!-- Ellipsis -->
&hellip;

<!-- Section heading within chapter -->
<h3>Section Title</h3>

<!-- Link -->
<a href="https://example.com">Link text</a>

<!-- Horizontal rule with custom styling (via Work Skin) -->
<hr class="custom-break" />
```

---

## A Note on Wolfe's Typographic Practice

Gene Wolfe's published novels use minimal typographic apparatus. There are few italics (mostly for ship names and the occasional emphasis). No bold. No special fonts. Scene breaks are indicated by extra whitespace or a small ornament. Chapter titles are plain. The prose does the work.

Honor this. The temptation with AO3's HTML capabilities is to over-format. Resist it. Severian's voice does not need visual amplification -- it amplifies itself. A `<hr />` between scenes, `<em>` for the occasional foreign term, `<blockquote>` for quoted text. That is sufficient. The prose carries the weight. The formatting should be invisible.

The exception is Chapter 12, where the shift in mode (literary criticism within a first-person adventure narrative) may benefit from structural formatting (section headings, blockquotes for "quoted" manga passages). Even there, restraint serves the voice better than spectacle.

---

## Sources

- [AO3 Formatting Content with HTML FAQ](https://archiveofourown.org/faq/formatting-content-on-ao3-with-html?language_id=en)
- [AO3 HTML Help: How Do We Format Your HTML?](https://archiveofourown.org/help/html-help.html)
- [A Complete Guide to 'Limited HTML' on AO3 (CodenameCarrot)](https://archiveofourown.org/works/5191202)
- [The Fic Writer's Guide to Formatting (AnisaAnisa)](https://archiveofourown.org/works/40868577)
- [AO3 Tutorial: Posting a Work](https://archiveofourown.org/faq/tutorial-posting-a-work-on-ao3?language_id=en)
