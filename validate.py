from datetime import datetime
import re
import pandas as pd

ALLOWED_UNIT_TYPES=["pcs","doz","kgs","g","l","ml","d","mm","mo"]
ALLOWED_TAX_SCHEMES=[]
ALLOWED_FIELD_TYPES=["textfield","date","phone number"]

PHONE_PATTERN=re.compile(r"^(\+91)?[6-9]\d{9}$")


def is_blank(value):
    if value is None:
        return True
    if isinstance(value,float) and pd.isna(value):
        return True
    if isinstance(value,str) and value.strip()=="":
        return True
    return False

def validate_non_empty(value,label):
    if is_blank(value):
        return f"{label} is empty"
    return None


def validate_unit_type(value):
    if not is_blank(value) and value not in ALLOWED_UNIT_TYPES:
        return f"Invalid unit type : {value}"
    return None


def validate_hsn_code(value):
    if value is None:
        return None
    text =str(value)
    if not text.isdigit():
        return f"HSN code must be numeric: {value}"
    if len(text)>20:
        return f"HSN code exceeds max length (20): {value}"
    return None


def validate_end_date(start,end):
    if end is None:
        return None
    if start is not None and end <start:
        return f"End date ({end}) is before start date ({start})"
    return None


def validate_tax_scheme(value):
    if not is_blank(value) and value not in ALLOWED_TAX_SCHEMES:
        return f"Invalid tax scheme code: {value}"
    return None


def validate_field_type(value):
    if not is_blank(value) and value not in ALLOWED_FIELD_TYPES:
        return f"Invalid field types:{value}"
    return None


def validate_field_value(value, field_type):
    if field_type == "phone number":
        if not value or not PHONE_PATTERN.match(str(value)):
            return f"Invalid phone number: {value}"
    elif field_type == "date":
        try:
            datetime.fromisoformat(str(value))
        except (ValueError, TypeError):
            return f"Invalid date value: {value}"
    elif field_type == "textfield":
        if value is None or str(value).strip() == "":
            return "Text value is empty"
    return None


def validate_product_row(row):
    errors = []
    for err in [
        validate_unit_type(row.get("Unit type")),
        validate_hsn_code(row.get("HSN Code")),
        validate_end_date(row.get("Start date"), row.get("End date")),
    ]:
        if err:
            errors.append(err)
    return "; ".join(errors) if errors else ""


def validate_price_row(row):
    errors = []
    if err := validate_tax_scheme(row.get("Default tax applicability")):
        errors.append(err)
    return "; ".join(errors) if errors else ""

def validate_characteristics_row(row):
    errors=[]
    field_name=row.get("Field name")
    field_type=row.get("Field type")
    field_value=row.get("Default value")

    if not is_blank(field_name):
        if err:= validate_non_empty(field_type,"Field type"):
            errors.append(err)
        else:
            if err:=validate_field_type(field_type):
                errors.append(err)
            if err:=validate_field_value(field_value,field_type):
                errors.append(err)
    return "; ".join(errors) if errors else ""
