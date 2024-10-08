# [Zakuchess](https://zakuchess.com)

![Powered by Django](https://img.shields.io/badge/Powered_By-Django-green)
![Formatting: Black](https://img.shields.io/badge/Formatting-Black-blue)
![Pre-commit: Enabled](https://img.shields.io/badge/Pre--commit-Enabled-blue)
![Type checking: Mypy](https://img.shields.io/badge/Type--checking-Mypy-blue)


### Chess with character(s)

A free and open-source "daily chess challenge" game, where you play against a computer opponent
with pixel art units.

No analytics, no tracking, no ads - it was built purely for fun, and to check how far I could go with 
a reactive User Interface powered by [htmx](https://htmx.org/) 🙂

The game lives at [zakuchess.com](https://zakuchess.com).

![The starting screen of a new ZakuChess daily challenge](./src/apps/daily_challenge/static/daily_challenge/img/og-image-1200x630.png)

### The stack

 - Programming language: [Python](https://www.python.org/)
 - Web framework: [Django](https://www.djangoproject.com/)
 - Database: [SQLite](https://www.sqlite.org/index.html)
 - Live user interface: [htmx](https://htmx.org/)
 - HTML templating: [DOMinate](https://github.com/Knio/dominate#readme)
 - CSS framework: [Tailwind CSS](https://tailwindcss.com/)
 - TypeScript compilation: [esbuild](https://esbuild.github.io/)
 - Units art: [The Battle for Wesnoth](https://www.wesnoth.org/) :shield:
 - Chess logic on the server: [python-chess](https://python-chess.readthedocs.io/en/latest/)
 - Chess logic in the browser: [Stockfish](https://stockfishchess.org/) 
(compiled in WebAssembly by the wonderful folks at [Lichess](https://github.com/lichess-org) 💙)
 - Talking of Lichess... Most of the daily challenges are adaptations of games from 
    [their open source database of chess games and puzzles](https://database.lichess.org/),
    so let's double that heart: 💙💙
 - Tests suite: [pytest](https://docs.pytest.org/en/latest/)
 - Hosting: [Fly.io](https://fly.io/)

### Running locally

 - Python: Entirely managed by [uv](https://docs.astral.sh/uv/). The `make install` command will
    make sure that the right version of `uv` is installed in the "bin/" folder - which is not ignored by git.
 - Node.js: Make sure you have Node.js v18 installed.  
     We recommend [nvm](https://github.com/nvm-sh/nvm#readme) to handle specific versions of Python and Node.js,
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

The roadmap now lives in a GitHub project:  
> https://github.com/users/olivierphi/projects/1/views/1

### Contributing

Improvements and bugfixes are welcome, but also new "daily challenges"!

When playing chess online with other people, if you find yourself in a position that you think 
could be interesting for others to try to solve ♞, please feel free to open an issue to discuss its
addition to the daily challenges database. 🙂

### License

This project is licensed under the GNU General Public License v3 - see the [LICENSE](./LICENSE) file for details.
