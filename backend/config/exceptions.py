from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            'error': True,
            'status_code': response.status_code,
            'message': response.data
        }, status=response.status_code)

    # unhandled exceptions return clean 500
    return Response({
        'error': True,
        'status_code': 500,
        'message': 'An unexpected error occurred.'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)