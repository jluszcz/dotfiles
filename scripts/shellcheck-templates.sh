#!/usr/bin/env sh
#
# Shellcheck chezmoi shell templates.
#
# shellcheck cannot parse `{{ ... }}`, so the .tmpl files are excluded from the
# normal shellcheck hook — which left the run_*.sh.tmpl scripts, the ones
# chezmoi actually executes on every apply, linted by nothing. Rendering each
# template first gives shellcheck something it can read.
#
# The render uses this machine's chezmoi context, so an `{{ if eq .chezmoi.os
# ... }}` branch is only checked on a runner of that OS. CI is Linux; the macOS
# branches get checked when you run the hooks locally.

set -eu

status=0

for template in "$@"; do
    rendered=$(chezmoi execute-template --source . <"$template") || {
        echo "$template: chezmoi could not render this template" >&2
        status=1
        continue
    }

    # Capture rather than pipe straight to sed: the exit status of a pipeline is
    # its last command's, so piping would report sed's success and pass a file
    # shellcheck had just rejected.
    if ! findings=$(printf '%s\n' "$rendered" | shellcheck -x -s sh --format=gcc -); then
        printf '%s\n' "$findings" | sed "s|^-|$template|" >&2
        status=1
    fi
done

exit "$status"
