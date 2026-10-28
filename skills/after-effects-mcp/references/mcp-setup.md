# MCP 설치·진단

사용자가 MCP를 지정했거나 MCP 설치·연결 진단을 요청한 경우에만 읽는다. 일반 AE 조작에는 SKILL.md의 1–4단계를 쓴다.

Connect Codex to Adobe After Effects through the implementation already selected by the user. Default to diagnosis and a read-only smoke test. Installing software, enabling auto-run, executing mutating JSX, saving, rendering, or closing projects requires that action in the request.

## Identify the stack

Before changing anything, record:

- OS and After Effects version/location
- active Codex MCP registration, command, args, and startup error
- server implementation and version
- bridge/daemon process and data directory
- AE panel state and scripting permission
- open project and unsaved-work risk

Do not replace an existing Node bridge with `ae-mcp`, or the reverse, merely because this skill mentions both.

## Diagnose by layer

1. **Codex config**: can the current CLI parse config and list the registered server?
2. **MCP server**: does the exact registered command start and expose tools?
3. **Broker/daemon**: is the local bridge process running and using the expected directory/port?
4. **AE panel**: is the matching ScriptUI panel installed, open, and connected?
5. **JSX execution**: can a non-mutating query return `app.version` from the intended AE instance?

Stop at the first failing layer. Do not reinstall every layer at once.

## Implementation notes

### Aodaruma / `adobe-mcp-rs` / `ae-mcp`

- `serve-stdio` connects the MCP client.
- `serve-daemon` brokers AE instances and bridge commands.
- A persistent service is optional and installed only when requested.
- Use the current official release for the detected OS; verify release assets and checksums before install.
- Older `Aodaruma/after-effects-mcp-rs` links may redirect to `Aodaruma/adobe-mcp-rs`; prefer the current repository and `adobe-mcp-rs-*` asset names.

### Node/llamainator-style server

- Verify the Node executable and registered built entry file exist.
- Inspect the package's own bridge install instructions and current build output.
- Rebuild or reinstall only the broken component; preserve working config and AE panels.
- On this Mac, `/Users/han/after-effects-mcp/build/index.js` plus the `MCP Bridge Auto` panel may be the active path; verify its stdio initialization, `tools/list`, and `~/Documents/ae-mcp-bridge/` exchange files before replacing it.

## Bridge setup

- Discover the correct AE Scripts/ScriptUI Panels directory for the current OS and AE version.
- Use the selected package's bridge installer or documented copy method after inspecting it.
- Enabling “Allow Scripts to Write Files and Access Network” and “Auto-run commands” expands authority. Explain the impact and enable them only for the requested automation.
- Multiple AE instances require an explicit target version or instance ID.

## JSX safety over MCP

- Execute only trusted local JSX whose source is visible in the task.
- Start with a non-mutating smoke test such as returning `app.version`.
- If the MCP implementation labels arbitrary JSX as `unsafe`, treat that as a warning, not a reason to run all code automatically.
- Saving, rendering, importing, deleting, closing, or overwriting requires explicit target paths and effect review.
- Preserve unsaved projects; do not close or replace them during diagnosis.
- Use timeouts and a human-readable description for every command.

Safe smoke payload shape when supported:

```json
{
  "code": "return app.version;",
  "description": "Read After Effects version",
  "timeoutMs": 10000
}
```

Add implementation-specific mode fields only when required by the inspected tool schema.

## Common failures

- Server not listed: stale or invalid Codex config, old CLI, wrong profile.
- Server exits: missing binary/build file, dependency error, incompatible args.
- No AE instance: project manager/application state, panel closed, daemon mismatch.
- Stale result: bridge roots or instance heartbeat differ.
- Wrong instance: target version/ID not specified.
- JSX timeout: modal dialog, blocked scripting permission, long render, or panel auto-run off.

## Verification

Verify separately:

1. current CLI loads config and lists the server;
2. server exposes expected MCP tools;
3. broker sees the intended AE instance;
4. read-only JSX returns the real AE version;
5. requested mutation, if any, has visible AE/file readback.

## Completion

Report the implementation, exact config/binary/bridge paths, layer that failed, changes made, smoke-test evidence, AE state left running, and any unverified save/render result. Never include credentials or unrelated project contents.
