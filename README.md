# LogBrew Skills

Agent skills that debug production errors, add error tracking to an app, and
check a release after a deploy. They use the
[Agent Skills](https://agentskills.io) format, so they work in Claude Code,
Codex, Cursor, GitHub Copilot, Gemini CLI, and other agents that read skills.

Each skill reads [LogBrew](https://logbrew.co) through the hosted MCP server
or the `logbrew` CLI. With no tool connected, each skill follows the same
steps with the stack traces, logs, and counts that you give it.

| Skill | What it does | Ask your agent |
| --- | --- | --- |
| [`debug-production`](plugins/logbrew/skills/debug-production/SKILL.md) | Finds the failing issue, reads its stack and first-seen release, pulls the logs and trace around the first event, checks who is affected, writes the fix, and checks that new events stop. | "Why did checkout break?" |
| [`instrument-app`](plugins/logbrew/skills/instrument-app/SKILL.md) | Detects the framework, installs the matching LogBrew SDK, sets service, environment, and release, sends a test event, and reads it back. Includes logging rules that help with any tool. | "Add error tracking to this app." |
| [`verify-release`](plugins/logbrew/skills/verify-release/SKILL.md) | Compares the issues, error logs, and trace error rate of a new release with the previous release, and decides go, rollback, or wait. | "Is the deploy safe?" |

## Install

Any agent that reads skills:

```bash
npx skills add LogBrewCo/skills
```

Claude Code, with the skills and the LogBrew MCP server in 1 plugin:

```text
/plugin install logbrew --marketplace LogBrewCo/skills
```

On Claude Code versions before 2.1.275, add the marketplace first:

```text
/plugin marketplace add LogBrewCo/skills
/plugin install logbrew@logbrew
```

Gemini CLI, with the skills and the LogBrew MCP server in 1 extension:

```bash
gemini extensions install https://github.com/LogBrewCo/skills
```

Then run `/mcp auth logbrew` in Gemini CLI to sign in.

Cursor and Kiro read the plugin in [`plugins/logbrew/`](plugins/logbrew). It
holds the skills and the LogBrew MCP server.

- **Cursor.** Copy `plugins/logbrew` to `~/.cursor/plugins/local/logbrew`,
  then run **Developer: Reload Window**.
- **Kiro.** Clone this repository. In the Powers panel, select
  **Add Custom Power**, then **Import power from a folder**, and choose
  `plugins/logbrew`.

Or copy a folder from [`plugins/logbrew/skills/`](plugins/logbrew/skills) into
the skills folder of your agent. Each folder works alone.

## Connect LogBrew

Use 1 of these:

- **MCP server.** The Claude Code plugin adds it. In other clients, add
  `https://mcp.logbrew.co/mcp` as a remote (HTTP) MCP server and sign in.
  The connection reads only the projects that you approve. See
  [Connect an AI agent with MCP](https://docs.logbrew.co/guides/mcp).
- **CLI.** Install it with `brew install LogBrewCo/tap/logbrew` or
  `npm install -g logbrew-cli@latest`, then run `logbrew login`. See
  [Install and use the LogBrew CLI](https://docs.logbrew.co/guides/cli).

Free plan: 50 GB of logs a month, no card.
[Create an account](https://logbrew.co).

## What is in each skill

```text
plugins/logbrew/skills/
  debug-production/
    SKILL.md
    references/cli.md              CLI commands for each step
    references/mcp.md              MCP operations for each step
    references/worked-example.md   A full investigation
  instrument-app/
    SKILL.md
    references/frameworks.md       Install commands and setup code per framework
    references/logging-rules.md    Logging rules for any tool
  verify-release/
    SKILL.md
    references/operations.md       CLI commands and MCP operations
```

## Checks

`python3 scripts/check.py` checks the skill format, the links, and the eval
cases in [`tests/evals.json`](tests/evals.json). It checks that the Claude
Code, Gemini CLI, Cursor, and Agent Plugins manifests agree on the name,
version, and MCP server. It also checks that every `logbrew` command matches
the help of the installed CLI, and that every MCP operation and input field is
in the published operation catalog. It makes no model calls. CI runs it
against the newest CLI release on every pull request, with the plugin
validators of Claude Code, Cursor, and Gemini CLI.

Each eval case is a prompt with the steps, commands, and operations that the
skill must give for it. To test a skill with a model, give the prompt to your
agent with the skill installed and compare its steps with the case.

## Privacy and support

The skills send nothing on their own. The MCP server reads only the projects
that you approve. Read the [LogBrew privacy policy](https://logbrew.co/privacy).
For help, email [support@logbrew.co](mailto:support@logbrew.co) or
[open an issue](https://github.com/LogBrewCo/skills/issues).

## License

[MIT](LICENSE)
