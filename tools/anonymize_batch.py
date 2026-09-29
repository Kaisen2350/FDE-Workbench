#!/usr/bin/env python3
"""
tools/anonymize_batch.py
-----------------------
Question-driven data minimization utility for operator export batches.

Features:
- HMAC-SHA256 with a local persistent secret salt (defeats low-entropy rainbow tables on RUC/cédulas).
- Exact column policy mapping (avoids over-matching bugs like 'ci' in 'precio').
- Numeric range-bucketing to preserve economic analysis variables without exposing exact pricing.
- Robust encoding fallback (UTF-8-SIG, UTF-8, Latin-1, Windows-1252) and delimiter detection.
- Optional date coarsening to mitigate small-sample quasi-identifier re-identification.

Usage:
    python tools/anonymize_batch.py <input.csv> <output.csv>
"""

import csv
import hashlib
import hmac
import os
import secrets
import sys
from typing import Callable, Dict, Tuple

SALT_FILE = ".operator_secret.salt"

def get_or_create_salt() -> bytes:
    """Retrieve or generate a 32-byte secret salt on the local machine."""
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            salt = f.read().strip()
            if len(salt) >= 16:
                return salt
    salt = secrets.token_bytes(32)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    print(f"[SECURITY] Generated new operator salt: {SALT_FILE}")
    print("           DO NOT SHARE THIS FILE. Keep it to preserve linkability across batches.")
    return salt

def hmac_pseudonym(value: str, salt: bytes) -> str:
    """Produce a cryptographically salted pseudonym preserving linkability without rainbow-table exposure."""
    if not value or not str(value).strip():
        return ""
    clean = str(value).strip().encode("utf-8", errors="replace")
    digest = hmac.new(salt, clean, hashlib.sha256).hexdigest()
    return f"ID_{digest[:12]}"

def bucket_numeric(value: str, step: float = 1000.0) -> str:
    """Bucket numeric quantities into ranges (e.g., 10000-11000) preserving distribution variance."""
    if not value or not str(value).strip():
        return ""
    raw = str(value).strip()
    # Normalize Latin comma decimal format: '42.350,00' -> '42350.00'
    cleaned = raw.replace(" ", "").replace("$", "").replace("US", "").replace("USD", "")
    if "." in cleaned and "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned and "." not in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        val = float(cleaned)
        low = int(val // step) * int(step)
        high = low + int(step)
        return f"{low:d}-{high:d}"
    except (ValueError, TypeError):
        return "[REDACTED_NUM]"

def coarsen_date(value: str) -> str:
    """Coarsen dates to YYYY-MM to reduce small-sample quasi-identifier linkability."""
    if not value or not str(value).strip():
        return ""
    s = str(value).strip()
    # Handle DD/MM/YYYY or YYYY-MM-DD
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}"  # YYYY-MM
    elif "-" in s:
        parts = s.split("-")
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1]}"  # YYYY-MM
    return s

def redact(value: str) -> str:
    """Completely suppress sensitive values where linkability is not required."""
    return "[REDACTED]" if value and str(value).strip() else ""

# Exact column policies (case-insensitive normalized matching)
DEFAULT_POLICIES: Dict[str, Tuple[str, Callable]] = {
    # Pseudonymized linkable identifiers
    "ruc_exportador": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "ruc_transportista": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "chofer_cedula": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "ci_chofer": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "cedula": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "matricula_camion": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "placa": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    "chapa": ("HMAC", lambda v, s: hmac_pseudonym(v, s)),
    
    # Range-bucketed economic variables
    "valor_flete_usd": ("BUCKET", lambda v, s: bucket_numeric(v, 250.0)),
    "flete_usd": ("BUCKET", lambda v, s: bucket_numeric(v, 250.0)),
    "costo_demora": ("BUCKET", lambda v, s: bucket_numeric(v, 100.0)),
    "valor_mercaderia": ("BUCKET", lambda v, s: bucket_numeric(v, 5000.0)),
    
    # Coarsened quasi-identifiers
    "fecha_embarque": ("COARSEN", lambda v, s: coarsen_date(v)),
    "fecha_despacho": ("COARSEN", lambda v, s: coarsen_date(v)),
    
    # Absolute redactions
    "nombre_chofer": ("REDACT", lambda v, s: redact(v)),
    "telefono": ("REDACT", lambda v, s: redact(v)),
    "observaciones_conductor": ("REDACT", lambda v, s: redact(v)),
}

def detect_delimiter(sample_text: str) -> str:
    """Determine whether file uses semicolon or comma delimiter."""
    if sample_text.count(";") > sample_text.count(","):
        return ";"
    return ","

def read_with_encoding_fallback(path: str) -> Tuple[str, str]:
    """Try common enterprise export encodings in order of likelihood."""
    for enc in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read()
                return content, enc
        except (UnicodeDecodeError, LookupError):
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(), "utf-8-replace"

def anonymize_file(in_path: str, out_path: str, delimiter: str = None) -> int:
    """Process an enterprise export file applying exact column policies."""
    salt = get_or_create_salt()
    content, enc = read_with_encoding_fallback(in_path)
    
    delim = delimiter or detect_delimiter(content[:2048])
    lines = [line for line in content.splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"Input file {in_path} is empty.")
    
    reader = csv.DictReader(lines, delimiter=delim)
    if not reader.fieldnames:
        raise ValueError(f"Could not parse CSV headers with delimiter '{delim}'")
    
    # Build normalized header lookup
    header_map = {fn.strip().lower(): fn for fn in reader.fieldnames}
    
    matched_policies = {}
    for col_key, policy in DEFAULT_POLICIES.items():
        if col_key in header_map:
            matched_policies[header_map[col_key]] = policy
    
    rows_processed = 0
    with open(out_path, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames, delimiter=delim)
        writer.writeheader()
        
        for row in reader:
            for col_name, (policy_type, transform) in matched_policies.items():
                if col_name in row and row[col_name]:
                    row[col_name] = transform(row[col_name], salt)
            writer.writerow(row)
            rows_processed += 1
            
    print(f"[SUCCESS] Processed {rows_processed} rows from {in_path} (encoding={enc}, delimiter='{delim}')")
    print(f"          Output saved to {out_path}")
    print(f"          Matched policies: {list(matched_policies.keys())}")
    return rows_processed

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/anonymize_batch.py <input.csv> <output.csv> [delimiter]")
        sys.exit(1)
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    custom_delim = sys.argv[3] if len(sys.argv) > 3 else None
    anonymize_file(in_file, out_file, custom_delim)
