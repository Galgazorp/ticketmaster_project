import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import SavedEvent, SearchHistory
from .forms import SearchForm
from datetime import datetime

API_KEY = 'wI9cG3aVgmUqwkyBXUPfrdbVNmHvb2yQ'
BASE_URL = 'https://app.ticketmaster.com/discovery/v2/events.json'


def get_best_image(images, preferred_ratio="3_2"):
    if not images:
        return ''
    matching = [img for img in images if img.get('ratio') == preferred_ratio]
    candidates = matching if matching else images
    best = max(candidates, key=lambda x: x.get('width', 0) * x.get('height', 0))
    return best.get('url', '')


def format_time_12hr(time_str):
    if not time_str or time_str == 'TBA':
        return 'TBA'
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = parts[1]
            period = 'AM' if hour < 12 else 'PM'
            if hour == 0:
                hour = 12
            elif hour > 12:
                hour -= 12
            return f"{hour}:{minute} {period}"
    except:
        return time_str
    return time_str


def format_date(date_str):
    if not date_str or date_str == 'TBA':
        return 'TBA'
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%b %d, %Y")
    except:
        return date_str


def index(request):
    form = SearchForm()
    return render(request, 'ticketmaster_app/index.html', {'form': form})


def search_events(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():
            classification = form.cleaned_data['classification']
            city = form.cleaned_data['city']

            try:
                params = {
                    'apikey': API_KEY,
                    'classificationName': classification,
                    'city': city,
                    'sort': 'date,asc'
                }

                response = requests.get(BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                raw_events = []
                if '_embedded' in data and 'events' in data['_embedded']:
                    raw_events = data['_embedded']['events']

                if request.user.is_authenticated:
                    saved_event_ids = set(
                        SavedEvent.objects.filter(user=request.user).values_list('event_id', flat=True)
                    )
                else:
                    saved_event_ids = set()

                events = []
                for event in raw_events:
                    venue = event.get('_embedded', {}).get('venues', [{}])[0] if event.get('_embedded') else {}
                    raw_time = event.get('dates', {}).get('start', {}).get('localTime', 'TBA')
                    raw_date = event.get('dates', {}).get('start', {}).get('localDate', 'TBA')
                    formatted_time = format_time_12hr(raw_time)
                    formatted_date = format_date(raw_date)
                    event_id = event.get('id', '')

                    events.append({
                        'id': event_id,
                        'name': event.get('name', ''),
                        'url': event.get('url', ''),
                        'image_url': get_best_image(event.get('images', [])),
                        'venue_name': venue.get('name', 'Venue TBA'),
                        'venue_address': venue.get('address', {}).get('line1', ''),
                        'venue_city': venue.get('city', {}).get('name', ''),
                        'venue_state': venue.get('state', {}).get('stateCode', ''),
                        'event_date': formatted_date,
                        'event_time': formatted_time,
                        'is_saved': event_id in saved_event_ids,
                    })

                SearchHistory.objects.create(
                    classification=classification,
                    city=city,
                    results_count=len(events)
                )

                request.session['last_search'] = {
                    'events': events,
                    'classification': classification,
                    'city': city,
                    'results_count': len(events)
                }

                context = {
                    'events': events,
                    'classification': classification,
                    'city': city,
                    'results_count': len(events),
                    'form': SearchForm(initial={'classification': classification, 'city': city})
                }
                return render(request, 'ticketmaster_app/results.html', context)

            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, 'Error fetching events. Please try again.')
                return render(request, 'ticketmaster_app/index.html', {'form': form})
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'ticketmaster_app/index.html', {'form': form})

    elif request.method == 'GET' and 'last_search' in request.session:
        last_search = request.session['last_search']

        if request.user.is_authenticated:
            saved_event_ids = set(
                SavedEvent.objects.filter(user=request.user).values_list('event_id', flat=True)
            )
        else:
            saved_event_ids = set()

        for event in last_search['events']:
            event['is_saved'] = event['id'] in saved_event_ids

        context = {
            'events': last_search['events'],
            'classification': last_search['classification'],
            'city': last_search['city'],
            'results_count': last_search['results_count'],
            'form': SearchForm(initial={
                'classification': last_search['classification'],
                'city': last_search['city']
            })
        }
        return render(request, 'ticketmaster_app/results.html', context)

    return redirect('index')


@login_required(login_url='login')
def saved_events(request):
    events = SavedEvent.objects.filter(user=request.user)
    return render(request, 'ticketmaster_app/saved_events.html', {'saved_events': events})


@login_required(login_url='login')
def save_event_ajax(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')

        if not event_id:
            return JsonResponse({'saved': False, 'message': 'Event ID is required'})

        if SavedEvent.objects.filter(event_id=event_id, user=request.user).exists():
            return JsonResponse({'saved': False, 'message': 'Event already saved', 'already_saved': True})

        SavedEvent.objects.create(
            event_id=event_id,
            event_name=request.POST.get('event_name', ''),
            event_url=request.POST.get('event_url', ''),
            event_image_url=request.POST.get('event_image_url', ''),
            venue_name=request.POST.get('venue_name', ''),
            venue_address=request.POST.get('venue_address', ''),
            venue_city=request.POST.get('venue_city', ''),
            venue_state=request.POST.get('venue_state', ''),
            event_date=request.POST.get('event_date', ''),
            event_time=request.POST.get('event_time', ''),
            user=request.user,
        )

        return JsonResponse({'saved': True, 'message': 'Event saved successfully!'})

    return JsonResponse({'saved': False, 'message': 'Invalid request'})


@login_required(login_url='login')
def save_event(request, event_id):
    if request.method == 'POST':
        try:
            url = f'https://app.ticketmaster.com/discovery/v2/events/{event_id}.json'
            response = requests.get(url, params={'apikey': API_KEY}, timeout=10)
            event_data = response.json()

            raw_time = event_data.get('dates', {}).get('start', {}).get('localTime', '')
            raw_date = event_data.get('dates', {}).get('start', {}).get('localDate', '')

            SavedEvent.objects.update_or_create(
                event_id=event_id,
                user=request.user,
                defaults={
                    'event_name': event_data.get('name', ''),
                    'event_url': event_data.get('url', ''),
                    'event_image_url': get_best_image(event_data.get('images', [])),
                    'venue_name': event_data.get('_embedded', {}).get('venues', [{}])[0].get('name', ''),
                    'venue_address': event_data.get('_embedded', {}).get('venues', [{}])[0].get('address', {}).get('line1', ''),
                    'venue_city': event_data.get('_embedded', {}).get('venues', [{}])[0].get('city', {}).get('name', ''),
                    'venue_state': event_data.get('_embedded', {}).get('venues', [{}])[0].get('state', {}).get('stateCode', ''),
                    'event_date': format_date(raw_date),
                    'event_time': format_time_12hr(raw_time),
                }
            )
            messages.success(request, 'Event saved!')
        except:
            messages.error(request, 'Error saving event.')

    return redirect('search_events')


@login_required(login_url='login')
def edit_saved_event(request, event_id):
    if request.method == 'POST':
        try:
            event = SavedEvent.objects.get(event_id=event_id, user=request.user)
            event.notes = request.POST.get('notes', '')
            event.save()
            messages.success(request, 'Event notes updated successfully!')
        except SavedEvent.DoesNotExist:
            messages.error(request, 'Event not found.')
        except:
            messages.error(request, 'Error updating event notes.')
    return redirect('saved_events')


@login_required(login_url='login')
def delete_saved_event(request, event_id):
    if request.method == 'POST':
        try:
            SavedEvent.objects.get(event_id=event_id, user=request.user).delete()
            messages.success(request, 'Event deleted.')
        except SavedEvent.DoesNotExist:
            messages.error(request, 'Event not found.')
    return redirect('saved_events')