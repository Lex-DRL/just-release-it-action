<div align="center">
  
# Just release it! (from TOML) 📦 Action

[![GitHub Release][github-release-shield]][github-release-url]

[github-release-shield]: https://img.shields.io/github/v/release/Lex-DRL/just-release-it-action?logo=github
[github-release-url]: https://github.com/Lex-DRL/just-release-it-action/releases/latest

*Easiest-to-setup GitHub release for python projects:<br />
just read version from `pyproject.toml`, build changelog and release it!*
</div>

Originally created to assist with releasing custom nodes for [ComfyUI](https://github.com/Comfy-Org/ComfyUI), but can be used for any python packages that rely on `pyproject.toml` for build/publishing.

## Output

An example of generated release: https://github.com/Lex-DRL/test-ComfyUI-dummy/releases

## Just set it up!

> [!NOTE]
> ### ULTRA-TL;DR
> - Just use the action in your GitHub workflow.
> - Even with no configuration, it should "just work" as long as you have version in `pyproject.toml`, and at least somewhat-organized commit history.

### TL;DR
- Have a `pyproject.toml` file in the repo root.
- Make sure it contains the `version` field under the main `[project]` section:
  ```toml
  [project]
  # ...
  version = "1.2.3"
  ```
- Create a GitHub workflow file under `.github\workflows\` - name it something like `just-release-it.yml`.
- Put the following code inside it (replace `main` with your default branch, if it has a different name):
  <details>
  <summary>▶️ Minimal workflow code ◀️</summary>

  ```yaml
  name: Release

  on:
    push:
      branches:
        - main
      paths:
        - "pyproject.toml"
    workflow_dispatch:  # Allows to manually run the workflow, too

  jobs:
    publish-release:
      name: >-
        📦 Publish release
      runs-on: ubuntu-latest
      timeout-minutes: 5  # Prevent stuck jobs

      permissions:
        contents: write  # Necessary to publish a release

      steps:
        - name: ♻️ Check out code
          uses: actions/checkout@v7
          with:
            fetch-depth: 0  # Critical for changelog + first-release support
  
        - name: "📦 Just release it!"
          id: just-release-it
          uses: Lex-DRL/just-release-it-action@v1
  ```
  </details>
- `📦 Just release it!` itself is [released](https://github.com/Lex-DRL/just-release-it-action/releases) with itself... yeah, a little recursion here. So, to have a more production-like example, check [its own release workflow](https://github.com/Lex-DRL/just-release-it-action/blob/main/.github/workflows/just-release-it.yml).
- The `📦 Just release it!` action doesn't require any extra configuration, unless you want to override defaults... which are already good enough for most repos.
- Lastly, make sure you have a release or a tag **on GitHub** for the latest previous version, and it's made on the right commit. Create at least the tag if you don't have any yet (i.e., if you were releasing directly to a package registry). Name it like `v1.2.3` / just `1.2.3` (with your version, obviously).
  - If you don't do so, your first release published with `📦 Just release it!` will contain **THE ENTIRE GIT HISTORY** as the changelog.

## What does it do, specifically?

The action:
- [Reads the current version from `pyproject.toml`](https://github.com/Lex-DRL/pyproject-toml-version-action).
- [Standardizes it](https://github.com/Lex-DRL/standardize-version-action) for the release name/tag.
- Detects the changelog range: from the last published release to the latest commit in the branch.
- Builds a changelog (using [orhun/git-cliff-action](https://github.com/orhun/git-cliff-action) + a custom config).
- Publishes the release (using [softprops/action-gh-release](https://github.com/softprops/action-gh-release)).
- Most of the heavy-lifting in the action is done with python, so the action also sets it up in the runner.

## How to name commits? (to categorize them properly)

In short, you don't need to do anything special. Just continue naming your commits in the same (at least somewhat logical) way that you already do.

The action is intentionally built to catch any naming scheme that's used widely. Specifically, it detects:
- [Conventional Commits](https://www.conventionalcommits.org/) - so `feat:`, `fix:`, `upd:`, `ci:`, `bld:` etc. prefixes.
- [GitMoji](https://gitmoji.dev/) - i.e. prefixing commit titles with emoji to classify them.
- Some natural-language words that the titles start with, like: `Adds ...`, `Fixes ...`, `New ...`
- Breaking changes are detected by the `prefix!:` or `prefix(subcategory)!:` format (so, with `!`) from Conventional Commits, as well as by `BREAKING CHANGES:` section somewhere in commit body.
- ... and even some common typos are caught.

> [!NOTE]
> For PRs, only the title is scanned. So, to detect breaking changes in them, use any of the title prefixes.
> 
> Regular merges and plain commits also catch the `BREAKING CHANGES:` section in commit body.

## What categories are detected?

The `git-cliff` tool (used internally) relies on regexes to classify commits. So the table below isn't exhaustive, because it would be insane to list all the spelling variations here.

GitHub or your browser might "prettify" some unicode characters into actual emojis - so it might look like some emojis appear twice. They're not - check the raw text of this ReadMe.

Listed in the order of priority:

| Name | Emoji prefix | [CC](https://www.conventionalcommits.org/) prefix | Natural text |
|---|---|---|---|
| `💥 Breaking Changes 💥` | 💥 ❗ ❕ ‼️ ‼ | `any!` `any(cat)!` | `Breaks ...`, `Breaking ...` etc; `BREAKING CHANGES:` section in the comment body |
| `⚠️ Deprecations` | ⚠️ ⚠ | `depr` | `Deprecated ...`, `Deprecates ...`, `Deprecation`, etc. |
| `↩️ Rollbacks` | ↩️ ↩ ↶ 🔙 ⏪️ ⏪ | - | `Revert ...`, `Reverts ...`, `Undo ...`, `Roll back...` |
| `✨ New Features` | ✨ 🌟 ⭐ 🎉 | `new` `feat` `feature` `add` `support` | `Adds ...`, `Supports ...`, `Supporting ...` |
| `🚀 Improvements` | 🚀 🚩 🚸 ♿️ | `upd` `enh` `enhance` `impr` `improve` | `Changes ...`, `Enhancing ...`, `Improvement ...`, `Better ...`, `Robust ...` |
| `🛠️ Fixes` | 🛠️ 🛠 🐛 🩹 🚑️ 🚑 🚨 🥅 | `bug` `fix` `bugfix` | `Fixes ...`, `Correct ...`, `Properly ...` |
| `⚡ Performance` | ⚡️⚡ | `prf` `perf` | `Performance ...` |
| `🔒 Security` | 🔒 🔐 🛡️ 🛡 | `sec` `security` | `Security ...` |
| `📝 Documentation` | 📝 📄 💬 | `doc` `docs` `readme` | `Documentation ...`, `Documents ...` |
| `♻️ Refactor` | ♻️ ♻ 🚚 | `refac` `refactor` `reimpl` `rename` | `Re-factored ...`, `Fully refactoriing ...`, `Re-implemented ...`, `Renames ...` |
| `🔬 Tests` | 🔬 🧪 ⚗️ ✅ 🦺 | `tst` `test` | `Tested ...`, `Testing ...` |
| `🎨 Code Style` | 🎨 | `fmt` `format` `stl` `style` | `Formatting ...`, `Code format ...`, `Code style ...` |
| `📦 Build/Packaging` | 📦 | `bld` `build` `pyproject` `setup.cfg` `setup.py` `requirements.txt` | `Building ...` |
| `🤖 CI/CD` | 🤖 👷 | `ci` `cd` | - |
| `🧹 Maintenance` | 🧹 🙈 💸 | `chr` `chore` `clean` `cleanup` `maintain` `git` `github` `gitignore` `gitattr` `gitattributes` | - |
| `Version` | 🔖 🏷️ 🏷 | `ver` `version` `bump` `release` | `v1...`, `v2...`, `ver3...` with any numbers |
| `🔀 Other changes` / `⚙️ What's changed` | - | - | All other commits |

## Configuration

Below is a snippet with all the configurable settings and their default values when omitted (all of them could be).

> [!NOTE]
> For boolean-like options:
> - Empty string (`''`) and `'false'` are treated as `false`.
> - Anything else means `true`.

```yaml
# ...

jobs:
  publish-release:
    # ...
    steps:
    # ...
    
    - name: "📦 Just release it!"
      id: just-release-it
      uses: Lex-DRL/just-release-it-action@v1
      with:
        project-toml-file: 'pyproject.toml' # Path to the TOML file in your repo to extract version from.
        attach-files: '' # Glob of files to attach (e.g. "dist/*").
        # Leave empty/unset for source-only release.
        # As an example config for PyPI build+release (with wheel), see:
        # https://github.com/Lex-DRL/typing-clean/blob/main/.github/workflows/just-release-it.yml
        
        # PYTHON SETUP
        # Internally, the action uses python, so it sets it up first
        skip-python-setup: false # Set to 'true' if it's already set up before by any of the previous steps
        python-version: '3.x' # Which python version to install
        
        # VERSION STANDARDIZATION
        # Normally, the extracted version is standardized for the release title/tag.
        # See: https://github.com/Lex-DRL/standardize-version-action
        skip-version-standardize: false # Set to 'true' to disable it
        
        # RELEASE TOGGLES
        is-pre-release: '' # Override pre-release status:
        # - '': let the version-standardizing step to decide (or 'false' if this step is skipped)
        # - 'false': force regular release
        # - 'true' or any other value: force pre-release
        is-draft: false # Set to 'true' to create a release draft instead of publishing right away
        
        # ADVANCED USE
        # The main "magic" of nice release notes is done by dynamically
        # building a config for `orhun/git-cliff-action`.
        # That's what all the 'cat-*' settings below used for.
        # But you can completely bypass this logic and instead provide
        # your own custom config for `git-cliff`... however, if you do,
        # the good question is why do you use "Just release it!" in the
        # first place: you're likely better off just using `git-cliff`
        # directly. Though, still, if you wish, here it is:
        cliff-config-file: '' # Path to custom git-cliff (toml) config
        # ... but are you sure? Maybe what you actually need is:
        # - request a feature: https://github.com/Lex-DRL/just-release-it-action/issues
        # - or PR it: https://github.com/Lex-DRL/just-release-it-action/pulls
        github-token: "${{ github.token }}" # For extremely fancy use cases,
        # you can provide a non-default token.
        # Alternatively, a global workflow-level `GITHUB_TOKEN` env-var
        # could be used instead.
        # Don't touch this setting unless you **really** know
        # what you're doing and why.
        
        # ALERTS
        # By default, the "important" categories
        # (Breaking Changes, Deprecations, Rollbacks)
        # are wrapped into GitHub alert blocks.
        cat-alert-blocks: true # When 'false':
        # - such blocks are disabled
        # - these categories are output as usual
        
        # CATEGORY CUSTOMIZATION
        # You're free to rename the category titles, as they appear
        # in the release notes. However, please make sure each of them
        # stays unique and doesn't contain any HTML tags - or it might
        # lead to messed up release notes.
        # Regardless of the order you specify them in, categories always
        # appear in release notes in the following order:
        cat-breaking: '💥 Breaking Changes 💥'
        cat-depr: '⚠️ Deprecations'
        cat-revert: '↩️ Rollbacks'
        cat-feat: '✨ New Features'
        cat-enhance: '🚀 Improvements'
        cat-fix: '🛠️ Fixes'
        cat-perf: '⚡ Performance'
        cat-security: '🔒 Security'
        cat-doc: '📝 Documentation'
        cat-refactor: '♻️ Refactor'
        cat-test: '🔬 Tests'
        cat-style: '🎨 Code Style'
        cat-build: '📦 Build/Packaging'
        cat-ci: '🤖 CI/CD'
        cat-chore: '🧹 Maintenance'
        cat-version: 'Version'
        cat-unclassified-multi: '🔀 Other changes' # When appears along with other categories
        cat-unclassified-only: "⚙️ What's changed" # When all the commits for the release are "unclassified"
```

## Dynamic version

(i.e., fetching version dynamically from a dedicated python file)

> [!WARNING]
> **TODO** 🚧🏗️: Planned but not yet implemented

## Outputs

The action also provides outputs for you to use in later steps:
- `tag`: Final tag name - with "v" prefix if version was standardized. Otherwise, the raw version extracted from TOML as-is.
- `raw-version`: Version without "v" prefix, if it was standardized. Otherwise, the raw version extracted from TOML as-is.
- `is-pre`: Whether the release is created as a pre-release.
- `changelog`: The generated release notes.
