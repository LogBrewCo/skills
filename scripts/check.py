#!/usr/bin/env python3
"""Check the skills, manifests, links, and evals in this repository.

The checks are deterministic and make no model calls:

- Skill frontmatter follows the Agent Skills format.
- Plugin and marketplace manifests parse and point at existing paths.
- The Gemini CLI, Cursor, and Agent Plugins manifests match the Claude Code
  plugin in name, version, description, and MCP server URL.
- Every relative Markdown link resolves.
- Every `logbrew` command in a skill parses against the help of the
  installed CLI (set LOGBREW_BIN to use another binary).
- Every MCP operation and listed input field exists in the published
  operation catalog (set MCP_CATALOG to a local file to skip the download).
- Every eval case in tests/evals.json finds its steps in order, its commands,
  and its operations in the skill.

Exit status: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "logbrew"
SKILLS = PLUGIN / "skills"
CATALOG_URL = "https://raw.githubusercontent.com/LogBrewCo/mcp/main/catalog/operations.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
OPERATION_RE = re.compile(r"`([a-z]+(?:\.[a-z]+)+\.v[0-9]+)`")
FIELDS_AFTER_OPERATION_RE = re.compile(
    r"`([a-z]+(?:\.[a-z]+)+\.v[0-9]+)`(?:\s*\|\s*|:\s*)((?:`[a-z_]+`(?:,\s*)?)+)"
)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SHELL_STOP = {"|", "||", "&&", ";", ">", ">>", "<", ")", "&", "2>"}

SEEDED_BAD_COMMANDS = (
    "logbrew read issues --not-a-flag 1 --json",
    "logbrew read incidents --json",
    "logbrew explain release --project p --json",
    "logbrew deploy d --project p --release r --rollback --json",
)
SEEDED_BAD_OPERATION = "`issues.list.v999` and `logs.list.v1`: `project_id`, `not_a_field`"

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# Skill frontmatter


def read_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{rel(path)}: missing frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{rel(path)}: frontmatter is not closed")
        return {}, text
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            fail(f"{rel(path)}: frontmatter line has no key: {line}")
            continue
        fields[key.strip()] = value.strip()
    return fields, text[end + 5 :]


def check_skill(skill_dir: Path) -> dict[str, str]:
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        fail(f"{rel(skill_dir)}: missing SKILL.md")
        return {}
    fields, body = read_frontmatter(path)
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        fail(f"{rel(path)}: name must be 1-64 lowercase letters, digits, and single hyphens")
    if name != skill_dir.name:
        fail(f"{rel(path)}: name {name!r} must match the folder name {skill_dir.name!r}")
    if not 1 <= len(description) <= 1024:
        fail(f"{rel(path)}: description must have 1-1024 characters, has {len(description)}")
    if "<" in description or ">" in description:
        fail(f"{rel(path)}: description must not contain angle brackets")
    for key in fields.keys() - ALLOWED_KEYS:
        fail(f"{rel(path)}: unknown frontmatter key {key!r}")
    if len(body.splitlines()) > 500:
        fail(f"{rel(path)}: keep SKILL.md under 500 lines; move detail to references")
    return fields


# Manifests


def check_manifests() -> None:
    plugin_path = PLUGIN / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        market = json.loads(market_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"manifest does not parse: {error}")
        return
    entries = market.get("plugins", [])
    if not any(entry.get("name") == plugin.get("name") for entry in entries):
        fail("marketplace.json must list the plugin under the name in plugin.json")
    for entry in entries:
        source = entry.get("source")
        if not isinstance(source, str) or ".." in source or not (ROOT / source).is_dir():
            fail(f"marketplace.json: plugin {entry.get('name')!r} source must be an existing folder")
    for name, server in plugin.get("mcpServers", {}).items():
        if not str(server.get("url", "")).startswith("https://"):
            fail(f"plugin.json: MCP server {name!r} must use an https URL")
    check_other_manifests(plugin)


AGENT_PLUGINS = "https://agent-plugins.org/schemas/1.0.0/"
AGENT_PLUGIN_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{rel(path)} does not parse: {error}")
        return {}


def check_other_manifests(plugin: dict) -> None:
    """Keep the Gemini CLI, Cursor, and Agent Plugins manifests in step with
    the Claude Code plugin: same name, version, and MCP server URL."""
    url = plugin.get("mcpServers", {}).get("logbrew", {}).get("url")
    gemini = load_json(ROOT / "gemini-extension.json")
    cursor_market = load_json(ROOT / ".cursor-plugin" / "marketplace.json")
    cursor = load_json(PLUGIN / ".cursor-plugin" / "plugin.json")
    agent = load_json(PLUGIN / "plugin.json")
    agent_mcp = load_json(PLUGIN / "mcp.json")
    servers = {
        "gemini-extension.json": gemini.get("mcpServers", {}).get("logbrew", {}).get("httpUrl"),
        "plugins/logbrew/.cursor-plugin/plugin.json": cursor.get("mcpServers", {}).get("logbrew", {}).get("url"),
        "plugins/logbrew/mcp.json": agent_mcp.get("mcpServers", {}).get("logbrew", {}).get("url"),
    }
    for path, value in servers.items():
        if value != url:
            fail(f"{path}: the logbrew MCP server URL must be {url}")
    for path, manifest in {
        "gemini-extension.json": gemini,
        "plugins/logbrew/.cursor-plugin/plugin.json": cursor,
        "plugins/logbrew/plugin.json": agent,
    }.items():
        for key in ("name", "version", "description"):
            if manifest.get(key) != plugin.get(key):
                fail(f"{path}: {key} must match plugins/logbrew/.claude-plugin/plugin.json")
    if not any(entry.get("name") == plugin.get("name") and entry.get("source") == "plugins/logbrew"
               for entry in cursor_market.get("plugins", [])):
        fail(".cursor-plugin/marketplace.json must list the plugin with source plugins/logbrew")
    logo = cursor.get("logo", "")
    if ".." in logo or not (PLUGIN / logo).is_file():
        fail("plugins/logbrew/.cursor-plugin/plugin.json: logo must be a file in the plugin")

    # Agent Plugins 1.0.0 (Kiro powers and Cursor): closed key sets.
    if agent.get("$schema") != AGENT_PLUGINS + "plugin.schema.json":
        fail(f"plugins/logbrew/plugin.json: $schema must be {AGENT_PLUGINS}plugin.schema.json")
    for key in agent.keys() - AGENT_PLUGIN_KEYS:
        fail(f"plugins/logbrew/plugin.json: Agent Plugins does not allow the key {key!r}")
    if not agent.get("keywords") or not agent.get("author", {}).get("name"):
        fail("plugins/logbrew/plugin.json: Kiro needs keywords and an author name")
    if agent_mcp.get("$schema") != AGENT_PLUGINS + "mcp.schema.json" or set(agent_mcp) != {"$schema", "mcpServers"}:
        fail(f"plugins/logbrew/mcp.json: needs only $schema {AGENT_PLUGINS}mcp.schema.json and mcpServers")
    for name, server in agent_mcp.get("mcpServers", {}).items():
        if server.get("type") != "streamable-http" or set(server) - {"type", "url", "headers"}:
            fail(f"plugins/logbrew/mcp.json: server {name!r} must be a streamable-http server")

    # Gemini CLI loads extension skills only from skills/ at the repository root.
    if (ROOT / "skills").resolve() != SKILLS.resolve():
        fail("skills must be a link to plugins/logbrew/skills")


# Links


def check_links(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        file_part = target.split("#", 1)[0]
        if not (path.parent / file_part).exists():
            fail(f"{rel(path)}: broken link {target}")


# CLI commands


def extract_commands(text: str) -> list[str]:
    commands: list[str] = []
    in_fence = False
    pending = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            pending = ""
            continue
        if in_fence:
            if pending:
                pending += " " + stripped
            elif re.match(r"^logbrew [^=]", stripped):
                pending = stripped
            if pending:
                if pending.endswith("\\"):
                    pending = pending[:-1].rstrip()
                else:
                    commands.append(pending)
                    pending = ""
            continue
        commands.extend(re.findall(r"`(logbrew [^`]+)`", line))
    # Help lookups such as `logbrew <topic> --help` are not product commands.
    return [command for command in commands if not command.endswith(" --help")]


def command_tokens(command: str) -> list[str] | None:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    for index, token in enumerate(tokens):
        if token in SHELL_STOP:
            return tokens[:index]
    return tokens


def parse_usage(line: str) -> tuple[list[tuple[str, frozenset[str], bool]], dict[str, bool]]:
    """Return the positional pattern and the flags (name -> takes a value)."""
    words = line.split()[1:]
    pattern: list[tuple[str, frozenset[str], bool]] = []
    index = 0
    while index < len(words) and not words[index].startswith(("[", "--")):
        word = words[index]
        variadic = word.endswith("...")
        word = word.removesuffix("...")
        if word.startswith("<"):
            pattern.append(("placeholder", frozenset(), variadic))
        else:
            pattern.append(("literal", frozenset(word.split("|")), variadic))
        index += 1
    flags: dict[str, bool] = {}
    for position, word in enumerate(words):
        match = re.match(r"^\[*(--[a-z][a-z0-9-]*)(\]*)", word)
        if not match:
            continue
        following = words[position + 1] if position + 1 < len(words) else ""
        takes_value = (
            not match.group(2)
            and bool(following)
            and not following.startswith(("--", "[", "|"))
        )
        flags[match.group(1)] = flags.get(match.group(1), False) or takes_value
    return pattern, flags


def matches(tokens: list[str], usage: tuple[list, dict[str, bool]]) -> bool:
    pattern, flags = usage
    position = 0
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.startswith("--"):
            name = token.split("=", 1)[0]
            if name == "--json":
                index += 1
                continue
            if name not in flags:
                return False
            index += 2 if flags[name] and "=" not in token else 1
            continue
        if position >= len(pattern):
            if pattern and pattern[-1][2] and pattern[-1][0] == "placeholder":
                index += 1
                continue
            return False
        kind, literals, _ = pattern[position]
        if kind == "literal" and token not in literals:
            return False
        position += 1
        index += 1
    return position == len(pattern)


def collect_usage(commands: list[list[str]]) -> list[tuple[list, dict[str, bool]]]:
    binary = os.environ.get("LOGBREW_BIN", "logbrew")
    topics = {("--help",)}
    for tokens in commands:
        words = [token for token in tokens[1:] if not token.startswith("-")][:2]
        for word in words:
            topics.add((word, "--help"))
    lines: set[str] = set()
    for topic in sorted(topics):
        try:
            result = subprocess.run(
                [binary, *topic], capture_output=True, text=True, timeout=30, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            fail(f"cannot run {binary} {' '.join(topic)}: {error}")
            continue
        for line in (result.stdout + result.stderr).splitlines():
            if line.startswith("  logbrew "):
                lines.add(line.strip())
    if not lines:
        fail(f"{binary} --help printed no usage lines; install the released CLI")
    return [parse_usage(line) for line in sorted(lines)]


# MCP catalog


def download(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8")
    except OSError:
        # Some Python installs have no CA bundle; curl uses the system store.
        result = subprocess.run(
            ["curl", "--proto", "=https", "-fsSL", "--max-time", "30", url],
            capture_output=True, text=True, check=True,
        )
        return result.stdout


def load_catalog() -> dict[str, set[str]]:
    source = os.environ.get("MCP_CATALOG")
    try:
        if source:
            raw = Path(source).read_text(encoding="utf-8")
        else:
            raw = download(CATALOG_URL)
        catalog = json.loads(raw)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        fail(f"cannot read the MCP operation catalog: {error}")
        return {}
    return {
        operation["id"]: set(operation.get("input_schema", {}).get("properties", {}))
        for operation in catalog.get("operations", [])
    }


def check_operations(path: Path, text: str, catalog: dict[str, set[str]]) -> None:
    for operation in OPERATION_RE.findall(text):
        if operation not in catalog:
            fail(f"{rel(path)}: MCP operation {operation} is not in the catalog")
    for operation, field_list in FIELDS_AFTER_OPERATION_RE.findall(text):
        for field in re.findall(r"`([a-z_]+)`", field_list):
            if operation in catalog and field not in catalog[operation]:
                fail(f"{rel(path)}: {operation} has no input field {field}")


# Evals


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def check_evals(descriptions: dict[str, str]) -> list[str]:
    path = ROOT / "tests" / "evals.json"
    try:
        cases = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"tests/evals.json does not parse: {error}")
        return []
    commands: list[str] = []
    covered = set()
    for case in cases:
        label = f"eval {case.get('id')}"
        skill = case.get("skill", "")
        skill_dir = SKILLS / skill
        if skill not in descriptions:
            fail(f"{label}: unknown skill {skill!r}")
            continue
        covered.add(skill)
        if not case.get("prompt"):
            fail(f"{label}: missing prompt")
        description = normalize(descriptions[skill])
        for term in case.get("description_terms", []):
            if normalize(term) not in description:
                fail(f"{label}: description of {skill} does not mention {term!r}")
        body = normalize((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        offset = 0
        for step in case.get("steps", []):
            found = body.find(normalize(step), offset)
            if found < 0:
                fail(f"{label}: step {step!r} is missing or out of order in {skill}/SKILL.md")
            else:
                offset = found + 1
        everything = normalize(
            " ".join(p.read_text(encoding="utf-8") for p in sorted(skill_dir.rglob("*.md")))
        )
        for command in case.get("commands", []):
            if normalize(command) not in everything:
                fail(f"{label}: command not found in {skill}: {command}")
            commands.append(command)
        for operation in case.get("operations", []):
            if f"`{operation}`" not in everything:
                fail(f"{label}: operation {operation} not found in {skill}")
    for skill in descriptions.keys() - covered:
        fail(f"tests/evals.json: no eval case for {skill}")
    return commands


def main() -> int:
    descriptions: dict[str, str] = {}
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if not skill_dirs:
        fail("no skills found")
    for skill_dir in skill_dirs:
        fields = check_skill(skill_dir)
        descriptions[skill_dir.name] = fields.get("description", "")
    check_manifests()

    markdown = [ROOT / "README.md", *sorted(SKILLS.rglob("*.md"))]
    for path in markdown:
        check_links(path)

    catalog = load_catalog()
    found: list[tuple[Path, str]] = []
    for path in sorted(SKILLS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if catalog:
            check_operations(path, text, catalog)
        found.extend((path, command) for command in extract_commands(text))
    for case_command in check_evals(descriptions):
        found.append((ROOT / "tests" / "evals.json", case_command))

    parsed: list[tuple[Path, str, list[str]]] = []
    for path, command in found:
        tokens = command_tokens(command)
        if not tokens or tokens[0] != "logbrew":
            fail(f"{rel(path)}: cannot parse command: {command}")
            continue
        parsed.append((path, command, tokens))
    usage = collect_usage([tokens for _, _, tokens in parsed])
    if usage:
        for path, command, tokens in parsed:
            if not any(matches(tokens[1:], line) for line in usage):
                fail(f"{rel(path)}: command does not match the CLI help: {command}")

        # The matcher must reject seeded mistakes, or it proves nothing.
        for seeded in SEEDED_BAD_COMMANDS:
            tokens = command_tokens(seeded) or []
            if any(matches(tokens[1:], line) for line in usage):
                fail(f"self-test: a seeded bad command matched the CLI help: {seeded}")
    if catalog:
        before = len(failures)
        check_operations(ROOT / "tests" / "evals.json", SEEDED_BAD_OPERATION, catalog)
        if len(failures) != before + 2:
            fail("self-test: seeded bad MCP operation and field were not both reported")
        else:
            del failures[before:]

    unique = len({command for _, command, _ in parsed})
    if failures:
        for message in failures:
            print(f"FAIL {message}", file=sys.stderr)
        print(f"{len(failures)} check(s) failed", file=sys.stderr)
        return 1
    print(
        f"ok: {len(skill_dirs)} skills, {len(markdown)} Markdown files, "
        f"{unique} CLI commands, {len(catalog)} catalog operations"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
