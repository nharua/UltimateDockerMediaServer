## Session history and logging rules

Session start:
1. Read `SESSIONS.md` to check previous session history and open TODOs.

Session end:
- If not already requested, remind the user to add a new `SESSIONS.md` entry.
- Only update `SESSIONS.md` when explicitly asked, following the `update-sessions` skill.
- Do not run `git status`, `git add`, or `git commit` unless asked.
- Checkpoint sequence: run `git-commit` first when requested to obtain the commit hash (git checkpoint), then record this checkpoint under `### Git checkpoint` in `SESSIONS.md`.

## Language policy
- **Conversation**: Use Vietnamese for all communications between user and agent.
- **Session logs**: Write and update `SESSIONS.md` entries in Vietnamese.
- **Technical artifacts**: Use English for all other artifacts, including git commit messages, issue and ticket docs under `.scratch/`, domain documentation, ADRs, and code comments.

## Writing style
- Always apply the `unslop` skill to all responses, documentation, and commit messages.

## Security policy
- Never output, log, or record raw passwords, secret tokens, or sensitive credentials in user communications, `SESSIONS.md`, technical artifacts, documentation, or git commits. Always use generic placeholders (e.g., `<PASSWORD>`, `<TOKEN>`) instead.
