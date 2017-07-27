from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='authentications:login')
def index(request):
    return render(request, 'web/index.html')


@login_required(login_url='authentications:login')
def permission_denied(request):
    return render(request, 'web/permission-denied.html')


def health(request):
    return render(request, 'web/health.html')


@login_required(login_url='authentications:login')
def backlog(request):
    return render(request, 'web/backlog.html')
