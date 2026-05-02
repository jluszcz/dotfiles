# chezmoi Dotfiles

This is a [chezmoi](https://www.chezmoi.io) dotfiles repository. chezmoi manages dotfiles by mapping files in this repo to their
target locations under `$HOME` using filename prefixes and suffixes as metadata.

## File Naming

chezmoi encodes metadata in filenames. Key conventions used in this repo:

| Prefix/Suffix | Meaning | Example |
|---|---|---|
| `dot_` | Maps to a dotfile (`.`) in `$HOME` | `dot_zshrc` → `~/.zshrc` |
| `executable_` | Target file should be `chmod +x` | `executable_tardir` → `~/.bin/tardir` |
| `private_` | Target file should be `chmod 600` | `private_dot_ssh/` → `~/.ssh/` |
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
- `run_onchange_symlinks.sh.tmpl` — creates symlinks for app prefs (macOS only)

## Rules of Thumb

- **New dotfile**: prefix with `dot_`, add `.tmpl` suffix only if it needs per-machine values.
- **New personal script**: add to `dot_bin/` with `executable_` prefix, no extension.
- **Sensitive file** (keys, tokens): add `private_` prefix so chezmoi sets restrictive permissions.
- **Mac OS-only config**: wrap in `{{- if eq .chezmoi.os "darwin" }}` inside a `.tmpl` file.
- **Don't edit target files directly** — edit the source files here and run `chezmoi apply`.
