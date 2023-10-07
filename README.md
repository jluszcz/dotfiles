# `dotfiles`

## Mac OS

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

### Dump Homebrew Packages

```bash
brew bundle dump -f --file=~/.config/Brewfile
chezmoi add ~/.config/Brewfile
```

## Linux

```bash
sudo yum -y install zsh

# follow instructions at https://ohmyz.sh
# follow instructions at https://rustup.rs
# install sccache from https://github.com/mozilla/sccache/releases
# follow instructions at https://www.chezmoi.io/install

sudo mv bin/chezmoi /usr/local/bin
rmdir bin

chezmoi init git@github.com:jluszcz/dotfiles.git
```

## General

### git-secrets

```bash
git secrets --install ~/.git-templates/git-secrets
```
