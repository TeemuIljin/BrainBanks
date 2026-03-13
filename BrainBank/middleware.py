import logging
import time


logger = logging.getLogger('performance')


class PerformanceLoggingMiddleware:
    """
    Simple middleware that logs request duration to help track p95 latency.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "request_completed",
            extra={
                "path": request.path,
                "method": request.method,
                "status_code": getattr(response, "status_code", None),
                "duration_ms": round(duration_ms, 2),
                "user_id": getattr(getattr(request, "user", None), "id", None),
            },
        )

        return response

