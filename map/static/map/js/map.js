//地图初始化
//创建地图实例时去掉默认的可点击POI
var map = new BMap.Map("mapContainer", {
    enableMapClick: false
});
//初始点初始化为用户所在地
var myCity = new BMap.LocalCity();
myCity.get(function (r) {
    map.centerAndZoom(r.name);
});
map.enableScrollWheelZoom();

//标记操作
var count = 0;
var markerArray = new Array(10);
var flag = 1;
var fix = 0;
map.addEventListener("click", function (event) {
    //保留点击位置
    if (flag) {
        if (fix) {
            //lng-0.001120 lat0.000975 zoom19
            var fixLng = -0.001120 * Math.pow(2, 19 - map.getZoom()),
                fixLat = 0.000975 * Math.pow(2, 19 - map.getZoom());
            markerArray[count] = new BMap.Marker(
                new BMap.Point(event.point.lng + fixLng, event.point.lat + fixLat)
            );

        } else {
            markerArray[count] = new BMap.Marker(event.point);
        }
        map.addOverlay(markerArray[count]);
        count++;
        if (count >= 10) {
            count = 0;
            flag = 0;
        }
    } else {
        //只保留10个标记
        markerArray[count].remove();
        markerArray[count] = new BMap.Marker(event.point);
        map.addOverlay(markerArray[count]);
        count++;
        count %= 10;
    }
});

//搜索
function searchMap(keyword) {
    var local = new BMap.LocalSearch(map, {
        renderOptions: {map: map}
    });
    local.search(keyword);
}
//清除覆盖物，清除marker数组
function clearMap() {
    map.clearOverlays();
    markerArray = [];
    count = 0;
    flag = 1;
    fix = 1;
}
