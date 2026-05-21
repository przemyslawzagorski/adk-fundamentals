# Formaty Changelogów

## Format 1: Keep a Changelog (keepachangelog.com)

Standard branżowy — czytelny, z linkami do diff.

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-04-12

### Added
- Polish language support for all modules
- Team workspace feature with role-based access

### Changed
- Improved file sync performance by 2x
- Updated dependency versions

### Fixed
- Large image upload failure
- Timezone display in scheduled posts

### Removed
- Legacy API v1 endpoints (deprecated since 1.0.0)

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```

## Format 2: GitHub Release Notes

Używany w GitHub Releases — z @mentions i #issue.

```markdown
## What's Changed

### ✨ New Features
* Team Workspaces — create separate spaces for projects by @developer in #142
* Keyboard shortcuts overlay (`?`) by @designer in #148

### 🐛 Bug Fixes
* Fix large image upload by @backend-dev in #151
* Fix timezone in scheduled posts by @backend-dev in #153

### ⚡ Performance
* 2x faster file sync by @infra-team in #150

**Full Changelog**: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```

## Format 3: Slack / Teams Announcement

Krótki, wizualny, dla kanału #releases.

```
🚀 *v2.5.0 is live!*

✨ *New*
• Team Workspaces — collaborate on projects together
• Keyboard shortcuts — press ? for the full list

⚡ *Faster*
• File sync is now 2× faster

🐛 *Fixed*
• Large images now upload correctly
• Scheduled posts show the right timezone

📝 Full changelog: <link>
```

## Format 4: App Store (What's New)

Max 4000 znaków, prosty język, bez technicznych detali.

```
What's New in 2.5.0:

🏢 Team Workspaces
Create separate spaces for different projects.
Invite your team and keep everything organized.

⌨️ Keyboard Shortcuts
Press ? to discover all shortcuts and navigate faster.

Plus: Faster file sync, bug fixes, and stability improvements.
```

## Zasady dobrego changeloga
1. **Pisz dla ludzi, nie maszyn** — "Fixed crash on profile page" > "fix: NPE in UserService.getProfile()"
2. **Najważniejsze na górze** — Breaking Changes > Features > Improvements > Fixes
3. **Linkuj issues/PRs** — ułatwia śledzenie
4. **Datuj wpisy** — zawsze ISO 8601 (YYYY-MM-DD)
5. **Nie mieszaj wersji** — każda wersja osobna sekcja
6. **Sekcja [Unreleased]** — zbieraj zmiany w trakcie pracy
