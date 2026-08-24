export const meta = {
  name: 'full-parallel-crons',
  description: 'Parallel run of all SkinTiers cron types: scout the work-list, then fan out Sonnet drafters -> Opus critics (fills), parallel image-search agents, and parallel video-harvest agents. Returns structured results; the main loop applies publish/commit serially.',
  phases: [
    { title: 'Scout', detail: 'gather pending fills, imageless products, creators' },
    { title: 'Fill', detail: 'one Sonnet drafter per queued item' },
    { title: 'Critic', detail: 'one Opus critic per drafted health-claim page' },
    { title: 'Images', detail: 'one agent per imageless product' },
    { title: 'Video', detail: 'one agent per YouTube creator' },
  ],
}

const REPO = '/Users/EricRies2/Projects/skincare'

// ---------- Phase 0: Scout ----------
phase('Scout')
const WORK_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['fills', 'images', 'creators'],
  properties: {
    fills: { type: 'array', maxItems: 16, items: { type: 'object', additionalProperties: false, required: ['type', 'name'], properties: { type: { type: 'string' }, name: { type: 'string' } } } },
    images: { type: 'array', maxItems: 10, items: { type: 'string' } },
    creators: { type: 'array', maxItems: 31, items: { type: 'object', additionalProperties: false, required: ['name', 'creator_slug', 'channel'], properties: { name: { type: 'string' }, creator_slug: { type: 'string' }, credential: { type: 'string' }, channel: { type: 'string' }, tier: { type: 'string' }, product_recs: { type: 'string' }, conflict: { type: 'string' } } } },
  },
}
const work = await agent(
  `You are the SCOUT for a parallel content run in ${REPO}. Gather the work-list. Run these and report results as structured data. DO NOT draft or change anything.
1. Pending fill items (next queued, NOT status:done) for each type. Read each data/queues/<type>s.yaml and list up to these caps of pending (status != 'done') names: product 12, ingredient 10, study 3, condition 1, goal 1, brand 1, person 2, list 1. Return them as fills[] = {type, name}. SKIP a type if its queue is empty. IMPORTANT: skip any name that looks garbled, non-existent, or a likely duplicate of an existing page (a fill agent will double-check, but do not pad).
2. Imageless products (up to 14): for f in data/products/*.md; do grep -q '^images:' "$f" || basename "$f" .md; done | head -14  -> images[] (slugs).
3. Creators: return an EMPTY array [] for creators (video harvest was just run; skip it this wave).
Return {fills, images, creators}.`,
  { schema: WORK_SCHEMA, label: 'scout', phase: 'Scout', model: 'sonnet', effort: 'low' }
)

if (!work) { log('Scout failed (subagent cap or error). Aborting.'); return { error: 'scout_failed' } }
log(`Scouted: ${work.fills.length} fills, ${work.images.length} imageless products, ${work.creators.length} creators.`)

// ---------- Shared rules snippet ----------
const RULES = `SkinTiers is a skeptical evidence-first skincare site (data-as-git markdown in data/{type}/{slug}.md). Work in ${REPO}. Follow docs/writing-guide.md + docs/anti-ai-ese.md. Fetch: try curl -sL -A "Mozilla/5.0" first; DailyMed (dailymed.nlm.nih.gov) is the durable-primary Drug Facts source for OTC products (search services/v2/spls.json?drug_name=...); PubMed via NCBI E-utilities (efetch/esearch) for studies; brand pages for cosmetics (cache non-primary sources: python scripts/source_cache.py put <url>). VERIFY every quote/stat/price/composition verbatim against the real source; when in doubt LEAVE IT OUT (never invent a price/%/claim). Link general ingredient evidence OUT in one clause to the ingredient page; do not re-explain what another page owns. Resolve identity before drafting (products get renamed/discontinued). Keep status:draft. Do NOT publish, do NOT resolve queues, do NOT commit.`

// ---------- Phase 1+2: Fill (Sonnet) -> Critic (Opus), pipelined ----------
const DRAFT_SCHEMA = { type: 'object', additionalProperties: false, required: ['type', 'slug', 'built'], properties: { type: { type: 'string' }, name: { type: 'string' }, slug: { type: 'string' }, built: { type: 'boolean' }, note: { type: 'string' }, identity_note: { type: 'string' } } }
const CRITIC_SCHEMA = { type: 'object', additionalProperties: false, required: ['slug', 'verdict'], properties: { slug: { type: 'string' }, verdict: { type: 'string', description: 'publish or revise' }, score: { type: 'number' }, note: { type: 'string' } } }

function draftPrompt(item) {
  return `${RULES}

Draft ONE ${item.type.toUpperCase()} page for the queued item: "${item.name}".
Scope by type: product/ingredient = full standard page (product-page standard / prose "## The Rubric"); INGREDIENT also set top-level tier: best/good/mid/weak matching your rubric. study = COMPACT structured (design/n/intervention vs comparator/primary result with numbers/effect size/generalizability/one limitation; link the ingredient story out). condition/goal = tight hub, PREFER a tier_list of graded items over essay. brand = LEAN <=180 words (what it is, founder in one line if verifiable, linked list of its on-site products/ingredients; attribute brand claims as the brand's own). person = LEAN <=150 words (who they are, an HONEST credential verified via NPI registry for a living person, linked products/videos; never state an unverified claim).
Steps: research (few sources), create data/${item.type}s/<slug>.md at status:draft with correct frontmatter + slug, then run: .venv/bin/python scripts/sk lint <slug>  and fix issues. If the item is off-topic, a duplicate of an existing page, or you cannot verify its identity, set built=false with a note (do NOT draft a bad page).
Return {type:"${item.type}", name:"${item.name}", slug, built, note, identity_note}.`
}
function criticPrompt(draft) {
  return `${RULES}

You are the OPUS CRITIC for the drafted ${draft.type} page data/${draft.type}s/${draft.slug}.md. Read it, then RE-VERIFY every load-bearing quote, statistic, price, and composition figure against the REAL source (re-fetch the cited URLs; check cited non-primary sources against the local cache first: python scripts/source_cache.py get <url>). Confirm: sources are primary/appropriate; no fabricated or mis-attributed claims; grades honest; general evidence linked out not re-told; (ingredient) tier matches the rubric. If anything is wrong, note it specifically. Run .venv/bin/python scripts/sk verify ${draft.slug} and sk style ${draft.slug}. Return {slug:"${draft.slug}", verdict:"publish" if clean else "revise", score (1-10), note (what you verified / what is wrong)}.`
}
const fillResults = await pipeline(
  work.fills,
  (item) => agent(draftPrompt(item), { schema: DRAFT_SCHEMA, label: `draft:${item.type}:${item.name.slice(0, 30)}`, phase: 'Fill', model: 'sonnet', effort: 'medium' }),
  (draft) => (draft && draft.built && ['product', 'ingredient', 'study', 'condition', 'goal'].includes(draft.type))
    ? agent(criticPrompt(draft), { schema: CRITIC_SCHEMA, label: `critic:${draft.slug}`, phase: 'Critic', model: 'opus', effort: 'high' }).then(v => ({ ...draft, critic: v })).catch(() => ({ ...draft, critic: null }))
    : draft
)

// ---------- Phase 3: Images (parallel) ----------
const IMG_SCHEMA = { type: 'object', additionalProperties: false, required: ['slug', 'added'], properties: { slug: { type: 'string' }, added: { type: 'boolean' }, file: { type: 'string' }, source: { type: 'string' }, source_url: { type: 'string' }, note: { type: 'string' } } }
function imgPrompt(slug) {
  return `${RULES}

Find and self-host a REAL product photo for data/products/${slug}.md, which lacks one. Read the page for its brand/retailer/DailyMed source URLs. Fetch a brand or major-retailer product page (og:image meta or the main product image), or a DailyMed image.cfm image; it MUST be a photo of THIS EXACT product (not a logo, banner, model shot, or unrelated image) - verify by checking the image looks like the product/label. Self-host: curl -sL "<url>" -o static/images/${slug}-<source>.jpg then confirm: file reports image data AND size > 3KB (else delete + skip). If good, ADD an images: block to the frontmatter after the category:/brand: line (file/source/source_url per data/products/cosrx-the-retinol-0-1-cream.md), then run .venv/bin/python scripts/sk lint ${slug}. If unsure or none found, added=false (never fabricate/mismatch an image). Return {slug:"${slug}", added, file, source, source_url, note}.`
}
const imgResults = await parallel(work.images.map(slug => () =>
  agent(imgPrompt(slug), { schema: IMG_SCHEMA, label: `img:${slug.slice(0, 34)}`, phase: 'Images', model: 'sonnet', effort: 'medium' }).catch(() => null)
))

// ---------- Phase 4: Video harvest (parallel, read-only proposals) ----------
const VID_SCHEMA = { type: 'object', additionalProperties: false, required: ['creator_slug', 'cards'], properties: { creator_slug: { type: 'string' }, note: { type: 'string' }, cards: { type: 'array', maxItems: 3, items: { type: 'object', additionalProperties: false, required: ['attach_slug', 'id', 'title', 'thesis', 'posted'], properties: { attach_slug: { type: 'string' }, id: { type: 'string' }, title: { type: 'string' }, thesis: { type: 'string' }, related: { type: 'string' }, posted: { type: 'string' } } } } } }
function vidPrompt(c) {
  return `Harvest eligible video cards from ONE creator for SkinTiers. Work in ${REPO}. READ-ONLY: do NOT write files, run sk add-video, or commit. Propose cards only.
CREATOR: ${c.name} (${c.creator_slug}); credential ${c.credential || '?'}; tier ${c.tier || '?'}; product_recs ${c.product_recs || 'none'}; CONFLICT: ${c.conflict || 'none'}; CHANNEL ${c.channel}
1. yt-dlp --flat-playlist --playlist-end 15 --no-warnings --print "%(id)s\\t%(title)s" "${c.channel}"
2. Choose UP TO 3 videos whose TITLE is a single-topic match to an EXISTING page (named product; ingredient/topic like retinoids/niacinamide/vitamin C/azelaic-salicylic-glycolic acid/sunscreen-SPF/ceramides/hyaluronic acid/peptides/coal tar/selenium sulfide/colloidal oatmeal; or condition/goal like rosacea/melasma/acne/seborrheic dermatitis/atopic dermatitis/hyperpigmentation/fungal acne/keratosis pilaris/stretch marks/psoriasis/anti-aging/dark circles). Skip vlogs/GRWM/hauls/roundups and #ad/sponsored titles. Product-rec/favorites videos are eligible ONLY if tier HIGH or product_recs ok; if the creator monetizes picks via an affiliate storefront (conflict mentions ShopMy/Amazon/affiliate/storefront), skip favorites/picks; if they have an own-brand line, skip videos mainly promoting it.
3. For each candidate: get transcript (.venv/bin/python scripts/yt_transcript.py <id>; none -> skip). MANDATORY sponsorship scan (grep -iE "sponsor|sponsored|#ad|paid partnership|gifted|use my code|affiliate|brought to you by|in partnership with") -> ANY present, REJECT. Confirm it is genuine education about the topic. attach_slug = the single most relevant EXISTING page (verify: test -f data/{ingredients,conditions,goals,products}/<slug>.md; none -> skip). Dedup: grep -rl "<id>" data/ | head ; if already carded, skip. Upload date: yt-dlp --skip-download --no-warnings --print "%(upload_date)s" "https://www.youtube.com/watch?v=<id>" -> YYYY-MM-DD. Thesis: 2-3 sentences, self-contained, name the topic + creator+credential on first mention, grounded ONLY in the transcript, no em/en-dashes, no overstated efficacy claim. related = comma-separated slugs of other existing pages it is about (best guesses ok).
Return {creator_slug:"${c.creator_slug}", cards:[{attach_slug,id,title,thesis,related,posted}], note}. Propose ONLY cards that passed transcript+sponsorship+page-exists+dedup.`
}
const vidResults = await parallel(work.creators.map(c => () =>
  agent(vidPrompt(c), { schema: VID_SCHEMA, label: `vid:${c.creator_slug}`, phase: 'Video', model: 'sonnet', effort: 'medium' }).catch(() => null)
))

// ---------- Aggregate ----------
const fills = fillResults.filter(Boolean)
const publishable = fills.filter(f => f.built && (f.critic ? f.critic.verdict === 'publish' : ['brand', 'person', 'list'].includes(f.type)))
const images = imgResults.filter(Boolean).filter(i => i.added)
const videoCards = vidResults.filter(Boolean).flatMap(r => (r.cards || []).map(c => ({ ...c, creator_slug: r.creator_slug })))
const seen = new Set(); const dedupCards = []
for (const c of videoCards) { if (c.id && !seen.has(c.id)) { seen.add(c.id); dedupCards.push(c) } }

log(`Done. ${fills.length} drafted (${publishable.length} publishable), ${images.length} images added, ${dedupCards.length} video cards proposed.`)
return {
  fills: fills.map(f => ({ type: f.type, name: f.name, slug: f.slug, built: f.built, note: f.note, identity_note: f.identity_note, critic: f.critic || null })),
  publishable: publishable.map(f => ({ type: f.type, slug: f.slug, score: f.critic?.score, critic_note: f.critic?.note })),
  images,
  video_cards: dedupCards,
}
