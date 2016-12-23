from time import time as now

from .models import InstrumentationEvent

class InstrumentQuestionPageLoadTimes:
    def __init__(self, next_middleware):
        self.next_middleware = next_middleware

    def __call__(self, request):
        # Remember when the request processing began. Unfortunately we don't
        # yet know if this request's timing should be logged so we do this
        # for every request.
        start = now()

        # Run the request like normal.
        response = self.next_middleware(request)

        # If the request object has been tagged to indicate that its
        # load time should be logged, then log it.
        event_info = getattr(request, "_instrument_page_load", None)
        if event_info:
            duration = (now() - start) * 1000 # store in msec because that's a more natural scale and
                                              # the analytics page likes to round event_value to integers
            InstrumentationEvent.objects.create(
                user=request.user,
                event_value=duration,
                **event_info
            )

        # Return the response unchanged.
        return response