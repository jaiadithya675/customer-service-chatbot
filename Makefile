.PHONY: install evaluate demo chat test lint app
install:
	pip install -r requirements-dev.txt
evaluate:
	python -m chatbot.cli evaluate
demo:
	python -m chatbot.cli demo
chat:
	python -m chatbot.cli chat
test:
	python -m pytest -v
lint:
	ruff check .
app:
	streamlit run app.py
