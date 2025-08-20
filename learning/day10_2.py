# import nltk
# nltk.download("stopwords")

import re
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

tokenizer = TreebankWordTokenizer()
lemmatizer = WordNetLemmatizer()
question = "How many Deals we have in this month ? What is total gross of James J ?"
# tokens = tokenizer.tokenize(question)


normalized = []

DDS_SYSNONYMS = {
    'mtd' : 'month_to_date',
    'this month' : 'month_to_date',
    "deal": "sales_deals",
    "units": "sales_deals",
    "current month": "month_to_date",
    "total gross": "total_gross",
    "frontend gross": "front_end_gross",
    "front end gross": "front_end_gross",
    "back end gross": "back_end_gross",
    "backend gross": "back_end_gross",
}

def to_lower_case(text):
    return text.lower()
def remove_special_chars(text):
    text = re.sub(r"[^a-z0-9\s]", "", text)

    return text


def apply_phrase_synonyms(tokens, DDS_SYSNONYMS):
    text = tokens

    # Pehle multi-word phrases replace karo
    for phrase, replacement in DDS_SYSNONYMS.items():
        if " " in phrase and phrase in text:
            text = text.replace(phrase, replacement)
        if " " not in phrase and phrase in text:
            text = text.replace(phrase, replacement)

    return text


def lemmatize_tokens(tokens):
    lemmatized_tokens = []
    for t_lower in tokens:
        lemma = lemmatizer.lemmatize(t_lower)
        lemmatized_tokens.append(lemma)

    return lemmatized_tokens

stopwords = set(stopwords.words('english'))

def remove_stopwords(tokens):
    tokens_without_stopwords = []
    for t_lower in tokens:
        if t_lower not in stopwords:
            tokens_without_stopwords.append(t_lower)

    return tokens_without_stopwords

question = to_lower_case(question)
print("to_lower_case")
print(question)
text = remove_special_chars(question)
print("remove_special_chars")
print(text)

lemmatized = lemmatize_tokens(text.split())
print("lemmatized")
print(lemmatized)

synonyms_applied = apply_phrase_synonyms(" ".join(lemmatized), DDS_SYSNONYMS)
print("apply_phrase_synonyms")
print(synonyms_applied)



tokens = remove_stopwords(synonyms_applied.split())
print("remove_stopwords")
print(tokens)

