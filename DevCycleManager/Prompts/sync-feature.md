# Sync Feature

Feature ID: {{feature_id}}
Feature folder: {{feature_path}}
Project repository: {{project_path}}

Direction: local → GitHub. Execute the shared Project GitHub Synchronization
policy. Update the existing feature issue; never create an issue in this command.

1. Read FeatureDescription.md, FeatureTasks.md, phase documents, PRDelivery.md,
   the parent epic and previous GitHubSync.md receipt. Resolve the existing issue
   link and verify it in the configured repository. If absent, report that
   sync-epic (for an epic feature) or explicit issue linking is needed. Do not
   silently create one or pick an issue by approximate title.
2. Check that local phase/tasks, unit membership, dependencies and forecast agree.
   Refinement owns this plan: missing or contradictory planning inputs are a
   planning gap, not permission for this sync to invent PR groups. For an older
   unrefined feature, synchronize only the available summary and explicitly say
   'not yet refined; PR forecast unavailable', never a fabricated zero count.
3. Render the managed section with concise context, local feature state, parent
   link and a phase table. Include each phase's state, predicted PR count, and
   planned units with stable feature/unit IDs, proposed PR title, short description,
   member tasks, dependencies and grouping rationale. Evidence-only phases show
   zero with the reason; grouping follows work properties, never phase labels.
   Explain that counts are a forecast and record the date/rationale of revisions.
4. Render each unit exactly once with its current actual PR link(s) when mapped;
   replace the planned display entry rather than adding a duplicate delivery row.
   Preserve the unit ID and original intent. Keep superseded/closed-unmerged PRs
   in history, all associated PR links, and their disposition. Proposed titles
   are not real PRs. A unit spanning phases has one owner/counting phase and
   cross-references from other phases so totals do not double count.
5. Show known implementation, review, merge and final-delivery states separately,
   with observation timestamps and available base/head/merge evidence. Never
   change a stale local PR_OPEN to MERGED merely because local tasks are done.
   Report unknown/stale hosting state and recommend refresh-delivery; sync-feature
   itself does not mutate the local plan from GitHub or run another sync command.
6. Preserve manual content and other issue attributes, write only a changed
   managed section, verify readback, and record the receipt beside the feature.
   Describe validation as planned versus actually run. Do not promote lifecycle
   status, close the issue, or start implementation when publishing a plan.

## Issue delivery table

Use an actual Markdown table in the feature issue's managed section, not just
a prose forecast. Populate it from PRDelivery.md:

| Phase | Unit / tasks | Proposed PR title and short description | Depends on | Actual PR | Delivery status |
| --- | --- | --- | --- | --- | --- |
| Owning phase | Stable feature/unit ID and task IDs | Planned improvement and purpose | Unit IDs or none | Not opened | Planned |

As soon as a PR is created, save its identity locally and update the same row's
Actual PR cell with the clickable number/URL and its observed Open/Draft status.
Do not wait for merge, review completion or the end of the phase/feature. Retain
the planned title/description and unit identity; replace the 'Not opened' placeholder,
not the whole plan. A later refresh updates status and merge evidence in that row.
Show CLOSED_UNMERGED distinctly; multiple attempts stay linked with dispositions.
Include the per-phase count summary and distinct feature total alongside this table.

Completion: existing feature issue matches the available local plan and mapped
PRs, with unknowns explicit, or SYNC_PENDING with a concrete reason.
