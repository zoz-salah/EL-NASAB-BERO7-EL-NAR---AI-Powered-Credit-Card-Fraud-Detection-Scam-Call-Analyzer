const API_BASE = "http://localhost:8000";

const TRANSACTION_FIELDS = ["Time", ...Array.from({ length: 28 }, (_, i) => `V${i + 1}`), "Amount"];

function buildTransactionForm() {
  const form = document.getElementById("transactionForm");
  TRANSACTION_FIELDS.forEach((field) => {
    const input = document.createElement("input");
    input.type = "number";
    input.step = "any";
    input.id = `field_${field}`;
    input.placeholder = field;
    form.appendChild(input);
  });
}

function readTransactionValues() {
  const values = {};
  for (const field of TRANSACTION_FIELDS) {
    const el = document.getElementById(`field_${field}`);
    values[field] = parseFloat(el.value) || 0;
  }
  return values;
}

function showResult(elementId, html, verdictClass) {
  const box = document.getElementById(elementId);
  box.classList.remove("hidden", "verdict-scam", "verdict-fraud", "verdict-suspicious");
  if (verdictClass) box.classList.add(verdictClass);
  box.innerHTML = html;
}

async function checkTransaction() {
  const payload = readTransactionValues();
  try {
    const res = await fetch(`${API_BASE}/predict_transaction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");

    const verdictClass = data.verdict === "Fraud" ? "verdict-fraud" : data.verdict === "Suspicious" ? "verdict-suspicious" : "";
    showResult(
      "transactionResult",
      `<strong>${data.verdict}</strong> — fraud probability: ${(data.fraud_probability * 100).toFixed(2)}%`,
      verdictClass
    );
  } catch (err) {
    showResult("transactionResult", `Error: ${err.message}`, "verdict-fraud");
  }
}

async function checkNumber() {
  const number = document.getElementById("phoneInput").value.trim();
  if (!number) return;
  try {
    const res = await fetch(`${API_BASE}/check_number`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: number }),
    });
    const data = await res.json();
    const verdictClass = data.is_spam ? "verdict-fraud" : "";
    showResult(
      "numberResult",
      `<strong>${data.is_spam ? "Spam" : "Not Spam"}</strong> — confidence: ${(data.confidence * 100).toFixed(0)}%`,
      verdictClass
    );
  } catch (err) {
    showResult("numberResult", `Error: ${err.message}`, "verdict-fraud");
  }
}

async function analyzeCall() {
  const transcript = document.getElementById("callTranscript").value.trim();
  const phone = document.getElementById("callPhoneInput").value.trim();
  if (!transcript) return;

  try {
    const res = await fetch(`${API_BASE}/analyze_call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcript, phone_number: phone || null }),
    });
    const data = await res.json();

    const verdictClass =
      data.final_verdict === "Scam" ? "verdict-scam" : data.final_verdict === "Suspicious" ? "verdict-suspicious" : "";

    const keywords = data.call_analysis.matched_keywords.join(", ") || "none";

    showResult(
      "callResult",
      `<strong>${data.final_verdict}</strong> — risk score: ${data.final_score}<br>Matched keywords: ${keywords}`,
      verdictClass
    );
  } catch (err) {
    showResult("callResult", `Error: ${err.message}`, "verdict-fraud");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  buildTransactionForm();
  document.getElementById("checkTransactionBtn").addEventListener("click", checkTransaction);
  document.getElementById("checkNumberBtn").addEventListener("click", checkNumber);
  document.getElementById("analyzeCallBtn").addEventListener("click", analyzeCall);
});
