from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from .models import Attraction, Tag, Tag_Map, Tag_Class_Map

INSIDE_CIRCLE = 0.0088960
OUTSIDE_CIRCLE = 0.0133439

tag_count = {}


def tag_count_init():
    results = Tag.objects.all()
    for result in results:
        tag_count[result.tag_name] = 0


def find_tag(attraction):
    return Tag_Map.objects.filter(attraction_id=attraction.id)[0].tag_id


def find_tag_class(tag):
    return Tag_Class_Map.objects.filter(tag_id=tag.id)[0].class_id


def add_attraction(days, recommends):
    pass


def offset_match(points, tag_classes):
    tag_count_init()
    recommends = []
    for point in points:
        print(type(point['lat']))
        inside_results = Attraction.objects.filter(point__dwithin=(
            Point(float(point['lat']), float(point['lng']), srid=4326), INSIDE_CIRCLE
        ))
        outside_results = Attraction.objects.filter(point__dwithin=(
            Point(float(point['lat']), float(point['lng']), srid=4326), OUTSIDE_CIRCLE
        ))
        # 内圈
        for result in inside_results:
            fit_select_theme = False
            attraction_tag = find_tag(result)
            for content_class in tag_classes:
                if content_class.id == find_tag_class(attraction_tag).id:
                    fit_select_theme = True
                    break
            recommend = {
                'attraction': result,
                'is-inside': True,
                'fit-select-theme': fit_select_theme,
                'tag': attraction_tag,
                'fit-most-theme': False,
            }
            tag_count[attraction_tag.tag_name] += 1
            recommends.append(recommend)
        # 外圈
        for result in outside_results:
            fit_select_theme = False
            attraction_tag = find_tag(result)
            for content_class in tag_classes:
                if content_class.id == find_tag_class(attraction_tag).id:
                    fit_select_theme = True
                    break
            recommend = {
                'attraction': result,
                'is-inside': False,
                'fit-select-theme': fit_select_theme,
                'tag': attraction_tag,
                'fit-most-theme': False,
            }
            tag_count[attraction_tag.tag_name] += 1
            recommends.append(recommend)

    most_theme = max(tag_count, key=tag_count.get)
    for i in range(len(recommends)):
        if recommends[i]['tag'].tag_name == most_theme:
            recommends[i]['fit-most-theme'] = True

    return recommends
