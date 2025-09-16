# Zakuchess 


## Installation

```bash
$ make install
```

This command will install [uv](https://docs.astral.sh/uv/) in the project's `bin/` folder,
then create a virtual environment in the `.venv/` folder and install the project's dependencies
in it.

So as long as your machine can run `uv`, you should be able to run the project 🤞

## Running the project on a local environment

```bash
$ make dev
```

Note that once the `make install` command has been run, you can also run the project by
sourcing the `dev-start.zsh` script and then running the Django development server, via
the shell alias `djm` (_"**DJ**ango **M**anage"_):  
(the `dev-start.zsh` script displays the shell aliases it defines)

```bash
$ source ~/_WORK/me/zakuchess/dev-start.zsh
$ djm runserver zakuchess.localhost:8000
``` 

⚠️ The `python manage.py` command should be replaced by the `djm` alias, 
as it sets the right DJANGO_SETTINGS_MODULE env var and also loads the `.env.local` file.  
You can of course still use `python manage.py` if you prefer 🙂, but you'll have to set these
manually.


### Using Watchman

If you have [Watchman](https://facebook.github.io/watchman/) installed on your machine, 
Django will automatically use it to watch for changes in your files.


## Running the test suite and code quality tools

To run Pytest:

```bash
$ make test
```

To run our various code quality tools (Ruff, MyPy...) :

```bash
$ make code-quality/all
```

## Using the Django Admin locally

This command creates a `admin@zakuchess.localhost` superuser, with the password `localdev`:

```bash
$ make django/createsuperuser
```
