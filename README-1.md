# Simple Web-Search Agent

## Setup
1. Install the SDK:
   ```
   pip install anthropic
   ```
2. Get an API key from https://console.anthropic.com/ and set it:
   ```
   export ANTHROPIC_API_KEY=your_key_here
   ```
   (On Windows: `set ANTHROPIC_API_KEY=your_key_here`)

## Run
```
python agent.py
```

Then chat with it in the terminal. It will automatically search the web when it needs current information (news, prices, recent events, etc.) and answer with citations built in.

## Web App Version (app.py)

If you want a browser-based chat UI instead of the terminal, plus image and video generation:

1. Install dependencies:
   ```
   pip install streamlit anthropic openai runwayml
   ```
2. Get an OpenAI API key from https://platform.openai.com/api-keys and set it:
   ```
   export OPENAI_API_KEY=your_openai_key_here
   ```
   (Separate billing from Anthropic — DALL-E 3 costs roughly $0.04–$0.08 per image.)
3. Get a Runway API key from https://dev.runwayml.com/ and set it:
   ```
   export RUNWAYML_API_SECRET=your_runway_key_here
   ```
   (Separate billing, credit-based — a 5-second video costs a handful of credits, check current pricing on their site. Generation takes 1-2 minutes, and the app will show a status message while it works.)
4. Run it:
   ```
   streamlit run app.py
   ```
5. It opens automatically in your browser at `http://localhost:8501`
6. Ask it to "generate an image of..." or "generate a video of..." and it calls the right tool, showing the result inline.

To let others use it over the internet (not just your own computer), deploy it for free at https://streamlit.io/cloud — connect your GitHub repo and it hosts it for you.

## Next steps to extend it
- Add more tools (see the `TOOLS` list) — e.g. a custom function tool for your own database or API
- Add a system prompt to give it a persona or specific instructions
- Swap the terminal loop for a web frontend (Flask/FastAPI + a simple chat UI)
- Add memory/persistence so conversations survive restarts (e.g. save `history` to a file or database)
