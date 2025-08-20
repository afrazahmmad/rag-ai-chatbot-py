import re
from datetime import datetime
import dateparser
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TreebankWordTokenizer

lemmatizer = WordNetLemmatizer()
tokenizer = TreebankWordTokenizer()

# DDS synonyms mapping
DDS_SYNONYMS = {
    # Duration
    "mtd": "month_to_date",
    "month to date": "month_to_date",
    "this month": "month_to_date",
    "current month": "month_to_date",
    "this month till today": "month_to_date",
    "ytd": "year_to_date",
    "year to date": "year_to_date",
    "this year till date": "year_to_date",
    "lm": "last_month",
    "last month": "last_month",
    "previous month": "last_month",
    "today": "today",
    "td": "today",

    # Metrics
    "deals": "sales_deals",
    "units": "sales_deals",
    "new units": "sales_deals",
    "used units": "sales_deals",
    "vehicles": "sales_deals",
    "gross": "gross_profit",
    "net": "net_profit"
}

# Example filters mapping (expandable)
FILTERS = {
    "active": "active_employees",
    "store": "store",
    "employee": "employee"
}


def normalize_query(query: str):
    """Tokenize, lemmatize, map synonyms."""
    text = query.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    tokens = tokenizer.tokenize(text)

    normalized = []
    for t in tokens:
        lemma = lemmatizer.lemmatize(t)
        normalized.append(DDS_SYNONYMS.get(lemma, lemma))

    return normalized


def parse_duration(query: str):
    """Detect MTD, YTD, LM, Today or explicit date ranges."""
    text_lower = query.lower()

    # 1️⃣ Check synonyms
    for key, val in DDS_SYNONYMS.items():
        if key in text_lower and val in ["month_to_date", "year_to_date", "last_month", "today"]:
            return {"type": val, "start_date": None, "end_date": None}

    # 2️⃣ Check explicit date range
    match = re.search(r"from (.+?) to (.+)", text_lower)
    if match:
        start_date = dateparser.parse(match.group(1), settings={'PREFER_DATES_FROM': 'past'})
        end_date = dateparser.parse(match.group(2), settings={'PREFER_DATES_FROM': 'past'})
        if start_date and end_date:
            return {"type": "custom_range", "start_date": start_date.date(), "end_date": end_date.date()}

    # 3️⃣ Check single date
    single_date = dateparser.parse(text_lower, settings={'PREFER_DATES_FROM': 'past'})
    if single_date:
        return {"type": "custom_single_day", "start_date": single_date.date(), "end_date": single_date.date()}

    return {"type": "unknown", "start_date": None, "end_date": None}


def extract_filters(query: str):
    """Detect filters like store, employee, active."""
    filters_found = {}
    for key, field in FILTERS.items():
        if key in query.lower():
            filters_found[field] = True  # Simple detection; can be improved
    return filters_found


def preprocess_user_query(query: str):
    """Final preprocessor: returns structured JSON"""
    tokens = normalize_query(query)
    duration = parse_duration(query)
    filters = extract_filters(query)

    return {
        "original_query": query,
        "tokens": tokens,
        "duration": duration,
        "filters": filters
    }


# ---- Test Cases ----
queries = [
    "How many deals MTD?",
    "How many deals we have in this month ?",
    "Show me Month to Date Gross",
    "Give YTD sales profit",
    "Last Month net deals by store",
    "Sales from 1 Aug to 19 Aug",
    "Deals on 19 Aug for active employees",
    "Who is benji ?",
    "How many units were sold in first week of last month ?",
]

for q in queries:
    result = preprocess_user_query(q)
    print(result)
