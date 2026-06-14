# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

My domain will cover what the best and afforadable options to eat within and outisde SFSU. This knowledge is valuable because people love to have options to point to when they are hungry and as a college student its always a good idea to try to save money when youre hungry. Its hard to find information like this through official channels because theres an innaccesibility when it comes to information about food places especially affordable options around or outside of campus. Ive come across many resources that are very dated and was writted way back towards 2012. Also there arent yelp pages for all dining options around sfsu and if there is information about the place is very vague. Sometimes yelp reviews are also vague and might not reflect an accurate depiction of the dining place within or outside of sfsu. Information is also repetetive, information accross resources can hold the same descriptions for the same restaurants.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

|| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Best Food on Campus or off (sfsu reddit) | forums | https://www.reddit.com/r/SFSU/
comments/1fe4on9/best_food_on_campus_or_off/ |

| 2 | hall of flame burger reviews (yelp) | reviews | https://www.yelp.com/biz/hall-of-flame-burgers-san-francisco?osq=Restaurants+Near+Sfsu&sort_by=elites_desc |

| 3 | cafe roso reviews (yelp) | reviews | https://www.yelp.com/biz/cafe-rosso-san-francisco?sort_by=elites_desc |

| 4 | blog post of top 5 places to eat off campus (goldengateexpress) | blog post | https://goldengatexpress.org/113255/opinion/opinion-top-five-off-campus-eateries-around-sfsu/ |

| 5 | halal shop yelp reviews (yelp) | reviews | https://www.yelp.com/biz/halal-shop-san-francisco-2?osq=Restaurants+Near+Sfsu&sort_by=elites_desc |

| 6 | natural selections yelp reviews (yelp) | reviews | https://www.yelp.com/biz/natural-sensations-san-francisco?sort_by=elites_desc |

| 7 | blog post about monarca a food dining hall (goldengateexpress) | blog post | https://goldengatexpress.org/107839/opinion gator-take-monarca-dining-hall-formerly-city-eats-is-not-bad/ |

| 8 | blog post about top places to eat around sfsu form society 19 (society19) | article | https://www.society19.com/guide-eating-sfsu-campus/ |

| 9 | article about campus restaurant run by sudents | food | https://www.smpltxt.net/2024/12/18/beyond-routine-san-francisco-states-elevated-dining/ |

| 10 | an article about top places to eat around sf as an sfsu student (xpressmagazine) | article | https://xpressmagazine.org/5585/fall-2013/the-best-of-san-francisco-sf-state-edition/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
