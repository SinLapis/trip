from django.shortcuts import render
from django.http import JsonResponse

ARRAY = 'array['
LNG = '][lng]'
LAT = '][lat]'


def main(request):
    return render(request, 'map/main.html')


def generate_route(request):

    i = 0
    points = []
    content = request.GET
    while True:
        if (ARRAY + str(i) + LNG) in content:
            point = {
                'lng': content[ARRAY + str(i) + LNG],
                'lat': content[ARRAY + str(i) + LAT]
            }
            points.append(point)
            i += 1
        else:
            break
    for point in points:
        print(point)
    json = {
        'rtime': '3:00',
        'rcost': '$50',
        'route': points,
    }
    return JsonResponse(json)
