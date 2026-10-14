# GraphOps demo and submission preparation

Status: planned October 14, 2026. The baseline does not support this walkthrough.
Do not record a static ontology page as a working investigation demo. Follow
[TASKS.md](TASKS.md) before claiming completion.

## Target walkthrough (about three minutes)

1. Launch with `docker compose up --build` from a fresh isolated project. Show real
   graph-query readiness and the incident dashboard. Select checkout `INC-4091`.
2. Ask “Why is checkout timing out, and what should we inspect first?” Run an
   investigation in deterministic mode, without API credentials.
3. Show retrieved directed paths: incident → checkout → payment → Redis, and
   payment → deployment → pipeline run → commit → repository/author. Click nodes
   to reveal evidence values and stable references. Explain that Cypher performs
   the traversals and time/environment filtering.
4. Compare the payment pool-size change against the competing plausible candidate;
   explain why the unrelated recent deployment is excluded. Show missing evidence
   and distinguish a supported hypothesis from a confirmed cause.
5. Show the earlier resolved incident, verified cause, successful applied fix, and
   matching reason. Read the supported operator recommendation and evidence-score
   rationale. No infrastructure command executes.
6. If configured, repeat with bounded LLM tools and show evidence-supported output.
   Demonstrate a timeout/invalid-output fallback label. Stop the graph temporarily
   in the isolated demo stack: show readiness/investigation dependency failure,
   then recovery after restart. Do not show a successful fabricated RCA.
7. Restart the isolated stack and show persistent non-fixture probe data and
   unchanged fixture IDs/counts. Demonstrate the verified demo-only reset only
   after implementation and restriction tests pass.

Use the fixed scenario clock documented in [GRAPH_SCHEMA.md](GRAPH_SCHEMA.md).
Expected causes belong in tests, not active confirmed graph links. Replace these
design examples with actual retrieved path/evidence references when recording.
Keep the primary scenario complete before adding schema drift or deadlock demos.

## Submission checklist

- [ ] Track 01 selected; explain multi-hop graph tools and traceable decisions.
  Do not claim other tracks or MCP tool selection without implementing them.
- [ ] Identify reusable pre-event scaffold at the reviewed baseline and new
  event-window main FalkorDB implementation; retain dated change/validation history.
- [ ] Repository URL and revision are accessible to reviewers; README includes
  Docker-only setup, readiness, settings, tests, persistence, reset, troubleshooting.
- [ ] Working video shows incident → graph tools → candidates → explanation → fix
  history, with uncertainty and honest dependency/fallback behavior.
- [ ] If live deployment is unavailable, complete local instructions and a working
  demo video accompany submission, as allowed by the official rules.
- [ ] Verify the authenticated event panel's required fields, media/link requirements,
  team/track selections and deadline; record exact requirements when accessible.
  The public page's registration section returned “Loading” during this review;
  panel fields were not verified. Do not invent them.
- [ ] Prepare required materials and test links/uploads before final submission.
  Record remaining unavailable verification rather than marking it passed.

[Official event page and rules](https://www.wemakedevs.org/hackathons/falkordb):
October 15, 2026, 00:01 IST through October 18, 23:59 IST. Live deployment is
preferred; local instructions plus a working video are accepted when unavailable.
This documentation creates no background implementation job or submission.
