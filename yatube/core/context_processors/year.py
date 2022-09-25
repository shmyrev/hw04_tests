from datetime import date


def year(request):
    today = date.today()
    year = today.strftime('%Y')
    return {'year': int(year)}
