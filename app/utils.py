from typing import Dict, List
from fastapi import Request


def parse_property_filters(request: Request) -> Dict[str, List[str]]:
    property_filters = {}
    query_params = request.query_params

    for key, values in query_params.multi_items():
        if key.startswith("property_") and not (key.endswith("_from") or key.endswith("_to")):
            prop_uid = key[len("property_"):]
            if prop_uid not in property_filters:
                property_filters[prop_uid] = []
            property_filters[prop_uid].append(values)

    return property_filters


def parse_int_property_ranges(request: Request) -> Dict[str, Dict[str, int]]:
    int_property_ranges = {}
    query_params = request.query_params

    for key, value in query_params.multi_items():
        if key.startswith("property_") and (key.endswith("_from") or key.endswith("_to")):
            prop_uid = key[len("property_"):]

            if key.endswith("_from"):
                prop_uid = prop_uid[:-len("_from")]
                range_key = "from"
            else:
                prop_uid = prop_uid[:-len("_to")]
                range_key = "to"

            if not value.isdigit():
                continue

            if prop_uid not in int_property_ranges:
                int_property_ranges[prop_uid] = {}

            int_property_ranges[prop_uid][range_key] = int(value)

    return int_property_ranges