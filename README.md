# simone-drago.github.io

My academic website, built by `build.py` from the files in `content/` and published by GitHub Actions on every push to `main`. It produces the home page (`index.html`), a news archive (`news.html`), and one downloadable `.bib` file per paper plus one with all of them (`bib/`).

## Editing

Everything you normally touch is in `content/`:

| File | What it holds |
|---|---|
| `config.yml` | name, position, links, photo, CV PDF, section order, tinted sections, contact text, publication options |
| `bio.md` | the paragraph under your name (Markdown) |
| `research.yml` | the Research interests section: a one-line intro and one card per topic, each with an icon |
| `papers.bib` | publications (plain BibTeX; see the comment at the top for the extra fields) |
| `news.yml`, `education.yml`, `experience.yml`, `teaching.yml`, `awards.yml`, `extracurricular.yml` | one list entry per item |

Sections: `sections:` in `config.yml` sets which sections appear and in what order (the top bar follows it). To hide one, remove it from the list. To add your own, create `content/<name>.yml` (entries with `title`, and optionally `subtitle`, `date` or `start`/`end`, `location`, `details`, `url`), add `<name>` to `sections`, and give it a heading under `titles:`.

Text in the YAML files accepts Markdown (`[link](https://...)`, `**bold**`, `*italic*`). Wrap a value in quotes if it contains a colon. Entries are sorted by date automatically, so their order in the file doesn't matter.

News appears in three places: the latest `news_ticker` items (default 5) rotate under the bio, the latest `news_limit` (default 10) are listed in the News section, and `news.html` lists everything. Both numbers are in `config.yml`.

Links in `config.yml` get an icon from their URL (Google Scholar, GitHub, LinkedIn, ORCID; anything else gets a link icon). Set `icon:` on a link to choose one yourself.

Photo and CV: put them in `static/` (e.g. `static/img/photo.jpg`, `static/cv.pdf`) and set `photo:` / `cv_pdf:` in `config.yml`.

## Publications

Papers are grouped by type and then by year (`layout: category-year`), or only by year with preprints last (`layout: year`). Either way, each paper is labelled by type and numbered from the oldest: C1, C2, ... (conference), J (journal), W (workshop), P (preprint), U (under review). The page lists the newest first.

- The type comes from the entry: `@inproceedings` is a conference paper (a workshop if the booktitle contains "Workshop"), `@article` is a journal paper (a preprint if the journal is arXiv), `@misc` is a preprint. `pubtype = {workshop}` (or conference, journal, preprint) forces it.
- `status = {underreview}` puts a paper in "Under review": its venue is never shown and it has no BibTeX button. Turn the whole category off with `show_under_review: false` in `config.yml`. When the paper is accepted, delete the `status` line.
- `venue = {NeurIPS 2025}` sets the short venue name shown on the page; without it the full booktitle or journal is used.
- `equal = {1,2}` marks equal contribution (author positions, from 1).
- Links: `arxiv`, `pdf`, `code`, `openreview`, `doi`, `url`, `slides`, `poster`, `video`, `project`. Without `pdf`, the PDF link points to arXiv when the paper has an arXiv id.
- `abstract` adds a foldable Abstract; `$...$` math in it is rendered.
- Every paper (except those under review) gets a BibTeX link that downloads its citation, without the website-only fields above.
- `selected = {true}` plus `selected_only: true` in `config.yml` shows only selected papers. `hidden = {true}` keeps an entry out of the site.

Your name is highlighted in author lists using `me:` in `config.yml`.

## Preview locally

```sh
python3 -m venv .venv && source .venv/bin/activate   # once
pip install -r requirements.txt                      # once
python build.py --serve                              # then open http://localhost:8000
```

`build.py` stops with a list of problems if something is wrong (a typo in a field name, a date it can't read, a colon that broke the YAML), and warns about lines still marked TODO.

## Publishing

Push to `main`. The workflow in `.github/workflows/deploy.yml` runs `build.py` and publishes the result; it takes about a minute. If a build fails, the Actions tab shows the same error messages as running it locally.

One-time setup: repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Changing the look

Colours, fonts and spacing are tokens at the top of `static/style.css`; the light and dark palettes are defined there side by side (change `--accent` in both). The button in the top bar switches theme; visitors who never press it get their system's setting. The layout is `templates/index.html.j2`. Fonts are self-hosted (Newsreader and Hanken Grotesk, SIL Open Font License), so the site makes no requests to Google.
