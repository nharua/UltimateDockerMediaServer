## Session history and logging rules

Session start:
1. Read `PROJECT_SUMMARY.md` to check previous session history and open TODOs.

Session end:
- If not already requested, remind the user to add a new `PROJECT_SUMMARY.md` entry.
- Only update `PROJECT_SUMMARY.md` when explicitly asked, following the `update-project-summary` skill.
- Do not run `git status`, `git add`, or `git commit` unless asked.

## Writing style
- Always apply the `unslop` skill to all responses, documentation, and commit messages.
