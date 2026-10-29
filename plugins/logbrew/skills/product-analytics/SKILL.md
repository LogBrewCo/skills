---
name: product-analytics
description: Answer product questions from real usage. Find where users come from, where they drop off, how many convert, which traffic source or campaign works best, and whether users come back. Use when someone asks about signups, conversion, funnels, drop-off, retention, returning users, traffic sources, UTM tags, referrers, or what users do on a page. Reads LogBrew product analytics through the logbrew CLI or MCP server and gives each answer with its breakdown, example sessions, change from the previous period, and sample size.
license: MIT
---

# Answer product questions

Give every answer in 6 parts: the answer, the breakdown, the sessions or
users behind it, the change from the previous period, the sample size and
how sure you are, and the next action. Use the analytics commands. Do not
count raw actions by hand.

## Choose the evidence source

1. **LogBrew CLI** with account access (`logbrew status --json`) or a
   project read key in `LOGBREW_TOKEN`.
2. **LogBrew MCP server** (`search` and `execute` tools from
   `https://mcp.logbrew.co/mcp`).
3. **No tool.** Ask the person for visits, signups, and returns per traffic
   source over the same period. Use the same steps.

Commands and operations for each step are in
[references/operations.md](references/operations.md).

## Steps

### 1. Find the project and the events

Read the overview and copy the exact event names. Page views are named by
their path, such as `/pricing`.

```bash
logbrew projects --json
logbrew analytics overview --project "$PROJECT_ID" --since 24h --json
```

Page views are trace spans, not actions, so `logbrew read actions` never
lists them. A missing page view in that list does not mean it was not
captured.

### 2. Find where users come from

The browser SDK tags every event of a visit with `tag.utm_source`,
`tag.utm_medium`, `tag.utm_campaign`, and `tag.referrer_domain`. It reads
them from the landing URL and the referrer. Do not recommend adding
attribution that is already captured. A visit with none of these tags is
direct.

```bash
logbrew analytics properties --project "$PROJECT_ID" --since 24h --json
```

Each value lists its sessions and up to 5 example sessions. Read
`tag.utm_source` for campaigns and `tag.referrer_domain` for links from
other sites.

### 3. Measure conversion and drop-off

Build the funnel from the first page to the goal. Split it by source.

```bash
logbrew analytics funnel --project "$PROJECT_ID" --since 24h --step page-view / --step page-view /signup --step interaction signup_completed --breakdown tag.utm_source --json
```

Run it again with `--breakdown tag.referrer_domain` for referred visits. The
largest drop is the `stopped` group with the most units. Session funnels
count visits, not people. A later visit by the same person is a new start,
so say so when people return.

### 4. Check whether users come back

```bash
logbrew analytics retention --project "$PROJECT_ID" --since 7d --start-kind interaction --start-event signup_completed --return-kind interaction --return-event signed_in --json
```

The `returned` and `not_returned` groups list example user IDs. A user whose
period has not ended is not counted as lost.

### 5. Read the sessions behind a number

Every number has up to 5 examples, each with action IDs and trace IDs. Read
one before you explain a drop.

```bash
logbrew read actions --session "$SESSION_ID" --project "$PROJECT_ID" --since 24h --json
logbrew read trace "$TRACE_ID" --project "$PROJECT_ID" --json
```

### 6. Report

```text
Answer: <one sentence with the number>
Breakdown: <value: units of base (rate)> for each source or step
Evidence: <2 or 3 example session or user IDs, with an action or trace ID>
Change: <now> vs <previous period> (<change>)
Sample: <sample_size> sessions or users; <high, medium, or low> confidence
Next: <one action, such as the source to fund or the step to fix>
```

Confidence is low under 30 units in a group: say that 1 more conversion
would move the rate a lot. A shared time range does not prove that one step
caused a drop. For a step that fails with errors, the debug-production
skill finds the cause.
