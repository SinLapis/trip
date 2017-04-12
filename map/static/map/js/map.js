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
map.addEventListener("click", function (event) {
    //保留点击位置
    if (flag) {
        markerArray[count] = new BMap.Marker(event.point);
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
