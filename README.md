# Experiment 15: Unvalidated Input Demonstration

This Flask application intentionally accepts user input without validation or output escaping.
It is for a controlled secure-coding lab only.

## Run

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

## Demonstrated abuse cases

1. Username `<script>alert('XSS')</script>` executes as reflected XSS because the value is interpolated directly into HTML.
2. Quantity `-5` is accepted, producing a negative total of `Rs. -500` because no range check is applied.

This source is deliberately vulnerable and must not be deployed.
