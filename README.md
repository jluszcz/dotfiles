# `dotfiles`

## Mac OS

- Install [iTerm2](https://iterm2.com)
- Install [Dropbox](https://www.dropbox.com/install)

```bash
sudo xcode-select --install

# follow instructions at https://brew.sh
# follow instructions at https://ohmyz.sh
# follow instructions at https://rustup.rs

brew install chezmoi

# chezmoi pulls secrets from 1Password at apply time, so the CLI has to be
# installed and signed in first
brew install --cask 1password-cli
op signin

chezmoi init git@github.com:jluszcz/dotfiles.git
```

## Linux

```bash
sudo yum -y install zsh
# set default shell by editing /etc/passwd

# follow instructions at https://ohmyz.sh
# follow instructions at https://rustup.rs
# install sccache from https://github.com/mozilla/sccache/releases
# follow instructions at https://www.chezmoi.io/install

sudo mv bin/chezmoi /usr/local/bin
rmdir bin

chezmoi init git@github.com:jluszcz/dotfiles.git
```

### Synology

```bash
# install rclone from https://rclone.org/downloads/
# install tmux from https://github.com/tmux/tmux-builds/releases

mkdir -p ~/.cache/chezmoi/tmp
# follow instructions at https://www.chezmoi.io/install
```

## General

### git-secrets

```bash
git secrets --install ~/.git-templates/git-secrets
```
