import asks


def make_session(token, base_location="https://api.telegram.org", connections=2):
    return asks.Session(
        base_location=base_location, endpoint=f"/bot{token}", connections=connections
    )
