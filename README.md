# Gamehub

A python server for multiplayer online games.


## Running the server

Run it with UV

```bash
uv run .\server.py
```

## Running the client

There are three sample HTML files in the `client` folder. You can run them with a simple HTTP server.

```bash
python -m http.server
```

Then open the browser at one of the following URLs:

- `http://localhost:8000/clients/chinese_poker/` 
- `http://localhost:8000/clients/tic_tac_toe/`
- `http://localhost:8000/clients/rock_paper_scissors/`


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