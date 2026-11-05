# Empório da Música Customer Service Agent

A Python terminal prototype for customer service at Empório da Música. The agent, Tom, answers product and store-policy questions using the supplied catalog and policy manual. It uses Gemini to interpret customer messages and pandas to query the catalog.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`. The `.env` file is ignored by Git.
4. Run `python scr/cli.py` from the project root. Type `sair` to end the conversation.

## Current implementation

- `scr/cli.py` manages the terminal conversation and numbered product selection.
- `scr/catalog.py` reads the CSV files and filters active products and stock.
- `scr/product_intent.py` extracts specific product names or category and maximum-price filters.
- `scr/agent.py` coordinates product and policy answers and handles questions requiring clarification.
- `scr/llm.py` defines the LLM interface and its Gemini implementation, with a recoverable error for API failures.
- `scr/policies.py` contains opening-hours, payment, and return answers based on the supplied policy manual. `scr/policy_intent.py` identifies the topic and requested detail, so the terminal can answer a PIX, Saturday, or online-return question without returning the full policy text.
- `scr/support_intent.py` classifies remaining messages to request missing details, explain unsupported accessory questions, or redirect out-of-scope questions to store topics.

The terminal currently handles the challenge's question-analysis stage: products, prices, availability, hours, payments, returns, ambiguous questions, and out-of-scope questions. Conversation follow-up and closure are later steps. Each customer message may require several Gemini calls, so replies can be slow; a temporary API failure produces a retry message and leaves the terminal running.

## Policy interpretation decision

The store policy manual has two descriptions of credit-card installment minimums. Its payment summary table states a BRL 100.00 minimum installment, while section **3.1, Installment Rules**, gives different conditions according to the number of installments. We use the **detailed rules in section 3.1** as the source of truth because the summary table does not distinguish installment counts:

- Up to 3 installments: interest-free. We interpret the manual's exception for amounts below BRL 50.00 as a BRL 50.00 minimum installment.
- 4 to 6 installments: interest-free, with a BRL 80.00 minimum installment.
- 7 to 12 installments: interest-free, with a BRL 100.00 minimum installment.

This is a documented interpretation of the supplied manual, not an implemented installment calculator. The payment policy text is available in `scr/policies.py` and customer questions are routed to the relevant answer.
