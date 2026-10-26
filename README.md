# `dotfiles`

`chezmoi init --apply` installs oh-my-zsh and rustup and, where git-secrets is installed, sets up
its hook template. On Linux it also installs sccache; on macOS the Brewfile does. oh-my-zsh is
pulled weekly on apply after that.

## Mac OS

```bash
sudo xcode-select --install

# follow instructions at https://brew.sh

# chezmoi pulls secrets from 1Password at apply time, so the CLI has to be
# installed and signed in first
brew install chezmoi 1password-cli
op signin

chezmoi init --apply git@github.com:jluszcz/dotfiles.git
```

## Linux

```bash
sudo yum -y install zsh util-linux-user
chsh -s "$(command -v zsh)"

# chezmoi pulls secrets from 1Password at apply time, so install the CLI
# (https://developer.1password.com/docs/cli/get-started) and sign in first
op signin

sh -c "$(curl -fsLS get.chezmoi.io)" -- -b ~/.local/bin init --apply git@github.com:jluszcz/dotfiles.git
```

### Synology

Copy [`dot_bin/executable_up-nas`](dot_bin/executable_up-nas) to the NAS and run it. It installs rclone, tmux and
chezmoi into `~/.bin`, then runs `chezmoi init --apply`. Once applied, `up-nas` updates all three.

```bash
bash up-nas
```
