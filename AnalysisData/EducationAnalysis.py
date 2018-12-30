from django.db import connections


def education_analysis_view(request):
    request.encoding = 'utf-8'

    if request.method == 'GET' or request.method == 'POST':
        to_render = {}
        with connections['ResultDB'].cursor() as cursor:
            cursor.execute(
                "SELECT "
            )