from django.shortcuts import render, redirect
from django.views import View


class ClientCreate(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'clients/create_client_form.html', {})
