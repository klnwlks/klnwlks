# Growth Ledger

The profile embeds one cream-paper SVG. The whole card links to the portfolio; GitHub renders the SVG as an image, not an interactive document.

`python3 scripts/contributions.py` refreshes `assets/ledger.svg` with the contribution levels and rolling-year total GitHub shows anonymous profile visitors. The daily GitHub Action also accepts manual dispatch. No backend, personal token, or fonts are required for refreshes. The source is GitHub’s public calendar HTML, not a versioned API. An incomplete or changed response fails the job and preserves the previous image. The printed date shows how current the graph is.

To change the layout, install `fonttools[woff]`, install npm dependencies in the adjacent `portfolio-v3` checkout, and extract the `simple-icons@15.21.0` npm package. Run `python3 scripts/render-layout.py <path-to-simple-icons/icons>` and then the refresh command above. Commit both the template and the rendered SVG. The outlined lettering and ASCII flower come from the portfolio; tool marks come from Simple Icons.
