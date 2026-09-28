"""
main.py
FastAPI backend for EL NASAB BERO7 EL NAR.

Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import load_model, predict_transaction
from nlp_analyzer import analyze_call, combine_verdicts
from number_checker import check_number

app = FastAPI(title="EL NASAB BERO7 EL NAR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model once at startup so requests stay fast
try:
    fraud_model = load_model()
except FileNotFoundError:
    fraud_model = None
    print("Warning: no trained model found yet. Run model.py to train one.")


class TransactionInput(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float


class NumberInput(BaseModel):
    phone_number: str = Field(..., examples=["+201234567890"])


class CallInput(BaseModel):
    transcript: str
    phone_number: str | None = None


@app.get("/")
def root():
    return {"status": "ok", "message": "EL NASAB BERO7 EL NAR API is running"}


@app.post("/predict_transaction")
def predict_transaction_endpoint(transaction: TransactionInput):
    if fraud_model is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run model.py first.")
    result = predict_transaction(fraud_model, transaction.model_dump())
    return result


@app.post("/check_number")
def check_number_endpoint(payload: NumberInput):
    return check_number(payload.phone_number)


@app.post("/analyze_call")
def analyze_call_endpoint(payload: CallInput):
    call_result = analyze_call(payload.transcript)

    number_result = None
    if payload.phone_number:
        number_result = check_number(payload.phone_number)

    return combine_verdicts(call_result, number_result)
