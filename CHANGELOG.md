# Changelog

## 1.0.1 — 2026-10-27

- Resolve short and embedded video links to the full watch page so metadata and related videos are available.
- Return the correct profile, channel and pornstar types when resolving author links.
- Keep channel authors out of categories and tags, and parse abbreviated rating counts safely.
- Expose Sort and SortDate and support normal get_author() and get_pornstars() calls.
- Include the HTML fixtures used by the parser regression tests.
- Use the published `eaf-base-api>=4.2.5` dependency.

