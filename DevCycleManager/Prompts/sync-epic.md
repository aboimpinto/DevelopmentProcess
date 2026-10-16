# Sync Epic

Epic ID: {{epic_id}}
Epic folder: {{epic_path}}
Project repository: {{project_path}}

Direction: local → GitHub. Execute the shared Project GitHub Synchronization
policy. This command publishes the hierarchy, not a new refinement or implementation.

1. Read the local EpicDescription.md, feature breakdown, dependencies and every
   defined child's FeatureDescription.md across lifecycle folders. Reconcile
   counts/status against actual records. All intended features need real local
   FEAT IDs and descriptions before initial publication; do not invent children
   from placeholders or publish an incomplete breakdown as complete.
2. Resolve settings/account and validate all existing issue links. Build a
   concrete create/update/no-op map before writing. Prefer existing references;
   discover exact identities across open/closed issues to avoid duplicates.
   Existing closed issues remain closed, with a reported mismatch if local state
   contradicts them. Do not recreate them as open issues.
3. Create the epic issue only if absent, including identity and managed-section
   markers. Summarize problem, scope, acceptance, current local lifecycle status
   and dependencies. Save/read back its link immediately. Do the same for missing
   feature issues in dependency order, with Parent and dependency links.
4. Link feature issues to the epic using native sub-issues where supported and
   authorized. Preserve existing unrelated relationships; an already different
   parent is a conflict, not permission to reparent it. If native linking is
   unavailable, retain explicit Parent links plus an epic linked checklist and
   report the fallback. Never claim a native link succeeded without readback.
5. Update the epic managed section with one row per feature: ID, concise purpose,
   issue link, local state, verified delivery summary. Check completion only from
   accepted local completion evidence, and distinguish GitHub issue closure if
   different. Recompute distinct-feature totals, preserving completed siblings.
   Update each feature's managed summary/parent reference without erasing detailed
   phases/PR rows already published by sync-feature. When such rows exist, render
   them from the same current PRDelivery.md plan, or preserve them if no plan is
   available; never downgrade detailed planning to the initial issue scaffold.
   Recompute the epic PR forecast from distinct active feature/unit pairs, including
   published/merged units once and showing unopened remainder separately. Preserve
   unrelated sibling estimates; unknown remains unknown. Record revised estimates
   and explicit hard limits separately. Keep superseded units and replacement
   mappings in history, excluded from current totals; a revised count does not
   change a feature's readiness. Use the same totals as the local epic and feature
   delivery records, including when refinement remains BLOCKED.
6. Read back all changed bodies and hierarchy links. Record per-entity results
   and partial failures in GitHubSync.md beside the local epic, saving canonical
   links in each child's records too. Report created/updated/unchanged counts and
   remaining conflicts; issue creation does not change local lifecycle state.

Completion: hierarchy synchronized and verified, or accurately reported partial
SYNC_PENDING. No feature refinement, Git branch change or issue closure occurs.
