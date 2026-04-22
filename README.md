# JokeBot

A command-line joke generator built with [LangGraph](https://langchain-ai.github.io/langgraph/) that fetches random jokes using the `pyjokes` library.

## Features

- **Random Jokes** — Fetch jokes with a single key press
- **Category Selection** — Choose from neutral, Chuck Norris, or all categories
- **Multi-language Support** — Currently set to English (`en`)
- **Interactive Menu** — Simple text-based interface using LangGraph state management

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the bot:

```bash
python app.py
```

### Controls

| Key | Action |
|-----|--------|
| `n` | Get the next joke |
| `c` | Change joke category |
| `l` | Change language |
| `r` | Reset joke history |
| `q` | Quit the bot |

### Categories

- `0` — Neutral
- `1` — Chuck Norris
- `2` — All

### Languages

- `0` — English (`en`)
- `1` — Spanish (`es`)
- `2` — German (`de`)

## Project Structure

```
JokeBot/
├── app.py          # Main application with LangGraph workflow
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## Dependencies

- **langgraph** — State graph workflow
- **pyjokes** — Joke generation
- **pydantic** — Data validation

## License

MIT