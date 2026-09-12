#!/usr/bin/env sh
#
# Validate chezmoi TOML templates.
#
# check-toml matches `*.toml`, so a `*.toml.tmpl` file is linted by nothing —
# and a template that renders to malformed TOML only surfaces at apply time, in
# a config the affected tool then rejects outright. Rendering each template
# first gives check-toml's job something it can parse.
#
# The render uses this machine's chezmoi context, so an `{{ if eq .chezmoi.os
# ... }}` branch is only checked on a runner of that OS. CI is Linux; the macOS
# branches get checked when you run the hooks locally.

set -eu

# .email lives in the config that `chezmoi init` writes, which a CI runner never
# has, so the render needs it supplied. A stub keeps the result identical on
# every machine and keeps a real address out of the repo — only the syntax
# around the value matters here.
override_data='{"email":"user@example.com"}'

status=0

for template in "$@"; do
    # --init defines promptStringOnce, which .chezmoi.toml.tmpl calls and plain
    # execute-template leaves undefined.
    #
    # onepasswordRead needs an unlocked vault, which CI has no way to provide,
    # and skipping every template that calls it would leave this hook with
    # nothing to check. printf returns its format string unchanged, so swapping
    # the two stands each secret in as its own op:// reference — the wrong
    # value, but a quoted string, which is all the parse below looks at.
    rendered=$(sed 's/onepasswordRead/printf/g' "$template" |
        chezmoi execute-template --source . --init --override-data "$override_data") || {
        echo "$template: chezmoi could not render this template" >&2
        status=1
        continue
    }

    # The decode error goes to stderr and nothing useful to stdout, so swap the
    # two and capture, to name the template alongside its error.
    if ! findings=$(printf '%s\n' "$rendered" | python3 -c 'import sys, tomllib
try:
    tomllib.loads(sys.stdin.read())
except tomllib.TOMLDecodeError as error:
    raise SystemExit(str(error))' 2>&1 >/dev/null); then
        printf '%s: %s\n' "$template" "$findings" >&2
        status=1
    fi
done

exit "$status"
