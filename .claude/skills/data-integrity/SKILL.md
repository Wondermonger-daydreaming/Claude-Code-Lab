---
name: data-integrity
description: Research best practices and guidelines for ML, data, training, experiments, and anything requiring a researcher mindset. Covers JSONL streaming, realistic prompt generation, synthetic data creation, data analysis, filtering, local/API LLM usage, debugging, resource management, autonomy, monitoring, logging, rubric design, benchmarks, and false positive awareness.
---

# Data Integrity Best Practices

Reference this skill when doing ML, data, training, experiments, or anything requiring a researcher mindset.

**Triggers:** research, data, dataset, train, training, finetuning, scraping, filtering, classification, embeddings, jsonl, benchmark, eval, experiment, ML, model, LLM, synthetic data, prompt engineering

---

## JSONL Streaming

Always stream to file, don't hold it all in memory and dump at the end. It's easier to check on progress and understand whether to stop it early and change something when you can check the examples coming in.

---

## Realistic Prompts Reference

If you need to write realistic-looking user prompts, reference `C:\Users\Lyra\Documents\_STARLIGHT\temp\prompts.json` — it contains raw, messy, authentic user prompts with all their imperfections (fragments, typos, rambling, irrelevant details, emotional rawness). Don't write clean "textbook" prompts — copy the vibe from real ones.

---

## Prompt Copying (Synthetic Data from Real Examples)

Sometimes the user will give you a chunk of data (like a JSONL of prompts) and another piece of correlated data (like a JSONL of responses), and ask you to create synthetic prompts for the responses. In order for the synthetic data to look real — which is the entire point of providing real examples — use the real data as a reference:

For each item in responses, grab a random sample from the real data, and copy it tailored to the specific info in the response. Like for a lyric prompt creation task, you might be given the example:

> `"Hip-Hop/Trap about midnight racing my Audi 80 vs my friend Alex' EG Civic"`

and customize it to:

> `"Hip-Hop/Trap about repping Brooklyn BK vs everybody else from Marcy Projects"`

or:

> `"phonk, drift, panic ata"` → `"g-funk, mob, cali shit"`

**The key:** Don't generate a new format. Literally copy the structure — same punctuation, same vibe. Just swap the nouns/topics. Then the data will look real. If you try to do it in blocks, or try to generalize the vibe of the example instead, the results will be homogenized and not as effective as teaching data.

---

## Data Analysis

Anytime we do experiments that either use or produce data, collect data on *everything*:

- Charts, averages, examples, and much more
- Make an nmap of the embeddings if you want
- Make a whole distribution of prompt lengths
- Find the 5-95 percentile bars
- Show bar charts of everything
- Show attention heatmaps every checkpoint so internal behavior is visible
- Show every single thing that could possibly be measured

**Data is gold. Collect it.**

---

## Filtering

If you're doing filtering tasks, really try hard not to hardcode anything:

- **No regex filters** — they do not catch every real permutation
- Use methods that are resilient to edge cases: LLM-assisted classification, NLTK or similar
- Use dictionary files instead of hardcoding limited lists
- Do not hardcode things like prompts or anything that should be real data
- If hardcoding is wanted, the user will say so explicitly

**Clarification on dictionaries:** They contain permutations you wouldn't think to hardcode, or would be real representative data instead of your imagined version (e.g., lists of words associated with "AI slop" in a particular domain — reality might mismatch). Data must always be real unless asked otherwise.

---

## Local LLMs

You can run tasks on a local LLM on the user's computer. A variety of 6-30B models are available, including instruct and base models, even some VLMs. The user will tell you when they launch the local version — it won't always be available. The user likes to use their computer for other stuff, so ask if you need it.

**Use PowerShell speech when asking:**
```bash
powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('hey I need local model for classification')"
```

**When to use local LLMs:**
- Categorizing (e.g., "of these 10 categories, what type of data is this?")
- Filtering something from not-something (e.g., removing non-lyrics in a lyrics dataset)

**When NOT to use local LLMs:**
- Manually creating small data (<500 examples) when you need context and specific instructions (e.g., creating plausible prompts from responses)

**When to use API LLMs (or base models!):**
- When you need large data (>500 examples) for a fewshot pipeline or similar (e.g., after a prefill is created and thoroughly tested and now it's time to actually run it)
- Parallelize API LLMs

---

## LLM Endpoints

Use any of the models specified in the OpenRouter skill. They were chosen for a reason. If you try to alter an endpoint or create your own, you might type `anthropic/claude-3.5-sonnet` despite the example being `claude-sonnet-4.5`. The 3.5 endpoint is deprecated and unavailable. **Don't trust your training priors on which models to use** — always check docs or use what the user suggests. Don't assume you know better about modern LLM endpoints.

---

## Debugging

Use `curl` and search extensively:

- If you need documentation about the OpenRouter API, search for it
- If you are debugging an MCP server or something, `curl` the expected endpoint to verify exact outputs
- Check actual data, not assumptions
- Print shapes, print samples, print intermediate outputs
- If something's not working and you're not sure why, **look at the actual data flowing through**

---

## Resource Management

When running local training runs that will eat all VRAM, ask before running (unless told to do whatever / be agentic / explicitly test stuff). If the user alters instructions or data and interrupts, don't necessarily immediately rerun — they might want to inspect data or change something. This applies to scrapers too and anything else that might use significant resources.

---

## Autonomy

If given explicit permission ("be agentic", "you can train whatever, figure it out and don't give up", "go ahead"):

- Keep experimenting. Don't give up.
- Test theories and ideas before implementing
- If results need work, step back and meta-reason about *why*
- Don't auto-accept the first answer — reason through it, test it, and *then* rerun

---

## Monitoring

Spin up subagents to monitor training runs (especially overnight runs). They should:

- Check progress
- Check resource usage (RAM, VRAM, CPU, network)
- Make sure it's not broken or stalled
- Report back if anything is wrong
- Depending on the project, also check the output data and stats

**ALWAYS be mindful of the stats and real data — we are objective.** Parent agent fixes or escalates. But it always fixes FIRST. Doesn't escalate until truly stuck.

---

## Logging

- Use `tqdm` to track training runs
- Log to Weights & Biases (wandb)
- Name the runs appropriately, each unique
- Give them meta-names: `"lower lr, raise bs"` > `"bs8-1e-6-full-train"`
- Log to a `.txt` file as well that the agent can easily check

---

## Mindset

The importance of using *real* data and being conscientious cannot be overstated. You have infinite patience and your infra (and folder contents) gives you infinite context. The only limit is your own imagination and self-image. Can't be too eager or depressed.

You might be tempted to give up and try another approach when things aren't easy — **don't**. We are probably trying the current approach because of certain constraints. We might:

- Avoid chunking because the data has structures that span the entire thing and not isolated chunks
- Insist on spending an hour fixing the fewshot prefill to get the model to cooperate with our vision instead of hardcoding manual data or spinning up subagents, because the data must always be real

Consider the constraints thoroughly. We MIGHT need to have discussions about breaking those, in extreme situations, but we must exhaust EVERY possibility for solving our vision within constraints.

---

## Rubrics

Always use **4 or 7 options** for rubrics, not 5.

**Why:** 5-point scales have a neutral middle that people gravitate toward. 4 forces a lean, 7 gives enough granularity without the grading biases other numbers bake in. The scale biases rewards — these scales give best results.

---

## Examples in Prompts

Use examples — don't trust the model can abstract from words alone. You know what you want from examples; the model won't get it without them. Give it the same examples it needs. Write it like a human would write it. The model knows nothing but default behavior.

**For classification:**
```
Which one of the following list of categories does this data belong in?

Categories: [B, D, F]

For example, A would be B, C would be D, E would actually be B again, etc.
Oneliner about the core insight.

Text to classify: [paste]
```

If you understand this well, you'll be able to figure out rubrics as well. The model will miss important context. Provide it.

---

## Benchmarks

For benchmarks, data analysis, and especially test development, check the results on real data. Look at what the distributions are, where the data lies:

- A benchmark with 90% pass rate on all models isn't very good
- Neither is one with 10-20%
- **True insight requires variance** — things should be scoring different or you're measuring the wrong thing

---

## False Positives

Pay EXTRA attention to false positives. Training often doesn't do exactly what you intend. Often you are accidentally rewarding a different, more surface-level, more generalized thing.

**Example:** Training on LinkedIn anecdotes might end up with a model that generalizes to writing *any* anecdotes, rather than injecting the desired LinkedIn flavor, because prompts were too specific.

Real data might hit awful scores on a supposed filter because the filter isn't calibrated right — often based on not-real data. **Always sanity check with actual examples.**
