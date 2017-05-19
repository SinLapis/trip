import heapq
import random
from operator import itemgetter

from django.contrib.gis.geos import LinearRing
from django.shortcuts import render
from django.http import JsonResponse

from map.models import Attraction, Picture, Tag, Tag_Map, Route, Route_Map, Tag_Class
from map import algorithm

POINTS = 'points['
LNG = '][lng]'
LAT = '][lat]'


def main(request):
    return render(request, 'map/main.html')


def generate_route(request):
    i = 0
    points = []
    content = request.GET
    for (key, value) in content.items():
        print('key: ' + key)
        print('value: ' + value)
    days = int(content['days'])
    guys = int(content['guys'])
    tag_classes = []
    if content['natural-type']:
        tag_classes.append(Tag_Class.objects.filter(class_name='自然景观')[0])
    if content['cultural-type']:
        tag_classes.append(Tag_Class.objects.filter(class_name='人文景观')[0])
    if content['historical-type']:
        tag_classes.append(Tag_Class.objects.filter(class_name='古迹类')[0])

    while True:
        if (POINTS + str(i) + LNG) in content:
            point = {
                'lng': content[POINTS + str(i) + LNG],
                'lat': content[POINTS + str(i) + LAT]
            }
            points.append(point)
            i += 1
        else:
            break
    # for point in points:
    #     print(point)
    # distance2 = ((float(points[0]['lng']) - float(points[1]['lng'])) ** 2 +
    #              (float(points[0]['lat']) - float(points[1]['lat'])) ** 2)
    # print(math.sqrt(distance2))
    recommends = algorithm.offset_match(points, tag_classes)
    if len(recommends) > days * 3:
        recommends = algorithm.score_delete_recommends(recommends, days)
    distance_matrix = algorithm.get_distance_matrix(recommends)
    recommends = algorithm.greedy_algorithm(recommends, distance_matrix)
    recommends_json = []
    deduplicate = []
    for index, recommend in enumerate(recommends):
        if recommend['attraction'].name not in deduplicate:
            img = Picture.objects.filter(attraction_id=recommend['attraction'].id)[0].pic_path
            recommend_content = {
                'name': recommend['attraction'].name,
                'lat': recommend['attraction'].point.x,
                'lng': recommend['attraction'].point.y,
                'img': img,
                'index': index,
            }
            deduplicate.append(recommend['attraction'].name)
            recommends_json.append(recommend_content)
    json = {
        'route': recommends_json,
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
