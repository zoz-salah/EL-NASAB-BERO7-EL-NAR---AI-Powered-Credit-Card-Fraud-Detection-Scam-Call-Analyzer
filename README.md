
# EL NASAB BERO7 EL NAR 🔥

AI-powered credit card fraud detection and scam call analysis platform.

**El Nasab Bero7 El Nar** combines three security-focused tools into one web application:

1. **Credit Card Fraud Detection** — A machine learning model trained on the Kaggle Credit Card Fraud Detection dataset.
2. **Phone Number Spam Checker** — Checks whether a phone number is potentially associated with spam.
3. **Scam Call Analyzer** — Analyzes call transcripts using keyword and contextual scoring, optionally combined with the phone number checker.

The project is built with a **FastAPI backend** and a lightweight **HTML/CSS/JavaScript frontend**.

---

## 🎥 Demo Preview

### Main Application

![El Nasab Bero7 El Nar Demo](screenshots/demo.png)

> The demo preview shows the main interface and the project's fraud detection, phone number checking, and scam call analysis features.

---

## ✨ Features

### 💳 Credit Card Fraud Detection

- Machine learning-based transaction fraud detection.
- Compares:
  - Logistic Regression
  - Random Forest
  - XGBoost
- Uses **AUC-PR** as the primary evaluation metric because of the severe class imbalance.
- Uses **SMOTE** on the training data to handle minority-class imbalance.
- Uses `class_weight='balanced'` for Logistic Regression and Random Forest.
- Returns a fraud probability and classification verdict.
- Uses configurable probability thresholds for:
  - Fraud
  - Suspicious
  - Legitimate

### 📞 Phone Number Spam Checker

- Checks phone numbers against a local demo blocklist.
- Supports integration with an external spam-lookup provider through an API key.
- Designed as a modular component so the lookup provider can be replaced.

### 🚨 Scam Call Analyzer

- Analyzes call transcripts using keyword and weighted contextual scoring.
- Produces an interpretable scam verdict.
- Can optionally combine transcript analysis with the phone number checker.
- Uses a lightweight rule-based approach instead of a heavy NLP model.

---

## 🏗️ Project Structure

```text
el-nasab-bero7-el-nar/
│
├── backend/
│   ├── main.py                  # FastAPI app and routes
│   ├── model.py                 # Training + loading the fraud model
│   ├── nlp_analyzer.py          # Scam call text analysis
│   ├── number_checker.py        # Phone number spam lookup
│   ├── requirements.txt
│   ├── data/
│   │   └── creditcard.csv
│   └── models/
│       └── xgboost_model.pkl    # Created after training
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── notebooks/
│   └── eda_and_training.ipynb
│
├── screenshots/
│   └── demo.png
│
└── README.md
````

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd el-nasab-bero7-el-nar
```

### 2. Create a virtual environment

```bash
cd backend

python -m venv venv
```

Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📊 Dataset

Download the **Credit Card Fraud Detection** dataset from Kaggle:

[Credit Card Fraud Detection Dataset](https://www.kaggle.com/mlg-ulb/creditcardfraud)

Place the downloaded file here:

```text
backend/data/creditcard.csv
```

---

## 🤖 Train the Fraud Detection Model

Run:

```bash
python model.py
```

The training pipeline compares:

* Logistic Regression
* Random Forest
* XGBoost

The models are evaluated using **AUC-PR**, and the best-performing model is saved as:

```text
backend/models/xgboost_model.pkl
```

---

## 🚀 Run the API

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Open:

```text
frontend/index.html
```

in your browser, or serve the frontend using any static file server.

The frontend communicates with the FastAPI backend running on:

```text
http://localhost:8000
```

---

## 📱 Phone Spam API

The phone number checker works in **demo mode** with a small local blocklist when no API key is provided.

To use an external spam-lookup provider, set:

```bash
export SPAM_API_KEY=your_key_here
```

Then update:

```text
SPAM_API_URL
```

inside:

```text
backend/number_checker.py
```

to match the provider's endpoint and response format.

> Truecaller public self-serve API. Other spam-lookup providers can be integrated as a drop-in replacement.

---

# 📈 Why AUC-PR Instead of Accuracy?

This is one of the most important parts of the project.

The dataset contains roughly **577 genuine transactions for every fraudulent transaction**.

Because of this extreme class imbalance, a model could predict **"Not Fraud" for every transaction** and still achieve approximately:

**99.83% accuracy**

while detecting **zero fraudulent transactions**.

Therefore, accuracy alone is not a meaningful metric for this problem.

### Why AUC-PR?

**AUC-PR (Area Under the Precision-Recall Curve)** focuses on the performance of the minority/positive class.

* **Precision** → Of all transactions flagged as fraud, how many were actually fraudulent?
* **Recall** → Of all actual fraudulent transactions, how many did the model detect?

This makes AUC-PR more informative for highly imbalanced fraud detection problems.

### AUC-PR vs AUC-ROC

ROC curves use the False Positive Rate, which can appear deceptively low when the number of legitimate transactions is extremely large.

Precision-Recall curves focus directly on the positive class and therefore provide a more informative view of fraud detection performance in this dataset.

---

## ⚖️ Handling Class Imbalance

The project uses multiple techniques to address the severe imbalance between legitimate and fraudulent transactions.

### SMOTE

**SMOTE (Synthetic Minority Oversampling Technique)** is applied only to the training split.

It generates synthetic fraud examples by interpolating between existing minority-class samples.

The test set remains untouched and imbalanced so that evaluation better represents the original data distribution.

### Balanced Class Weights

Logistic Regression and Random Forest use:

```python
class_weight="balanced"
```

This increases the penalty for incorrectly classifying minority-class examples.

### Model Evaluation

Models are compared using:

* AUC-PR
* Precision
* Recall
* Confusion Matrix

Accuracy is not used as the primary model-selection metric.

---

## 🎯 Threshold Selection

The probability threshold used to classify a transaction is an important part of the system.

The current thresholds in `model.py` are:

```text
≥ 0.8  → Fraud
≥ 0.3  → Suspicious
< 0.3  → Legitimate
```

These thresholds are not universal.

In a real-world fraud detection system, the threshold would need to be tuned according to the business cost of:

* False positives → legitimate customers being flagged
* False negatives → fraudulent transactions being missed

The appropriate threshold should therefore be selected using the precision-recall trade-off and the specific business requirements.

---

# 🔌 API Reference

| Endpoint               | Method | Purpose                                                  |
| ---------------------- | ------ | -------------------------------------------------------- |
| `/predict_transaction` | `POST` | Returns fraud probability and transaction verdict        |
| `/check_number`        | `POST` | Checks whether a phone number is potentially spam        |
| `/analyze_call`        | `POST` | Analyzes a call transcript for potential scam indicators |

---

# 🧠 Technical Approach

```text
                    ┌─────────────────────┐
                    │     Frontend        │
                    │ HTML / CSS / JS     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI API      │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ Fraud Model │   │    Phone    │   │ Scam Call   │
      │ XGBoost     │   │   Checker   │   │  Analyzer   │
      └─────────────┘   └─────────────┘   └─────────────┘
             │                 │                 │
             ▼                 ▼                 ▼
       Fraud Score       Spam Verdict       Scam Verdict
```

---

# 🛠️ Technologies

### Backend

* Python
* FastAPI
* Uvicorn

### Machine Learning

* Scikit-learn
* XGBoost
* SMOTE
* Pandas
* NumPy

### Data Analysis

* Jupyter Notebook
* Exploratory Data Analysis
* Precision-Recall Analysis
* Confusion Matrix

### Frontend

* HTML
* CSS
* JavaScript

---

# 📌 Project Notes

* The code is intentionally written at an **intermediate level** to keep the project readable, modular, and easy to understand.
* The scam call analyzer uses **keyword-based and weighted contextual scoring** rather than a heavy NLP model because it is fast, interpretable, and does not require a training dataset.
* The phone number checker can operate in demo mode without an external API.
* The fraud detection model is trained on the Kaggle Credit Card Fraud Detection dataset.
* This project is intended for **learning and demonstration purposes**.

> ⚠️ **Disclaimer:** This is not a production-ready fraud detection or scam prevention system. Do not connect it directly to real payment infrastructure or use its predictions as the sole basis for financial or security decisions.

---

## 👨‍💻 Author

**Zoz Salah**

Built as an AI/ML learning project exploring:

* Fraud Detection
* Imbalanced Classification
* Machine Learning Model Evaluation
* NLP / Text Analysis
* FastAPI
* AI-powered Security Applications

````