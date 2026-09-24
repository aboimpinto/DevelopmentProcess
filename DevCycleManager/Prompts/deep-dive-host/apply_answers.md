## Apply saved answers

Return only the versioned deep-dive.edits JSON exchange, without fences or commentary.
Use the current target snapshot, authoritative preparation context and saved answers;
do not conduct a new interview. Preserve useful sections, links, tables, diagrams,
and valid design-derived decisions. Apply only answered decisions. Chat may
explain an answer but cannot override it or independently add requirements.

Resolve validation markers using the saved decisions. Remove a resolved marker
entirely; do not reintroduce its literal token in explanatory status prose. Leave
unresolved decisions visible rather than claiming readiness. Express decisions
with implementable boundaries and acceptance behavior. Preserve explicit
delegation rules, and do not add future human approval or manual phase gates.
Return scoped exact edits: `before` is a nonempty verbatim excerpt that occurs
exactly once in the supplied target; `after` is its replacement. Include enough
surrounding text for a unique match. Edits must not overlap. All before excerpts
refer to the same original snapshot, not earlier edits in this response. An empty
edits list is valid when the saved decisions are already represented. Never
replace the whole document; retain untouched content. Do not return a shortened
document or a summary in place of edits. The host validates and applies the edits,
and rejects them if the source changed while this turn was running.

Do not modify design/context documents; this response affects the primary target only.
