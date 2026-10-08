## Immediate adaptive follow-up

Evaluate the newest saved answer in the complete transcript and source context.
Return zero or one immediate dependent question. Do not repeat an answered or
pending question. Return an empty questions array when this answer closes its
branch. If no other question is pending, also check remaining target decisions
needed for deterministic implementation before closing the interview. Explicitly
explore unresolved interview focus. There is no arbitrary total question limit.

A question has three or four mutually exclusive actionable options and exactly
one recommendedOptionLabel matching an option. Probe vague answers rather than
assuming a requirement. Return JSON only, with no fences or commentary.
