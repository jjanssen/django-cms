from datetime import datetime


def get_reference_date(request):
    """
    Returns the reference date to be used for determining whether content
    (Pages and Plugins) are "published".
    
    If the user is "time travelling" (and therefore a "timetravel_date" session
    variable has been set), the time travel date is used. Otherwise, it uses
    the current date/time (the standard Django CMS behavior).
    """
    if 'timetravel_date' in request.session:
        return request.session['timetravel_date']
    else:
        return datetime.now()
    
    