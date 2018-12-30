from django.shortcuts import render


# Create your views here.
def error_report_view(request):
    # request.encoding = 'utf-8'
    # request.GET = request.GET.copy()
    # request.POST = request.POST.copy()

    return render(request, 'ErrorReport.html')
