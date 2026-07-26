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

- `shellcheck` covers the plain scripts under `dot_bin/` and `dot_config/rustbin`, excluding `.tmpl` files.
- `shellcheck-templates` (`scripts/shellcheck-templates.sh`) renders each `run_*.sh.tmpl` with
  `chezmoi execute-template` and pipes the result through shellcheck. Its `files` pattern used to be part of the
  first hook's, where the `.tmpl` exclusion silently cancelled it out — **zero `run_` scripts were linted by
  anything**, despite the config appearing to cover them.

A rendered template only exercises the branches that this machine's context selects, so an
`{{ if eq .chezmoi.os "darwin" }}` block is checked when you run the hooks on macOS, and the `linux` side is what CI
checks. Run the hooks locally before pushing macOS-only changes.
