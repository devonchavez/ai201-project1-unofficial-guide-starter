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

 # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Best Food on Campus or off (sfsu reddit) | forums | https://www.reddit.com/r/SFSU/comments/1fe4on9/best_food_on_campus_or_off/ |
| 2 | hall of flame burger reviews (yelp) | reviews | https://www.yelp.com/biz/hall-of-flame-burgers-san-francisco?osq=Restaurants+Near+Sfsu&sort_by=elites_desc |
| 3 | cafe roso reviews (yelp) | reviews | https://www.yelp.com/biz/cafe-rosso-san-francisco?sort_by=elites_desc |
| 4 | blog post of top 5 places to eat off campus (goldengateexpress) | blog post | https://goldengatexpress.org/113255/opinion/opinion-top-five-off-campus-eateries-around-sfsu/ |
| 5 | halal shop yelp reviews (yelp) | reviews | https://www.yelp.com/biz/halal-shop-san-francisco-2?osq=Restaurants+Near+Sfsu&sort_by=elites_desc |
| 6 | natural selections yelp reviews (yelp) | reviews | https://www.yelp.com/biz/natural-sensations-san-francisco?sort_by=elites_desc |
| 7 | blog post about monarca a food dining hall (goldengateexpress) | blog post | https://goldengatexpress.org/107839/opinion/gator-take-monarca-dining-hall-formerly-city-eats-is-not-bad/ |
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
350–500 characters (target ~450), with the split preferring a sentence boundary (. ! ?) or newline inside that window so a chunk never ends mid-word.

**Overlap:**
50–70 characters (target ~60). Each new chunk backs up ~60 characters from the previous boundary and snaps forward to the next word boundary, so context that lands on a seam isn't lost.

**Preprocessing before chunking:**
HTML was stripped to plain text with a standard-library `html.parser` extractor that captured text only inside each page's article/comment container, dropping site navigation, related-story rails, and footers. The Reddit thread had its subreddit sidebar/FAQ boilerplate removed. The four Yelp pages block automated downloading (HTTP 403 even with a browser user-agent), so their review text was collected manually and cleaned of copy-paste markdown (`*`, `**`) and wrapped line breaks. A 3-line `Source / URL / Type` header on each document is parsed into per-chunk metadata for source attribution rather than embedded in the chunk text. A QA pass (grep for HTML entities, leftover tags, and nav/boilerplate words across all 10 docs) returned zero hits.

**Why these choices fit your documents:**
The corpus is mostly short reviews and forum comments, not long-form guides. A ~450-character chunk is large enough to hold one complete thought (a single review, a menu description, a couple of related comments) but small enough that a specific query — e.g. "popular item at the Halal shop" — matches a precise chunk instead of a diluted multi-topic blob. The small overlap stitches sentences that fall on a boundary back together. The one known weakness is the Reddit thread: forum replies are short and disconnected, so packing them to ~500 characters can glue unrelated one-line comments into the same chunk, which lowers their standalone meaning.

**Final chunk count:**
137 chunks across 10 documents (avg 431 characters; 129/137 fall inside the 350–500 window, the remainder being the shorter last chunk of each document). This sits comfortably within the 50–2,000 guideline — chunks are neither too coarse to match specific queries nor too fine to carry meaning.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
`all-MiniLM-L6-v2`, run locally through `sentence-transformers` (no API key, 384-dimensional vectors). Embeddings are L2-normalized at both index time and query time, and the vectors are stored in a persistent ChromaDB collection configured for cosine distance (`hnsw:space: cosine`). I chose it because it's small, fast on CPU, and free to run locally — a good fit for a 137-chunk corpus of short reviews and forum comments where I don't need a huge context window per chunk. Its 256-token input limit is well above my ~450-character chunk size, so no chunk gets truncated, and its general-purpose semantic quality is strong enough to match casual food queries to relevant review text.

**Production tradeoff reflection:**
If I were deploying this for real users and cost wasn't a constraint, I'd weigh moving to a larger, higher-accuracy embedding model — for example an API-hosted model like OpenAI's `text-embedding-3-large` or a bigger open model such as `bge-large` / `e5-large`. The main tradeoffs:
- **Accuracy on domain-specific text:** larger models capture more nuance, which would help with the vague, slangy language in Yelp/Reddit posts where MiniLM sometimes misses the intent (e.g. my Q2 and Q3 test questions, where retrieval came back off-target). This is the tradeoff I'd prioritize most.
- **Context length:** a model with a longer input limit would let me use bigger chunks without truncation, so a single review or comment thread could stay intact instead of being split.
- **Multilingual support:** SFSU has a large international student population, so a multilingual model would handle non-English reviews and queries that MiniLM (English-focused) handles poorly.
- **Latency and local vs. API-hosted:** the current model runs locally in milliseconds with no network call or per-query cost. An API-hosted model adds latency, a rate limit, and an ongoing bill, and creates a dependency on a third party being up. For a student project the local model wins; for a real product I'd accept that cost for the accuracy gain, but I'd cache embeddings to keep repeat queries fast.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
Grounding is enforced at three layers, not just requested in prose:

1. **Structural** — the model never sees the full corpus. It only receives the retrieved chunks, formatted as a numbered list (`[1] Source… / URL… / text`). Before generation, any chunk scoring below a cosine-similarity floor of `0.15` is filtered out, so barely-related chunks are never offered as "context" the model could lean on. For an off-topic question this can leave nothing to answer from, which is by design.

2. **Instructional** — the system prompt gives the model strict rules. The actual instruction is:
   > "Answer the question using ONLY the information in the provided documents (the CONTEXT). Never use outside or prior knowledge, and never guess. If the documents don't contain enough information to answer, set `answer` to an empty string and `cited_sources` to an empty list… Otherwise, write a concise, specific answer and list the EXACT source numbers you used in `cited_sources`. Only include a number if that source genuinely supports your answer. In the answer text, mark each claim with its source number in square brackets, e.g. `[3]`."

   The model must reply with a JSON object `{"answer": ..., "cited_sources": [...]}` and nothing else (enforced with Groq's `response_format=json_object`), and it runs at `temperature=0.2` to favor faithful over creative answers.

3. **Programmatic** — after generation, every cited source number is validated against the real retrieved set (`1..k`), de-duplicated, and kept in citation order. If the model returns an empty answer **or** cites no valid source, the system discards the answer entirely and shows a fixed fallback: *"I don't have enough information on that."* So an uncited or unsupported answer is never displayed — this is enforcement, not a suggestion. This is exactly what happened on test questions 2 and 3.

(Honest caveat, also noted in the code: an LLM can't give true per-sentence proof that a claim came from the context. What's guaranteed is that every *displayed* source was actually retrieved and explicitly claimed by the model, that invalid citations are dropped, and that an uncited answer is never shown.)

**How source attribution is surfaced in the response:**
The answer text marks each claim inline with a bracketed number (`[1]`, `[4]`), and the response then renders a **Sources** section listing only the validated, model-cited sources. Each entry shows the source name, its type (review / blog post / article / forum), its relevance score, and its URL — e.g. `[4] halal shop yelp reviews (reviews) · relevance 0.62 · <url>`. Because that list is built from the retrieval + validation step rather than from free text the model wrote, the user can trace every `[n]` in the answer back to a real document, and a source can never appear unless it was both retrieved and cited.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does the Vista Room have a set or rotating menu? | The Vista Room at SFSU has a wide variety of food options and a rotating menu that changes every couple of months. | The Vista Room has a rotating menu, with a three-course menu that changes three times a semester [1], and also offers a soup and pasta of the day, along with weekly specials | Relevant | Accurate |
| 2 | What is the dining hall called that students are usually acquainted with their first year at SFSU? | Yerba Buena Dining Hall and Monarca (formerly City Eats). | I don't have enough information on that. | Off-target | Inaccurate |
| 3 | What neighborhoods is SFSU near to? | Ocean Ave and Lake Merced (near the Sunset). | I don't have enough information on that. | Off-target | Inaccurate |
| 4 | What's a popular food item at the Halal shop at SFSU? | Chicken Tikka Masala over Rice. | Falafels [1], tikka chicken over rice [4], and the plate with rice, salad, and creamy white sauce with spicy red drizzle | Relevant | Accurate |
| 5 | Where is the Vista Room at SFSU located? | Rm. 401, Burk Hall. | The Vista Room is located in Rm. 401 at SFSU | Relevant | Partially accurate |

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
What neighborhoods is SFSU near to?
**What the system returned:**
I don't have enough information on that.
**Root cause (tied to a specific pipeline stage):**
I think the rootcause to this answer inaccuracy is the lack of information provided about dining experiences in SFSU. When conducting research about the dining places within SFSU there was a lack of student opinion about the type of food to eat on campus more so WHERE to go eat. With information like where to find food outside of campus this was a challenge aswell where although the name of the restaurants was really good, being able to locate these stores and associate them with a section within SF was a struggle especialy if you wanted to know how accesible some places within SF but outside of SFSU were.
**What you would change to fix it:**
I wouldve tried to find better sources or instead of relying on documents that coevered specifically "places outside of SFSU" for information it be better to use more general city food guides.
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Planning helped during implementation because I was able to find proper documents to ensure that my LLM would be able to create acurate outputs.
**One way your implementation diverged from the spec, and why:**
I think i fufilled the planning document pretty well where I didnt had to experienve implementation divergement.
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

- Whenever I needed a core feature fleshed out Id tell claude to use the context of the planning document to help make an accurate implementation of what I needed. Whether this was the chunking syste, embedded text system, and etc. I used claude to generate the core structure of the code and made minor edits if I saw my project diverging from the project outline.
- Claude was able to create a good ammount of the code. If there wer areas where I needed to make edits it was usually because I wasnt specific enough to have certain features follow the project guidelines. Claude would even work ahead of the project guidelines and have most of a milestone complete off of the prompts I would load it with.
- I remember specifically that the LLM was using general knowledge to help answer some of the questions that shouldve come back as the machine not having enough information to make an accurate answer with or not using the resource documents I proided. So i had to fix the system prompt to make sure the LLM was grounded in the documents I provided and not using any outside infomration.

**Instance 2**

- I used Claude to help explain certain topics to me that I didnt know in the beginning. Before the project I struggled with the ideas of sourcing chunks from my resources and what embedding them was.
- Claude helped dumbdown these concepts and explained what creating chunks were and how to embed them thoughroughly
- I didnt need to change much or override anything since the way I used AI in this instance wasnt to contribute manually to the project more so being able to do research about what the project was having me do.
