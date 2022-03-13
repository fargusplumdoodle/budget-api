from typing import Dict, Any

import arrow


def nativify_dates(input: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in input.items():
        if isinstance(v, arrow.Arrow):
            input[k] = v.datetime
    return input
