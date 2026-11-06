# 💬 Customer Service Chatbot

![CI](https://github.com/YOUR-USERNAME/customer-service-chatbot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An NLP customer-support chatbot for a fictional online store ("ShopEasy"). It classifies each message into one of **13 intents**, extracts entities, handles **multi-turn slot filling** (asks for an order number when it is missing), rejects out-of-scope questions with a **confidence threshold**, and hands over to a human when asked. Everything (training, evaluation, results, tests) is reproducible with three commands.

## Highlights
- **Intent classifier:** word (1-2 gram) + character (2-5 gram) TF-IDF with logistic regression. Character n-grams make it robust to typos such as "pasword".
- **Rigorous evaluation:** utterances are split into train/validation/test **before** augmentation, so no near-duplicate leaks into the test set. Three models are compared.
- **Out-of-scope handling:** a confidence threshold, tuned on validation data only, routes unknown questions to a fallback.
- **Dialogue management:** entity extraction (order ID, email), slot filling, context memory and human hand-off.
- Tests, lint, CI, CLI, Streamlit chat UI and Docker.

## Run it
```bash
git clone https://github.com/YOUR-USERNAME/customer-service-chatbot.git
cd customer-service-chatbot
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
make install        # pip install -r requirements-dev.txt
make evaluate       # retrains, evaluates, rewrites results/ and models/
make demo           # scripted conversation (output below)
make chat           # talk to the bot in the terminal
make app            # Streamlit chat UI at http://localhost:8501
make test           # 13 tests
```
A trained model is already included in `models/`, so `make chat` and `make app` work immediately.

## Execution output
Real output of `make demo` (saved in `results/demo_transcript.txt`):
```text
You: hi
Bot: Hi there! What can I help you with?
     [intent=greeting confidence=0.984]
You: where is my order
Bot: Sure, could you share your order number?
     [intent=order_status confidence=0.997]
You: #48213
Bot: Order #48213: Shipped (arrives in 2-3 days).
     [intent=order_status confidence=1.0 entities={'order_id': '48213'}]
You: i forgot my pasword
Bot: Tap 'Forgot password' on the login page and we'll email you a reset link (check spam too). ...
     [intent=password_reset confidence=0.858]
You: what is the weather today
Bot: Sorry, I didn't understand that. I can help with orders, returns, shipping, payments, ...
     [intent=fallback confidence=0.333]
You: can i talk to a person
Bot: Connecting you to a human agent now. ...
     [intent=human_agent confidence=0.997]
```
Also in `results/`: `test_output.txt` (13 passed), `lint_output.txt` (clean).

## Results
Held-out **test set: 65 utterances** (5 per intent) never used for training or tuning. Full data: 260 hand-written utterances; training set augmented from 156 to 780 examples.

| Model | Accuracy | Macro F1 | Latency / query |
|---|---|---|---|
| Naive Bayes (word TF-IDF) | 0.769 | 0.770 | 0.03 ms |
| Linear SVM (word+char) | 0.815 | 0.817 | 0.09 ms |
| **Logistic Regression (word+char)** | **0.877** | **0.879** | 0.08 ms |

![Confusion matrix](results/confusion_matrix.png)

Per-intent scores are in `results/classification_report.txt`. Weakest intents: `payment_methods` (F1 0.60) and `product_availability` (0.73), which share vocabulary such as "available" and "can I get". Several intents (change_address, human_agent, return_refund, shipping_info) reach F1 1.00.

### Out-of-scope rejection and the threshold trade-off
The threshold (0.65) was chosen on the validation split (`results/threshold_sweep.csv`), then measured on test data:

| Metric (test, threshold 0.65) | Value |
|---|---|
| Out-of-scope questions correctly rejected (15 queries) | 86.7% |
| In-scope questions answered correctly | 64.6% |
| In-scope questions wrongly sent to fallback | 32.3% |

Raising the threshold blocks more off-topic questions but also rejects more valid ones. A production system could lower it and instead ask "did you mean ...?" for mid-confidence cases.

### Honest notes on these numbers
- **Small, hand-written dataset.** 65 test utterances means each wrong answer moves accuracy by 1.5 points, so treat results as indicative, not as a production benchmark.
- **Dataset was expanded once.** The first version (14 phrasings/intent, 46 test utterances) scored 78.3% accuracy (`results/metrics_v1_initial_dataset.json`). Error analysis showed too few phrasings per intent, so I added 6 per intent and re-split. More data, not model tuning, produced the gain.
- Real customer logs would be messier (slang, multi-intent messages, other languages).
- The deployed model is retrained on all data; the metrics above come from the train-only model.

## How it works
```
user text -> normalize (lowercase, contractions, mask order IDs/emails)
          -> TF-IDF (word + char n-grams) -> logistic regression -> intent + confidence
          -> confidence < threshold ? fallback
          -> dialogue manager (slot filling, order lookup, hand-off) -> response
```
Order lookup is a **deterministic mock** (`lookup_order` in `chatbot/dialogue.py`); replace it with a call to a real order API.

## Project structure
```
customer-service-chatbot/
├── chatbot/        # nlp.py, data.py, model.py, dialogue.py, evaluate.py, cli.py
├── data/           # intents.json (add your own intents here), out_of_scope.json
├── models/         # trained model (joblib)
├── results/        # metrics, report, confusion matrix, sweep, demo transcript, test logs
├── tests/          # pytest
├── app.py          # Streamlit chat UI
└── Dockerfile  Makefile  ruff.toml  .github/workflows/ci.yml
```
**Customize:** add an intent with patterns and responses to `data/intents.json`, then run `make evaluate`.

## Future work
- Embedding-based classifier (e.g. sentence-transformers) or fine-tuned transformer, compared against this baseline
- Multi-intent messages, entity extraction with spaCy, multilingual support
- REST API (FastAPI), conversation logging, and a human-in-the-loop labelling loop

## License
MIT
