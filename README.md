# Zakuchess

![Powered by Django](https://img.shields.io/badge/Powered_By-Django-blue)
![Formatting: Black](https://img.shields.io/badge/Formatting-Black-blue)
![Pre-commit: Enabled](https://img.shields.io/badge/Pre--commit-Enabled-blue)
![Type checking: Mypy](https://img.shields.io/badge/Type--checking-Mypy-blue)


### Chess with character(s)

A free and open-source "daily chess challenge" game, where you play against a computer opponent
with pixel art graphics.

### The stack

The following pieces of technology are used to build Zakuchess:

 - Programming language: [Python](https://www.python.org/)
 - Web framework: [Django](https://www.djangoproject.com/)
 - Database: [SQLite](https://www.sqlite.org/index.html)
 - HTML templating: [DOMinate](https://github.com/Knio/dominate#readme)
 - JavaScript-based interactions: [htmx](https://htmx.org/)
 - CSS framework: [Tailwind CSS](https://tailwindcss.com/)
 - TypeScript compilation: [esbuild](https://esbuild.github.io/)
 - Chess logic on the server: [python-chess](https://python-chess.readthedocs.io/en/latest/)
 - Chess IA in the browser: [Stockfish](https://stockfishchess.org/) (compiled in WebAssembly by the folks at [Lichess](https://github.com/lichess-org))
 - Hosting: [Fly.io](https://fly.io/)

### Running locally

Make sure you have Python 3.11 installed, as well as Node.js v18.

We recommend [pyenv](https://github.com/pyenv/pyenv-installer#readme) and [nvm](https://github.com/nvm-sh/nvm#readme) to handle specific versions of Python and Node.js,
but you can use whatever you want of course :-)

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
