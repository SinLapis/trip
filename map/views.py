import heapq
import random

import math
from operator import itemgetter

from django.contrib.gis.geos import LinearRing
from django.shortcuts import render
from django.http import JsonResponse

from map.models import Attraction, Picture, Tag, Tag_Map, Route, Route_Map

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
    # for point in points:
    #     print(point)
    distance2 = ((float(points[0]['lng']) - float(points[1]['lng'])) ** 2 +
                (float(points[0]['lat']) - float(points[1]['lat'])) ** 2)
    print(math.sqrt(distance2))
    json = {
        'rtime': '3:00',
        'rcost': '$50',
        'route': points,
    }
    return JsonResponse(json)


def show_attractions(request):
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
    if content['tag'] == 'all':
        results = Attraction.objects.filter(point__contained=ls)
    else:
        tag = Tag.objects.filter(tag_name=content['tag'])[0]
        pre_results = Attraction.objects.filter(point__contained=ls)
        results = []
        for pre_result in pre_results:
            if tag.id == Tag_Map.objects.filter(attraction_id=pre_result.id)[0].tag_id.id:
                results.append(pre_result)
        print(results)
    for result in results:
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


def show_detail(request):
    name = request.GET['name']
    attraction = Attraction.objects.filter(name=name)[0]
    image_path = Picture.objects.filter(attraction_id=attraction.id)
    if len(image_path) >= 10:
        l = random.sample(range(len(image_path)), 10)
    else:
        l = range(len(image_path))
    images = []
    for i in l:
        images.append(image_path[i].pic_path)
    json = {
        'introduction': attraction.introduction,
        'images': images,
    }
    return JsonResponse(json)

def show_tags(request):
    tags = Tag.objects.all()
    counts = []
    for tag in tags:
        count = len(Tag_Map.objects.filter(tag_id=tag.id))
        counts.append(count)
    top_5_index = heapq.nlargest(5, range(len(counts)), counts.__getitem__)
    content = []
    for index in top_5_index:
        content.append(tags[index].tag_name)
    json = {
        'tag': content,
    }
    return JsonResponse(json)


def show_route(request):
    routes = Route.objects.all()
    content = []
    for route in routes:
        content.append(route.route_name)
    json = {
        'route': content
    }
    return JsonResponse(json)


def route_detail(request):
    route_name = request.GET['name']
    route = Route.objects.filter(route_name=route_name)[0]
    route_query = Route_Map.objects.filter(route_id=route.id)
    content = []
    for rq in route_query:
        attraction = Attraction.objects.filter(id=rq.attraction_id.id)[0]
        attraction_poiint = {
            'lat': attraction.point.x,
            'lng': attraction.point.y,
            'num': rq.attraction_num,
        }
        content.append(attraction_poiint)
    sorted(content, key=itemgetter('num'))
    json = {
        'detail': content
    }
    return JsonResponse(json)
