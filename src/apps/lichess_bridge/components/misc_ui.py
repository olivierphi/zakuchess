_ONE_DAY = 86_400
_TWO_DAYS = _ONE_DAY * 2


def time_left_display(time_left_seconds: int) -> str:
    # TODO: write a test for this
    if time_left_seconds < 1:
        return "time's up"
    if time_left_seconds < 60:
        return f"{time_left_seconds} seconds"
    if time_left_seconds < 3600:
        return f"{round(time_left_seconds/60)} minutes"
    if time_left_seconds < _ONE_DAY:
        return f"{round(time_left_seconds/3600)} hours"
    if time_left_seconds < _TWO_DAYS:
        return f"1 day and {round((time_left_seconds-_ONE_DAY)/3600)} hours"
    return f"{round(time_left_seconds/_ONE_DAY)} days"
