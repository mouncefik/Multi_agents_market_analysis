# Installation Guide

Follow these steps to set up and run the Market Research AI System.

## Prerequisites

- **Python 3.10+**
- **Poetry** (Python dependency manager)
  - Install instructions: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/mouncefik/Multi_agents_market_analysis.git
    cd Multi_agents_market_analysis
    ```

2.  **Install dependencies:**

    ```bash
    poetry install
    ```

3.  **Set up environment variables:**

    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        # On Windows Command Prompt: copy .env.example .env
        # On PowerShell: Copy-Item .env.example .env
        ```
    -   Open `.env` in a text editor and add your API keys:
        ```ini
        OPENAI_API_KEY=sk-...
        GEMINI_API_KEY=...
        ```

## Running the Application

Start the application using Poetry:

```bash
poetry run py market_agents/app.py
```

The application will launch in your default web browser (usually at `http://127.0.0.1:7860`).
