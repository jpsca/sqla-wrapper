# Alembic wrapper

Alembic is great but it has a configuration problem. While you web application config is probably one or more python files and parameters loaded from environment variables and other sources, Alembic needs a static `alembic.ini` file. You are suppose to edit the almost-undocumented `env.py` file to customize it to your application.

The `Alembic` wrapper class aims to simplify that set up so you can just use your application config, without any more config files to maintain. The actual database migrations are still handled by Alembic so you get exactly the same functionality.


## Set up

The `Alembic()` class require two arguments: A [`SQLAlchemy()`](sqlalchemy-wrapper) instance and the path of the folder that will contain the migrations.

```python
from sqla_wrapper import Alembic, SQLAlchemy

db = SQLAlchemy(…)
alembic = Alembic(db, "db/migrations")
```

If the migrations folder doesn't exists, it will be created.


## CLI integrations

The only downside is that you can't use the `alembic` command-line tool anymore. Instead, all the usual Alembic command are be available as methods of the wrapper instance and you need to integrate them with your framework/application CLI.

Is easier than it sounds, specially because the wrapper comes with one-line methods to extend [Click](https://click.palletsprojects.com) (the CLI used by Flask by default) and [pyCEO](https://github.com/jpsca/pyceo) (arguably, the best CLI ever made).

### Integrating with Flask Click

```python
from flask import Flask

db = SQLAlchemy(…)
alembic = Alembic(…)

app = Flask(__name__)
app.cli.add_command(alembic.get_flask_cli("db"))
```

### Integrating with Click

```python
import click

db = SQLAlchemy(…)
alembic = Alembic(…)

@click.group()
def cli():
    pass

cli.add_command(alembic.get_click_cli("db"))

```

### Integrating with pyCEO

```python
from pyceo import Cli

db = SQLAlchemy(…)
alembic = Alembic(…)

class Manage(Cli):
  db = alembic.get_pyceo_cli("db")

cli = Manage()

```
