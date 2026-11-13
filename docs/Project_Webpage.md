# Attendly project webpage

The public project webpage is built with plain HTML, CSS, and JavaScript. No Node install or React build is required. It introduces the working Python application and provides a clearly labeled browser-only sample attendance walkthrough.

## Live URLs

- GitHub Pages: https://sudip09-sys.github.io/Final_Project/
- Render-hosted entry page: https://attendly-sudip.onrender.com/
- Administrator application: https://attendly-sudip.onrender.com/login

GitHub Pages deployment completed successfully; hosting is enabled on the `gh-pages` branch.

## Source

`static/project/` contains the HTML page, base layout CSS, attendance walkthrough JavaScript, portfolio presentation CSS/JavaScript, favicon, and locally hosted fonts with their licenses.

## Portfolio visual system

The homepage follows [Sudip Sah's portfolio](https://sudip09-sys.github.io/Portfolio/): near-black background, red ember canvas, red accents, bold condensed headings, outlined display text, and monospaced labels. The original Attendly content and walkthrough remain available.

Light/dark mode and pause/resume motion controls work independently of attendance. Operating-system reduced-motion preferences take priority, decorative animation stops in hidden tabs, and particle count is capped for smaller screens. Theme and motion choices are optional local browser preferences; sample attendance is never persisted.

The local font subsets use Barlow Condensed, DM Sans and IBM Plex Mono, with Attendly family aliases and included Open Font Licenses. They load from the same origin on GitHub Pages and Render.

The Python server serves these files publicly at `/static/project/index.html`. Signed-out visitors to `/` are directed to this webpage. **Launch Attendly** opens `/login`; after administrator sign-in, `/` displays the attendance workspace with its existing authentication.

## GitHub Pages

The `gh-pages` branch contains the published static files at its root, ready for GitHub Pages. To enable hosting once:

1. Open this repository's **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Select **gh-pages** and **/(root)**, then **Save**.
4. Wait for GitHub's Pages deployment to complete. Open the exact URL shown in Settings; a source-code commit alone does not confirm hosting is active.

The Python server and recognition model continue to run on Render. GitHub Pages hosts the project webpage and its sample simulation. Neither the walkthrough nor this public page stores real attendance or accesses a camera.

When editing the webpage, update `static/project/` on `main` and publish that directory's contents, including its fonts subdirectory, to the root of `gh-pages`. Do not copy the backend, environment files, databases, or credentials into the static branch.

## Walkthrough behavior

- Three fictional sample students; attendance uses no network calls and no browser storage. Only theme and motion preferences may be remembered locally.
- Simulated check-in, duplicate prevention, unknown-visitor rejection, and manual attendance with a verification note.
- Downloadable sample CSV, including formula escaping for the note field.
- Reset clears the sample state, including any pending simulated check-in.
- Native keyboard-accessible controls, modal dialog, live result messages, and reduced-motion styles.

The page links to the existing application's login and source documentation. The current Render application uses temporary SQLite storage; the webpage discloses that limitation and does not claim persistent TiDB is connected.
