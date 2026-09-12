# chezmoi Dotfiles

This is a [chezmoi](https://www.chezmoi.io) dotfiles repository. chezmoi manages dotfiles by mapping files in this repo to their
target locations under `$HOME` using filename prefixes and suffixes as metadata.

## File Naming

chezmoi encodes metadata in filenames. Key conventions used in this repo:

| Prefix/Suffix | Meaning | Example |
|---|---|---|
| `dot_` | Maps to a dotfile (`.`) in `$HOME` | `dot_zshrc` → `~/.zshrc` |
| `executable_` | Target file should be `chmod +x` | `executable_tardir` → `~/.bin/tardir` |
| `private_` | Strip group/world permissions on the target (`0600` files, `0700` dirs) | `private_dot_ssh/` → `~/.ssh/` |
| `.tmpl` suffix | File is a Go template rendered at apply time | `dot_zshrc.tmpl` → `~/.zshrc` |
| `run_onchange_` | Script run only when its contents change | `run_onchange_brew.sh.tmpl` |

Prefixes are applied left-to-right and can be combined: `private_dot_ssh/` → `~/.ssh/` (private directory named `.ssh`).

## Templates

Files ending in `.tmpl` are Go templates. Use them when a file needs to vary by machine. Common variables available:

- `{{ .chezmoi.homeDir }}` — home directory path
- `{{ .chezmoi.os }}` — OS (`darwin`, `linux`)
- `{{ .chezmoi.hostname }}` — machine hostname

Guard OS-specific blocks with `{{- if eq .chezmoi.os "darwin" }}...{{- end }}`.

## Directory Structure

- `dot_bin/` → `~/.bin/` — personal scripts; all files should have `executable_` prefix
- `dot_config/` → `~/.config/` — app config files
- `dot_claude/` → `~/.claude/` — Claude Code settings
- `private_dot_ssh/` → `~/.ssh/` — SSH config (private)
- `run_onchange_brew.sh.tmpl` — runs `brew bundle` when the Brewfile changes
- `run_symlinks.sh.tmpl` — creates symlinks for app prefs on every apply (macOS only)

`dot_claude/CLAUDE.md` is the source of `~/.claude/CLAUDE.md`, so working in this repo would otherwise load the
same instructions twice — once as user memory from `~/.claude/`, once as project memory from the source file.
The `claudeMdExcludes` entry in `dot_claude/settings.json.tmpl` suppresses the source copy. It is matched against
*absolute* paths, which is what lets one pattern (`**/dot_claude/CLAUDE.md`) skip the source while leaving the
applied `~/.claude/CLAUDE.md` loading normally — the two never collide despite the setting itself being applied
to `~/.claude/settings.json`.

The settings file is a template so the iTerm2 `cc-status` hooks can be guarded on `darwin`: `~/.config/iterm2/cc-status`
is a symlink iTerm2 installs into its own app bundle, so on the Synology every hook would fire a missing command.
Claude Code rewrites `~/.claude/settings.json` itself (reordering keys, escaping `/`), so `chezmoi diff` on it is
mostly noise; compare the parsed JSON instead.

## Shells

Interactive shells are zsh (`dot_zshrc.tmpl`) on every machine except the Synology NAS, which logs in under POSIX
`sh`. `.chezmoiignore.tmpl` enforces the split: `.zshrc` is ignored on the `Synology` host, while `.profile`,
`.tmux.conf`, `.bin/up-rc` and `.config/rclone/` are ignored everywhere else.

`dot_profile` is therefore Synology-only and has to stay POSIX — `case ... esac` rather than `[[ ]]`, no arrays, no
`local`, no `+=`. Under `dot_bin/` the shebang decides rather than the directory: bash is installed on the NAS, so a
script declaring `#!/usr/bin/env bash` may use bashisms, while the several declaring `#!/usr/bin/env sh` may not.
shellcheck infers its dialect from the shebang and catches a bashism in the latter — but neither `dot_profile` nor
`dot_zshrc.tmpl` matches the hooks' `files` patterns (see Checks), so nothing catches one there.

## Rules of Thumb

- **New dotfile**: prefix with `dot_`, add `.tmpl` suffix only if it needs per-machine values.
- **New personal script**: add to `dot_bin/` with `executable_` prefix, no extension.
- **Secret value** (keys, tokens, IDs): **never write the value into a file in this repo.** `private_` only
  changes permissions on the *applied* target — it does nothing to the source file, which is committed to git in
  plaintext. Instead create a `private_<name>.tmpl` and pull the value from 1Password at apply time:

  ```
  export JAKESKY_API_KEY="{{ onepasswordRead "op://Personal/Open Weather/api key" }}"
  ```

  Only the `op://` reference is committed; the secret itself never enters the repo. See
  `dot_config/envrc/private_executable_jakesky.tmpl` and its siblings for the pattern. The `.tmpl` suffix is
  what makes this work — a `private_` file *without* it is not templated, so the value would be stored literally.
- **Mac OS-only config**: wrap in `{{- if eq .chezmoi.os "darwin" }}` inside a `.tmpl` file.
- **Don't edit target files directly** — edit the source files here and run `chezmoi apply`.

## Checks

`pre-commit run --all-files` is the gate, and CI (`.github/workflows/ci.yml`) runs the same hooks on every push and
PR — the repo previously had no CI at all, so nothing but local discipline enforced them.

Shell linting takes two hooks, because shellcheck cannot parse chezmoi's `{{ ... }}`:

- `shellcheck` covers the plain scripts under `dot_bin/`, `dot_config/rustbin` and `scripts/`, excluding `.tmpl` files.
- `shellcheck-templates` (`scripts/shellcheck-templates.sh`) renders each `run_*.sh.tmpl` with
  `chezmoi execute-template` and pipes the result through shellcheck. Its `files` pattern used to be part of the
  first hook's, where the `.tmpl` exclusion silently cancelled it out — **zero `run_` scripts were linted by
  anything**, despite the config appearing to cover them.

JSON linting splits the same way, for the same reason:

- `check-json` covers plain `*.json` files; its pattern does not reach a `*.json.tmpl`.
- `check-json-templates` (`scripts/check-json-templates.sh`) renders each `*.json.tmpl` and parses the result with
  `python3 -m json.tool`. Without it a template that renders to malformed JSON surfaces only at apply time, in a
  config the affected tool then silently ignores. `private_` templates are excluded: rendering one calls
  `onepasswordRead`, which CI cannot satisfy.

TOML linting splits a third time, and handles secrets differently:

- `check-toml` covers plain `*.toml` files; its pattern does not reach a `*.toml.tmpl`.
- `check-toml-templates` (`scripts/check-toml-templates.sh`) renders each `*.toml.tmpl` and parses the result with
  `tomllib`. Excluding every template that calls `onepasswordRead` would leave the hook with nothing to check, since
  none of the TOML templates are `private_`, so the script swaps `onepasswordRead` for `printf` before rendering:
  `printf` returns its format string unchanged, standing each secret in as its own `op://` reference. The value is
  wrong and the syntax is real, which is all the parse looks at. `.chezmoi.toml.tmpl` is excluded instead — it uses
  `promptStringOnce`, which only `chezmoi init` defines, not `chezmoi execute-template`.

A rendered template only exercises the branches that this machine's context selects, so an
`{{ if eq .chezmoi.os "darwin" }}` block is checked when you run the hooks on macOS, and the `linux` side is what CI
checks. Run the hooks locally before pushing macOS-only changes.
