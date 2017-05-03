from django.contrib.gis.geos import LinearRing
from django.shortcuts import render
from django.http import JsonResponse

from map.models import Attraction, Picture

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


def show_attractions(request):
    print(request.GET)
    content = request.GET
    ls = LinearRing(
        (float(content['west-lat']), float(content['south-lng'])),
        (float(content['east-lat']), float(content['south-lng'])),
        (float(content['east-lat']), float(content['north-lng'])),
        (float(content['west-lat']), float(content['north-lng'])),
        (float(content['west-lat']), float(content['south-lng'])),
        srid=4326
    )
    json_content = []
    results = Attraction.objects.filter(point__contained=ls)
    for result in results[:20]:
        image = Picture.objects.filter(attraction_id=result.id)[0].pic_path
        attraction = {
            'name': result.name,
            'lat': result.point.x,
            'lng': result.point.y,
            'id': result.id,
            'img': image,
        }
        json_content.append(attraction)
    json = {
        'content': json_content,
    }
    return JsonResponse(json)
