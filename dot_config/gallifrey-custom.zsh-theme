# ZSH Theme - Preview: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes#gallifrey
return_code="%(?..%{$fg[red]%}%? ↵%{$reset_color%})"

PROMPT="%{$fg[green]%}%B[MacBook]%b%{$reset_color%} %2~ \$(git_prompt_info)%{$reset_color%}%B»%b "
RPS1="${return_code}"

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[blue]%}<"
ZSH_THEME_GIT_PROMPT_SUFFIX="> %{$reset_color%}"

unset return_code
