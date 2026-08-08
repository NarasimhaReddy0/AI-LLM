@echo off
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate

echo Installing project dependencies...
pip install -r 01-text-to-sql\requirements.txt
pip install -r 02-rag-question-answering\requirements.txt
pip install -r 03-prompt-chaining-summarization\requirements.txt

echo.
echo Setup complete.
echo Add your OPENAI_API_KEY to each project's .env file.
pause
