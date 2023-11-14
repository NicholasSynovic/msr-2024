import re

def parse_licenses(license_string):
    # Split the string on 'AND' or 'OR', and remove leading/trailing whitespaces
    terms = [term.strip() for term in re.split(r'\b(?:AND|OR)\b', license_string)]

    # Remove parentheses from terms
    terms = [term.strip('()') for term in terms]

    # Remove empty terms
    terms = [term for term in terms if term]

    return terms

# Example input
examples = [
    "cc-by-nc-sa-4.0 AND (cc-by-4.0 AND cc-by-nc-sa-4.0)",
    "cc-by-4.0 AND mit",
    "apache-2.0",
    "mit",
    "bsd-simplified",
    "mit AND apache-2.0",
    "gpl-1.0-plus AND gpl-3.0",
    "gpl-3.0"
]

# Process and print results for each example
for example in examples:
    result = parse_licenses(example)
    print(f'Input: {example}\nOutput: {result}\n')
