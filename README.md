# Gamehub

A python server for multiplayer online games.


## Running the server

Run it with UV

```bash
uv run task serve
```

## Running the sample clients

There are three sample HTML files in the `clients` folder. You can run them with a simple HTTP server.

```bash
python -m http.server
```

Then open the browser at one of the following URLs:

- `http://localhost:8000/clients/chinese_poker/` 
- `http://localhost:8000/clients/tic_tac_toe/`
- `http://localhost:8000/clients/rock_paper_scissors/`


## Chinese poker client

There is a much more advanced Chinese Poker client project at the [gamehub-front](https://github.com/Tomas-Tamantini/gamehub-front) project. It is also hosted with github pages [here](https://tomas-tamantini.github.io/gamehub-front/).

## Running the tests

The project was built with TDD, so it has pretty good test coverage. Run the tests with:

```bash
uv run task tests
```

## Formatting

The project uses `ruff` for code formatting. Run it with:

```bash
uv run task format
```