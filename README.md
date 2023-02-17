# `dotfiles`

## Setup

- Install [Maestral](https://maestral.app) to `~/Dropbox`
- Install [1Password](https://1password.com)

```bash
sudo xcode-select --install

# follow instructions at https://brew.sh
# follow instructions at https://ohmyz.sh
# follow instructions at https://rustup.rs

brew install --cask 1password/tap/1password-cli
brew install chezmoi

chezmoi init git@github.com:jluszcz/dotfiles.git
```

### git-secrets

```bash
git secrets --install ~/.git-templates/git-secrets
```

## Dump Homebrew Packages

```bash
brew bundle dump -f --file=~/.config/Brewfile
chezmoi add ~/.config/Brewfile
```
