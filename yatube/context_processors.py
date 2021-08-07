import datetime as dt


def year(request):
    god = dt.datetime.now().year
    return {
        "year": god,
    }
