from datetime import date


company_holidays = [
    {
        "date": "2026-10-02",
        "name": "Gandhi Jayanti"
    },
    {
        "date": "2026-10-20",
        "name": "Company Holiday"
    },
    {
        "date": "2026-11-09",
        "name": "Diwali"
    }
]


def tool_get_company_holidays(
    start_date: str | None = None,
    end_date: str | None = None
):

    holidays = company_holidays

    if start_date:

        try:
            start = date.fromisoformat(
                start_date
            )
        except ValueError:

            raise ValueError(
                "start_date must use YYYY-MM-DD format."
            )

        holidays = [
            holiday
            for holiday in holidays
            if date.fromisoformat(
                holiday["date"]
            ) >= start
        ]

    if end_date:

        try:
            end = date.fromisoformat(
                end_date
            )
        except ValueError:

            raise ValueError(
                "end_date must use YYYY-MM-DD format."
            )

        holidays = [
            holiday
            for holiday in holidays
            if date.fromisoformat(
                holiday["date"]
            ) <= end
        ]

    return holidays