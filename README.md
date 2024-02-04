# Zakuchess

![Powered by Django](https://img.shields.io/badge/Powered_By-Django-green)
![Formatting: Black](https://img.shields.io/badge/Formatting-Black-blue)
![Pre-commit: Enabled](https://img.shields.io/badge/Pre--commit-Enabled-blue)
![Type checking: Mypy](https://img.shields.io/badge/Type--checking-Mypy-blue)


### Chess with character(s)

A free and open-source "daily chess challenge" game, where you play against a computer opponent
with pixel art graphics.

### The stack

The amazing following projects are the main ones powering Zakuchess:

 - Programming language: [Python](https://www.python.org/)
 - Web framework: [Django](https://www.djangoproject.com/)
 - Database: [SQLite](https://www.sqlite.org/index.html)
 - Live user interface: [htmx](https://htmx.org/)
 - HTML templating: [DOMinate](https://github.com/Knio/dominate#readme)
 - CSS framework: [Tailwind CSS](https://tailwindcss.com/)
 - TypeScript compilation: [esbuild](https://esbuild.github.io/)
 - Units art: [The Battle for Wesnoth](https://www.wesnoth.org/) :shield:
 - Chess logic on the server: [python-chess](https://python-chess.readthedocs.io/en/latest/)
 - Chess logic in the browser: [Stockfish](https://stockfishchess.org/) (compiled in WebAssembly by the folks at [Lichess](https://github.com/lichess-org))
 - Tests suite: [pytest](https://docs.pytest.org/en/latest/)
 - Hosting: [Fly.io](https://fly.io/)

### Running locally

Make sure you have Python 3.11 installed, as well as Node.js v18.

We recommend [pyenv](https://github.com/pyenv/pyenv-installer#readme) and [nvm](https://github.com/nvm-sh/nvm#readme) to handle specific versions of Python and Node.js,
but you can of course use whatever you want :-)

```bash
$ python -V
Python 3.11.x # <-- check that you get this output 🙂
$ node -v
v18.x.x # ditto
```

Once you have these two installed, you can clone the repository and install the dependencies:

```bash
$ make install
$ make dev
```

You can take a look at [the Makefile](./Makefile) to see more commands.

### Roadmap

##### Before launch

 - [x] Game preview and FEN editing in the Django Admin
 - [x] Being able to import games from the Lichess puzzles database, ready to be editorliased in our Django Admin
 - [x] Validate input data, using good ol' Django path converters 
 - [x] Users' personal stats (current streak, etc)
 - [x] "End of game" screen
 - [x] "Help" screen, opened automatically on the very 1st visit
 - [x] Server stats _(without any user tracking, of course)_
 - [x] Make the session cookie shorter, by using [msgspec](https://jcristharif.com/msgspec/index.html)
 - [x] opengraph metatags, so we have a nice preview of the UI when sharing the URL

Bugs:
 - [x] Fix bubble speech when it's at the top of the chess board 
 - [x] Fix bubble speech priority (win/lose should always have priority over the rest for example)
 - [x] Fix unit names display (missing space between names)
 - [x] Fix remaining turns display when in "danger" zone (HTML shouldn't be escaped)
 - [x] Fix bug that allows the player to select/de-select a piece during the bot's turn, which can cancel the delayed bot move


##### Post launch

 - [ ] More testing! (the "Pytest + Playwright" combo should be our friend here)
 - [ ] Translate the user interface for other languages
 - [ ] Allow seasoned chess players to play more difficult challenges
 - [ ] Score sharing
 - [ ] The UI should allow "replays" - whether it's for the current game or someone else's
