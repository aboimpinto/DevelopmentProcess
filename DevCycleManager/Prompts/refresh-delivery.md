# Refresh Delivery

Feature ID: {{feature_id}}
Feature folder: {{feature_path}}
Project repository: {{project_path}}

Direction: GitHub → local delivery records → existing feature issue table.
Execute the shared Project GitHub Synchronization policy. Read PRs without
modifying them; the only remote write is the existing feature issue managed
section through sync-feature. Do not change Git branches.

1. Read local PRDelivery.md, feature/epic delivery inventories and GitHubSync.md.
   Enumerate all mapped PRs, including earlier/superseded PRs. Validate repository
   and feature/unit association. If publication was interrupted before saving its
   link, discover candidates from explicit FEAT-ID / PRU-ID references and branch
   evidence; accept only an unambiguous match and record why. Never use a similar
   title alone. No mapped PRs means 'no delivery to refresh', not full delivery.
2. Read each PR's live URL/number, state, draft status, review/check status, head
   SHA, current base branch/SHA, merged flag, mergedAt and merge commit SHA when
   available. Paginate supporting inventories. Record observation time. A 404,
   missing permission, timeout or absent field is unknown, not closed or merged.
   Prepare observations separately; if required reads fail, retain the previous
   facts with an explicit stale/REFRESH_PENDING error rather than applying a
   partial snapshot as a fully refreshed feature.
3. Classify OPEN, CLOSED_UNMERGED or MERGED from GitHub facts. Preserve local
   implementation and acceptance states independently. A merged PR counts as
   final delivery only when it reached the configured integration target, or
   verified ancestry proves its changes reached that target later. A merge into
   an unmerged predecessor is MERGED with final delivery still pending; record
   its actual target. Do not treat the current base label, green checks, a closed
   issue or an open parent PR as proof of final delivery. Unavailable ancestry
   evidence leaves final delivery unverified, not inferred.
4. For each stack child, compare live predecessor head with its recorded old
   boundary. After parent amendments/merge/retarget/deletion flag any restack or
   retarget work and stale review/test evidence. Preserve the old boundary and
   original-to-merged revision mapping; do not overwrite the very SHA needed to
   restack. A rejected/closed-unmerged parent blocks dependent delivery unless a
   verified replacement exists. Report suggested next action; do not rebase,
   retarget, force-push, delete branches/worktrees or merge PRs here.
5. Re-read local input versions before applying observations; reconcile concurrent
   edits rather than overwriting a newer plan. Update hosting-fact fields in
   PRDelivery.md and the existing feature/epic delivery summaries consistently.
   Keep scope, grouping, forecasts, user notes and phase/task acceptance unchanged.
   Flag changed revisions as requiring fresh validation. Do not mark phases or
   features COMPLETED, move folders or check local acceptance automatically.
6. Save GitHubSync.md with timestamp, source URLs, exact observed revisions,
   transitions, final-target evidence, stale facts and required actions.
7. After successfully saving verified local observations, invoke sync-feature once
   for this feature and execute its recipe to update the existing issue table.
   Do this when facts changed OR a previous issue write is SYNC_PENDING, even if
   the next refresh observes no further PR transitions. Do not ask the user to run
   the second command or issue another authorization for this agreed operation.
   No linked issue means local refresh succeeded / SYNC_PENDING with a link-needed
   explanation; never create an issue. A failed remote write preserves the verified
   local facts and records the pending update; do not roll them back. On partial
   hosting-read failure, do not publish an incomplete new observation as complete.
   Read back the table, record local and issue outcomes separately, and report
   updated/no-op/unknown PR counts. Repeated unchanged refresh is a no-op on both
   sides once readback confirms the issue matches. sync-feature cannot call back
   into refresh-delivery; no recursion or background loop.

Completion: local delivery observations and the existing issue table reflect
verified GitHub facts, or REFRESH_PENDING / SYNC_PENDING identifies which step
remains incomplete. This is metadata
reconciliation, never a Git merge or independent feature-completion operation.
