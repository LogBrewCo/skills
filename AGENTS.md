# LogBrew Skills Agent Guide

This public guide applies to the whole repository. Keep every file, branch
name, commit, pull request, check log, and release note suitable for permanent
public history.

## Ownership and Source of Truth

- This repository owns the agent skills in `skills/`, the plugin and
  marketplace manifests in `.claude-plugin/`, and their checks.
- The released `logbrew` CLI owns command names and flags. The hosted MCP
  server's operation catalog owns operation names and input fields. The SDK
  package READMEs own setup code. Copy from those sources; never invent a
  command, flag, operation, field, or package.
- Each skill folder must work alone when someone copies it. Keep its
  references inside the folder.

## Working and Verification

- Start with `git status --short --branch` and preserve unrelated work.
- Run `python3 scripts/check.py` before every commit. CI runs the same script
  with the released CLI help and the published operation catalog, plus
  `claude plugin validate`.
- A skill change that adds a command, operation, or step also updates
  `tests/evals.json`.

## Writing

- Write short, imperative steps. One instruction per sentence.
- Keep descriptions under 1,024 characters and name the phrases people use.
- Never claim behavior that the CLI, MCP server, SDKs, or public docs do not
  show.

## Public Boundary

Never add credentials, private paths or hosts, customer or account data,
internal architecture or operations, private plans, research, task state,
agent prompts, or non-public release evidence. Use synthetic IDs in examples.

Commits, pull-request titles and bodies, branch names, READMEs, and release
notes describe user-visible behavior only. Do not name hosting, network,
storage, or deployment internals, non-public repositories, local paths,
plans, agent sessions, costs, or real user data. Do not add AI attribution.

`scripts/public-guard.sh` enforces this. The required `Public guard` status
scans every new commit, commit message, changed path, branch name, and
pull-request title and body. Run `bash scripts/public-guard.sh install` once
per checkout to scan commit messages and pushes locally. Never use
`--no-verify`. If a finding is a false positive, change the rule in its own
pull request first; never split, encode, or reword text only to pass the
guard.
