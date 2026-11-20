# tinyheadlines.live

Static one-page site around the 24/7 live stream. Served by GitHub Pages from the repo
`yeikiu/tinyheadlines.live` (branch `main`, root), custom domain in `CNAME`.

The source of truth is this folder (`web/`) of the Tiny Headlines repo. To publish a change:

    git subtree split --prefix web -b web-pages
    git push https://github.com/yeikiu/tinyheadlines.live.git web-pages:main --force

The live player is the YouTube "live_stream?channel=" embed, which always points at the current broadcast.
