#!/usr/bin/env sh
#
# Validate chezmoi JSON templates.
#
# check-json matches `*.json`, so a `*.json.tmpl` file is linted by nothing —
# and a template that renders to malformed JSON only surfaces at apply time, in
# a config the affected tool then silently ignores. Rendering each template
# first gives check-json's job something it can parse.
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

    # json.tool reports the parse error on stderr and nothing useful on stdout,
    # so swap the two and capture, to name the template alongside its error.
    if ! findings=$(printf '%s\n' "$rendered" | python3 -m json.tool 2>&1 >/dev/null); then
        printf '%s: %s\n' "$template" "$findings" >&2
        status=1
    fi
done

exit "$status"
