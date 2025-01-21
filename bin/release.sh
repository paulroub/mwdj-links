#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

txt_version=$(cat VERSION)
gem_version=$(cat linky.gemspec | grep -E "spec\.version\s+=" | awk '{print $3}' | tr -d "\"")

if [ "$txt_version" != "$gem_version" ]; then
    echo "Version mismatch: VERSION ($txt_version) != Gemspec version ($gem_version)"
    exit 1
fi

if ! grep -Fq "linky $txt_version" CHANGELOG.md; then
    echo "Version $txt_version not found in CHANGELOG.md"
    exit 1
fi

git_status=$(git status --porcelain)
git_branch=$(git rev-parse --abbrev-ref HEAD)

if [ -n "$git_status" ]; then
    echo "Uncommitted changes:"
    git status --porcelain
    exit 1
fi

if [ "$git_branch" != "main" ]; then
    echo "Not on main branch"
    exit 1
fi

git tag -a "$txt_version" -m "Release $txt_version"
bundle exec gem build linky.gemspec
bundle exec gem push "jekyll-theme-linky-$txt_version.gem"
git push --tags
git push
