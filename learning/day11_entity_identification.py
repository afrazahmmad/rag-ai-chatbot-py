import re

# DDS Synonyms mapping
METRIC_SYNONYMS = {
    "deals": ["deal", "deals", "sales", "units", "vehicles","cars"],
    "gross": ["gross", "gross profit","sales profit"],
    "profit": ["profit", "net", "earning"],
}

DURATION_SYNONYMS = {
    "today": ["today", "current date", "current day", "today’s"],
    "mtd": ["mtd", "month to date", "this month", "current month", "iss mahine"],
    "ytd": ["ytd", "year to date", "this year", "current year", "iss saal"],
    "lm": ["last month", "lm", "previous month"],
    "ltd": ["last month till date", "lmtd"],
    "lytd": ["last year till date", "lytd", "pichle saal till date"],
    "compare_mtd": ["compare mtd", "mtd vs lmtd"],
    "compare_ytd": ["compare ytd", "ytd vs lytd"],
    "same_month": ["same month", "this month last year", "compare same month"],
}


# Sample employees/stores
FILTERS = {
    "employees": ["ali", "ahmad", "sara", "usman"],
    "stores": ["lahore", "karachi", "islamabad","store"]
}


def normalize(text: str) -> str:
    """Lowercase and remove extra spaces/punctuation"""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]"," ",text)
    return re.sub(r"\s+", " ", text).strip()


def match_synonyms(text, synonyms_map):
    """Find best matching key from synonyms"""
    for key, synonyms in synonyms_map.items():
        for s in synonyms:
            if s in text:
                return key
    return None


def extract_entities(query: str):
    text = normalize(query)

    metric = match_synonyms(text, METRIC_SYNONYMS)
    duration = match_synonyms(text, DURATION_SYNONYMS)

    # Find filter (employee or store)
    employee = None
    for emp in FILTERS["employees"]:
        if emp in text:
            employee = emp
            break

    store = None
    for st in FILTERS["stores"]:
        if st in text:
            store = st
            break

    return {
        "metric": metric,
        "duration": duration,
        "employee": employee,
        "store": store,
    }


# ✅ Validation Layer
def validate_entities(entities):
    errors = []
    validated = {}

    # Validate metric
    valid_metrics = list(METRIC_SYNONYMS.keys())
    if entities.get("metric") in valid_metrics:
        validated["metric"] = entities["metric"]
    else:
        errors.append(f"Invalid or missing metric: {entities.get('metric')}")

    # Validate duration
    valid_durations = list(DURATION_SYNONYMS.keys())
    if entities.get("duration") in valid_durations:
        validated["duration"] = entities["duration"]
    else:
        errors.append(f"Invalid or missing duration: {entities.get('duration')}")

    # Validate employee
    if entities.get("employee"):
        if entities["employee"] in FILTERS["employees"]:
            validated["employee"] = entities["employee"]
        else:
            errors.append(f"Employee not found: {entities['employee']}")

    # Validate store
    if entities.get("store"):
        if entities["store"] in FILTERS["stores"]:
            validated["store"] = entities["store"]
        else:
            errors.append(f"Store not found: {entities['store']}")

    return {"validated": validated, "errors": errors}

def validate_entities_2(entities,entities_to_validate):
    errors = []
    validated = {}
    for entity in entities_to_validate:
        if entity == 'metric':
            valid_metrics = METRIC_SYNONYMS.keys()
        elif entity == 'duration':
            valid_metrics = DURATION_SYNONYMS.keys()
        elif entity == 'store':
            valid_metrics = DURATION_SYNONYMS.keys()
        else:
            valid_metrics = METRIC_SYNONYMS.keys()

        if entities.get(entity) in valid_metrics:
            validated[entity] = entities.get(entity)
        else:
            errors.append(f"Entity {entity} {entities.get(entity)} is invalid")

    return {'validated' : validated, 'errors': errors}


def buildSql(parsed):
    metric : parsed.get("metric")
    duration : parsed.get("duration")

    return {metric : duration}


import datetime


def build_query(parsed):
    metric = parsed.get("metric")
    duration = parsed.get("duration")

    # base table
    if metric == "deals":
        select_part = "COUNT(*) as deals_count"
        table = "sales_deals"
    elif metric == "gross":
        select_part = "SUM(gross_amount) as total_gross"
        table = "sales_deals"
    elif metric == "profit":
        select_part = "SUM(profit_amount) as total_profit"
        table = "sales_deals"
    else:
        raise ValueError("Unknown metric")

    # duration filter
    today = datetime.date.today()
    if duration == "today":
        where_part = f"deal_date = '{today}'"
    elif duration == "mtd":
        first_day = today.replace(day=1)
        where_part = f"deal_date BETWEEN '{first_day}' AND '{today}'"
    elif duration == "ytd":
        first_day = today.replace(month=1, day=1)
        where_part = f"deal_date BETWEEN '{first_day}' AND '{today}'"
    elif duration == "last_20_days":
        start = today - datetime.timedelta(days=20)
        where_part = f"deal_date BETWEEN '{start}' AND '{today}'"
    elif duration == "this_week":
        start = today - datetime.timedelta(days=today.weekday())  # Monday
        where_part = f"deal_date BETWEEN '{start}' AND '{today}'"
    elif duration == "last_week":
        start = today - datetime.timedelta(days=today.weekday() + 7)
        end = start + datetime.timedelta(days=6)
        where_part = f"deal_date BETWEEN '{start}' AND '{end}'"
    else:
        raise ValueError("Unknown duration")

    # final query
    sql = f"SELECT {select_part} FROM {table} WHERE {where_part} AND where is_closed = 1;"
    return sql


if __name__ == "__main__":
    queries = [
        "How many deals did Ali close MTD?",
        # "How many deals did Ali close in last 90 days?",
        # "Show me gross profit last month for Lahore",
        # "Sara ke sales aj kitni hain?",
        # "YTD profit Islamabad store",
        # "Random text without valid entity"
    ]

    for q in queries:
        entities = extract_entities(q)
        result = validate_entities_2(entities,['metric','duration',
                                               # 'store','employee'
                                               ])
        # print(q, "->", result)
        # result = validate_entities(entities)
        # print(q, "->", result)
        # print(q, "->", result.get('validated').get('metric'))
        print(build_query(result.get('validated')))
