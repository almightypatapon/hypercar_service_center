from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect


services = {
    'change_oil': {'description': 'Change oil', 'duration': 2},
    'inflate_tires': {'description': 'Inflate tires', 'duration': 5},
    'diagnostic': {'description': 'Get diagnostic', 'duration': 30},
}

line_of_cars = {key: [] for key, value in services.items()}
ticket = {'number': 0}


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html', context={'services': services})


class TicketView(View):

    def get(self, request, *args, **kwargs):
        service_key = kwargs['service_key']
        ticket['number'] += 1
        min_to_wait = sum(len(value) * services[key]['duration'] for key, value in line_of_cars.items()
                          if services[key]['duration'] <= services[service_key]['duration'])
        line_of_cars[service_key].append(ticket['number'])
        return render(request, 'tickets/ticket.html',
                      context={'service': services[service_key], 'ticket_number':  ticket['number'], 'min_to_wait': min_to_wait})


class OperatorView(View):
    next_ = []

    def post(self, request, *args, **kwargs):
        if line_of_cars['change_oil']:
            self.next_.insert(0, line_of_cars['change_oil'].pop(0))
        elif line_of_cars['inflate_tires']:
            self.next_.insert(0, line_of_cars['inflate_tires'].pop(0))
        elif line_of_cars['diagnostic']:
            self.next_.insert(0, line_of_cars['diagnostic'].pop(0))
        return redirect('/processing')

    def get(self, request, *args, **kwargs):
        [services[key].update({'queue': len(value)}) for key, value in line_of_cars.items()]
        return render(request, 'tickets/operator.html', context={'services': services, 'line_of_cars': line_of_cars, 'next_': self.next_})


class NextView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/next.html', context={'next_': OperatorView().next_})
