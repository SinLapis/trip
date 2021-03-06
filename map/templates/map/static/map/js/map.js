//地图初始化
//创建地图实例时去掉默认的可点击POI
var map = new BMap.Map("mapContainer", {
    enableMapClick: false
});
// var driving;
// map.addEventListener("load", function () {
//     //路线规划
//     var options = {
//         onSearchComplete: function (results) {
//             // 获取第一条方案
//             var plan = results.getPlan(0);
//             // 获取方案的驾车线路
//             var route = plan.getRoute(0);
//             var pts = route.getPath();
//             var polyline = new BMap.Polyline(pts);
//             map.addOverlay(polyline);
//             console.log(pts);
//         }
//     };
//     driving = new BMap.DrivingRoute(map, options);
// });
//初始点初始化为用户所在地
// var myCity = new BMap.LocalCity();
// myCity.get(function (r) {
//     map.centerAndZoom(r.name, 14);
// });
map.centerAndZoom(new BMap.Point(104.072438, 30.662863), 14);
map.enableScrollWheelZoom();

//标记操作
var count = 0;
var markerArray = new Array(10);
var flag = 1;
var fix = 0;
map.addEventListener("click", function (event) {
    //保留点击位置
    if (flag) {
        //win10 150%缩放手动修正
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

