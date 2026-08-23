export const meta = {
  name: 'video-harvest',
  description: 'Parallel video harvest: one agent per roster creator proposes eligible non-sponsored, transcript-verified video cards for existing pages; returns proposals for the main loop to dedup and apply.',
  whenToUse: 'Bulk-integrate influencer/video content. Needs subagents (raise CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION). Pass args = array of creator objects from data/video-sources.yaml.',
  phases: [
    { title: 'Harvest', detail: 'one agent per creator: pick + transcript-verify + sponsorship-scan eligible videos' },
  ],
}

// args: array of creator objects, each: {name, creator_slug, credential, channel, tier, product_recs, conflict}
// (Built by the main loop from data/video-sources.yaml before invoking. YouTube channels only.)
const creators = (Array.isArray(args) ? args : []).filter(c => c && c.channel && String(c.channel).includes('youtube.com'))

if (!creators.length) {
  log('No creators passed in args. Pass the roster (YouTube channels) as args.')
  return { error: 'no creators in args', cards: [] }
}

log(`Harvesting ${creators.length} creators in parallel (concurrency-capped by the runtime).`)

const CARD_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['creator_slug', 'cards', 'note'],
  properties: {
    creator_slug: { type: 'string' },
    creator: { type: 'string' },
    credential: { type: 'string' },
    note: { type: 'string', description: 'one line: what was found or why none' },
    cards: {
      type: 'array',
      maxItems: 3,
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['attach_slug', 'id', 'title', 'thesis', 'posted'],
        properties: {
          attach_slug: { type: 'string', description: 'existing page slug to embed on (verified to exist)' },
          id: { type: 'string', description: 'YouTube video id' },
          title: { type: 'string' },
          thesis: { type: 'string', description: '2-3 sentences, self-contained, names subject + creator+credential, no em/en-dashes' },
          related: { type: 'string', description: 'comma-separated other existing-page slugs, or empty' },
          posted: { type: 'string', description: 'YYYY-MM-DD upload date' },
        },
      },
    },
  },
}

function harvestPrompt(c) {
  return `You are harvesting eligible video cards for SkinTiers (a skeptical skincare site) from ONE creator. Work in /Users/EricRies2/Projects/skincare. READ-ONLY: do NOT write files, do NOT run sk add-video, do NOT commit. Return proposals only.

CREATOR: ${c.name} (slug ${c.creator_slug})
CREDENTIAL: ${c.credential || 'see roster'}
CHANNEL: ${c.channel}
TIER: ${c.tier || '?'}   PRODUCT_RECS: ${c.product_recs || 'none'}
CONFLICT: ${c.conflict || 'none'}

STEP 1 - List recent uploads: yt-dlp --flat-playlist --playlist-end 15 --no-warnings --print "%(id)s\\t%(title)s" "${c.channel}"
STEP 2 - Choose UP TO 3 candidate videos whose TITLE is a single-topic match to an EXISTING site page: a named product, an ingredient/topic (retinoids, niacinamide, vitamin C, azelaic/salicylic/glycolic acid, sunscreen/SPF, ceramides, hyaluronic acid, peptides, coal tar, selenium sulfide, colloidal oatmeal), or a condition/goal the site covers (rosacea, melasma, acne, seborrheic dermatitis, atopic dermatitis, hyperpigmentation, fungal acne, keratosis pilaris, stretch marks, psoriasis, anti-aging).
   ELIGIBILITY: skip vague vlogs/GRWM/hauls/pure product-roundups and any #ad/sponsored title. PRODUCT-REC / FAVORITES videos are eligible ONLY if the creator is credibility-vetted: tier HIGH (derm/chemist) OR product_recs: ok. For a MED creator WITHOUT product_recs: education/how-to only. If the creator monetizes picks via an affiliate storefront (conflict mentions ShopMy/Amazon/affiliate/storefront), treat favorites/picks as effectively paid and skip them. If the creator has an own-brand line, skip videos mainly promoting their own products.
STEP 3 - For EACH candidate (stop at 3 that pass):
   a. Transcript: .venv/bin/python scripts/yt_transcript.py <id>  -> no transcript, skip.
   b. MANDATORY sponsorship scan of the transcript (grep -iE "sponsor|sponsored|#ad|paid partnership|gifted|use my code|use code|affiliate|brought to you by|thank you .* for sponsoring|in partnership with"). ANY present -> REJECT (do not propose it). Reject brand-channel uploads.
   c. It must be genuine education/how-to (or an eligible non-sponsored pick per above). Confirm the transcript actually is about the topic.
   d. attach_slug = the single most relevant EXISTING page. VERIFY it exists: test -f data/{ingredients,conditions,goals,products}/<slug>.md. If none exists, skip (do NOT invent pages).
   e. Dedup: check the id is not already carded: grep -rl "<id>" data/ | head. If already present, skip.
   f. Upload date: yt-dlp --skip-download --no-warnings --print "%(upload_date)s" "https://www.youtube.com/watch?v=<id>" -> reformat YYYY-MM-DD.
   g. Write a THESIS: 2-3 sentences, SELF-CONTAINED for a lay reader, grounded ONLY in the transcript (never fabricate a number/claim): name the product/ingredient/topic explicitly (never a bare "this"/"it"), introduce the creator with credential on first mention. NO em/en-dashes. No site self-reference.
   h. related = comma-separated slugs of EVERY OTHER existing page the video is genuinely about (best guesses fine; leave empty if none).

Return the structured object: creator_slug, creator, credential, and cards[] (0-3 passing cards), plus a one-line note ("added N: ..." or "none found: <why>"). Propose ONLY cards that passed the transcript + sponsorship + page-exists + dedup checks.`
}

const results = await parallel(
  creators.map(c => () =>
    agent(harvestPrompt(c), {
      label: `harvest:${c.creator_slug}`,
      phase: 'Harvest',
      schema: CARD_SCHEMA,
      effort: 'medium',
    }).catch(() => null)
  )
)

const good = results.filter(Boolean)
const allCards = good.flatMap(r => (r.cards || []).map(card => ({ ...card, creator: r.creator || '', creator_slug: r.creator_slug, credential: r.credential || '' })))

// Dedup across creators by video id (in case two agents propose the same id)
const seen = new Set()
const deduped = []
for (const card of allCards) {
  if (!card.id || seen.has(card.id)) continue
  seen.add(card.id)
  deduped.push(card)
}

log(`Harvest complete: ${good.length}/${creators.length} creators reported, ${deduped.length} unique candidate cards proposed.`)

return {
  creators_reported: good.length,
  creators_total: creators.length,
  card_count: deduped.length,
  cards: deduped,
  notes: good.map(r => ({ creator_slug: r.creator_slug, note: r.note })),
}
