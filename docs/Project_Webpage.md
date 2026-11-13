# Attendly project webpage

The public project webpage is built with plain HTML, CSS, and JavaScript. No Node install or React build is required. It introduces the working Python application and provides a clearly labeled browser-only sample attendance walkthrough.

## Source

`static/project/` contains `index.html`, `style.css`, `script.js`, `mark.svg`, and `.nojekyll`.

The Python server serves these files publicly at `/static/project/index.html`. Signed-out visitors to `/` are directed to this webpage. **Launch Attendly** opens `/login`; after administrator sign-in, `/` displays the attendance workspace with its existing authentication.

## GitHub Pages

The `gh-pages` branch contains the published static files at its root, ready for GitHub Pages. To enable hosting once:

1. Open this repository's **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Select **gh-pages** and **/(root)**, then **Save**.
4. Wait for GitHub's Pages deployment to complete. Open the exact URL shown in Settings; a source-code commit alone does not confirm hosting is active.

The Python server and recognition model continue to run on Render. GitHub Pages hosts the project webpage and its sample simulation. Neither the walkthrough nor this public page stores real attendance or accesses a camera.

When editing the webpage, update `static/project/` on `main` and publish the same five files to `gh-pages`. Do not copy the backend, environment files, databases, or credentials into the static branch.

## Walkthrough behavior

- Three fictional sample students; no network calls and no browser storage.
- Simulated check-in, duplicate prevention, unknown-visitor rejection, and manual attendance with a verification note.
- Downloadable sample CSV, including formula escaping for the note field.
- Reset clears the sample state, including any pending simulated check-in.
- Native keyboard-accessible controls, modal dialog, live result messages, and reduced-motion styles.

The page links to the existing application's login and source documentation. The current Render application uses temporary SQLite storage; the webpage discloses that limitation and does not claim persistent TiDB is connected.
