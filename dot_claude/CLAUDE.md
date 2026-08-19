# Development Guidelines

- Match the existing code — study similar implementations before introducing new patterns,
  libraries, or tools.
- Never disable a failing test; fix it.
- Stop and reassess after 3 failed attempts at the same problem.
- Never write a real email address into a file, commit message, or PR — use `user@example.com`
  or read it at runtime from config/env. This includes the user's own address; git authorship
  metadata is exempt.
- Documentation and comments describe the code as it is, not how it got there. No "changed to…",
  "previously…", "kept for backwards compatibility" — that belongs in the commit message. Comments
  carry the non-obvious *why*; don't paraphrase the line below them.
- Never commit directly to the default branch — create a feature branch first.
- Commit with the "jluszcz:commit" skill — it handles feature branches, doc sync, and git safety.
- Stacked PRs: `git switch -c <branch> <parent>` then `git branch --set-upstream-to=<parent>`.
