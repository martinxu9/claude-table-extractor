# Table Extractor Powered By Claude Tool Use and Reflex

## Prerequisites

First you need to have an Anthropic API key. Get yours by signing up at [Anthropic](https://anthropic.com/).

## Requirements

The following packages are required to run the code:

```text
reflex==0.4.6
anthropic
Pillow
```

## How It Works

Follow the [Claude API Tool Use docs](https://docs.anthropic.com/claude/docs/tool-use) and define a `extract_table` function that takes an image file and return an extract table as a list of lists.

## How to Run the App

Export this as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_api_key
```

This app is based on [Reflex](https://github.com/reflex-dev/reflex) framework. In the top level directory (this directory has a file named `rxconfig.py`), run the following commands to run the app:

```bash
reflex init
reflex run
```

Also check out [Reflex Documentation](https://reflex.dev/docs/getting-started/introduction/) to build/run/host your own app.

## Limitations

1. Right now, only support certain image types supported by Anthropic messaging API, no PDFs.
2. Only the first table in the image is returned. Experimented with multiple tables and the results were not as good.
3. The return table is a plain text representation. Best returned result is a json encoded string of the table, so less post processing code.
