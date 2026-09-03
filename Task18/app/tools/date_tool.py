from datetime import date


def get_current_date() -> dict:
    """
    Return today's date.
    """

    current_date = date.today().isoformat()

    return {
        "date": current_date
    }