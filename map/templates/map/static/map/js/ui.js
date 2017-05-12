//关闭菜单
function closeMenu() {
    $("#menu").css("left", "-350px");
    var $mask = $("#mask");
    $mask.css("background-color", "rgba(0, 0, 0, 0)");
    //添加监听器等待动画结束再改变蒙版的z值
    $mask.one("transitionend", function () {
        $mask.css("z-index", "-1");
    });
}
//蒙版效果
$("#menuBtn").on("click", function () {
    $("#menu").css("left", "0");
    var $mask = $("#mask");
    $mask.css("z-index", "2");
    $mask.css("background-color", "rgba(0, 0, 0, 0.5)");
    $mask.one("click", closeMenu);
});

//搜索按钮功能
$("#searchBtn").on("click", function () {
    searchMap($("#search").val());
});

//景点面板关闭
$("#detailDismiss").on("click", function () {
    $("#detailPanel").css("display", "none");
    var $mask = $("#mask");
    $mask.css("background-color", "rgba(0, 0, 0, 0)");
    //添加监听器等待动画结束再改变蒙版的z值
    $mask.one("transitionend", function () {
        $mask.css("z-index", "-1");
    });
    var $detailImage = $("#detailImage");
    $detailImage.find("ol").empty();
    $detailImage.find("div").empty();
    $detailImage.removeClass("slide");
});
//菜单选项
$("#days").slider({
    formatter: function (value) {
        return value;
    }
});
//全局tag
var current_tag = "all";
//菜单tag部分初始化
var $themePanel = $("#themePanel");
$themePanel.children("li").on("click", function () {
    current_tag = "all";
    clearAttractionOverlay();
    getCurrentAttractions();
    closeMenu();
});
$themePanel.children("li").css("cursor", "pointer");
$.getJSON("/map/top-tags/", {}, function (json) {
    for (var i = 0; i < json.tag.length; i++) {
        $themePanel.append('<li class="list-group-item"></li>');
        $themePanel.children("li:last").text(json.tag[i]);
        $themePanel.children("li:last").css("cursor", "pointer");
        $themePanel.children("li:last").on("click", function () {
            current_tag = $(this).text();
            clearAttractionOverlay();
            getCurrentAttractions();
            closeMenu();
        });
    }
});
//路线生成及绘制
var $infoBox = $("#infoBox"), $waiting = $("#waiting"), $result = $("#result");
//查找poi回调
function localSearchCallback(titles, json) {
    var drivingOptions = {
        onSearchComplete: function (results) {
            var plan = results.getPlan(0);
            var route = plan.getRoute(0);
            var pts = route.getPath();
            var polyline = new BMap.Polyline(pts);
            map.addOverlay(polyline);
        }
    };
    var driving = new BMap.WalkingRoute(map, drivingOptions);
    for (i = 1; i < titles.length; i++) {
        console.log(titles[i - 1] + ' ' + titles[i]);
        driving.search(titles[i - 1], titles[i]);
    }
    $infoBox.css("height", "150px");
    $infoBox.one("transitionend", function () {
        $waiting.css("display", "none");
        $result.css("display", "block");
        $("#rtime").html(json.rtime);
        $("#rcost").html(json.rcost);
    });
}
//信息框展示标志
var infoBoxOn = false;
function drawRoute(pack) {
    var days = $("#days").attr("data-slider-value");
    var guys = $("#guys").val();
    if (!guys)
        guys = 1;
    $.getJSON("/map/generate/", {
        "days": days,
        "guys": guys,
        "natural-type": $("#naturalOption").is(":checked"),
        "cultural-type": $("#culturalOption").is(":checked"),
        "historical-type": $("#historicalOption").is(":checked"),
        "points": pack
    }, function (json) {
        //处理后端回应
        //信息框展示
        infoBoxOn = true;
        clearMap();
        console.log(json.route);
        //绘制折线、图标
        var points = [];
        for (i = 0; i < json.route.length; i++) {
            if (json.route[i].lng && json.route[i].lat) {
                var attractionOverlay = new AttractionOverlay(
                    new BMap.Point(json.route[i].lng, json.route[i].lat),
                    json.route[i].name, json.route[i].img
                );
                attractionOverlayArray.push(attractionOverlay);
                map.addOverlay(attractionOverlay);
            }
            points.push(new BMap.Point(json.route[i].lng, json.route[i].lat));
        }
        // var polyline = new BMap.Polyline(points);
        // map.addOverlay(polyline);
        var titles = [];
        var searchOption = {
            onSearchComplete: function (results) {
                if (results.getPoi(0))
                    titles.push(results.getPoi(0).title);
                else {
                    var index = titles.length;
                    points.splice(index, 1);
                }
                if (titles.length === points.length)
                    localSearchCallback(titles, json);
            }
        };
        var localSearch = new BMap.LocalSearch(map, searchOption);
        for (i = 0; i < points.length; i++) {
            localSearch.search(json.route[i].name);
        }
    });
}
//菜单路线部分初始化
var $routePanel = $("#routePanel");
$.getJSON("/map/route/", {}, function (json) {
    for (var i = 0; i < json.route.length; i++) {
        $routePanel.append('<li class="list-group-item"></li>');
        $routePanel.children("li:last").text(json.route[i]);
        $routePanel.children("li:last").css("cursor", "pointer");
        $routePanel.children("li:last").on("click", function () {
            closeMenu();
            $("#genRoute").addClass("disabled");
            //调出信息面板-等待
            $infoBox.css("display", "block");
            $infoBox.css("height", "60px");
            $waiting.css("display", "inline-block");
            $.getJSON("/map/route-detail/", {
                "name": $(this).text()
            }, function (json) {
                var pack = json.detail;
                for (var i = 0; i < pack.length; i++) {
                    var marker = new BMap.Marker(new BMap.Point(pack[i].lng, pack[i].lat));
                    map.addOverlay(marker);
                }
                drawRoute(pack);
            });
        });
    }
});
//生成路线按钮
$("#genRoute").on("click", function () {
    $("#genRoute").addClass("disabled");
    //调出信息面板-等待
    $infoBox.css("display", "block");
    $infoBox.css("height", "60px");
    $waiting.css("display", "inline-block");
    //向后端发送ajax请求
    var pack = [];
    for (var i = 0; i < 10; i++) {
        if (markerArray[i]) {
            var point = {
                "lng": markerArray[i].getPosition().lng,
                "lat": markerArray[i].getPosition().lat
            };
            pack.push(point);
        }
    }
    drawRoute(pack);
});
//自定义覆盖物
function AttractionOverlay(point, name, imgURL) {
    this._point = point;
    this._name = name;
    this._imgURL = imgURL;
}

AttractionOverlay.prototype = new BMap.Overlay();
AttractionOverlay.prototype.initialize = function (map) {
    this._map = map;
    var div = this._div = document.createElement("div");
    div.style.position = "absolute";
    div.style.zIndex = BMap.Overlay.getZIndex(this._point.lat);
    div.style.backgroundColor = "#6BADCA";
    div.style.border = "1px solid #5188A5";
    div.style.color = "white";
    div.style.height = "60px";
    div.style.width = "80px";
    div.style.padding = "2px";
    div.style.lineHeight = "18px";
    div.style.whiteSpace = "nowrap";
    div.style.MozUserSelect = "none";
    div.style.fontSize = "12px";
    //div.style.display = "table-cell";
    div.style.textAlign = "center";
    //div.style.verticalAlign = "middle";
    var that = this;
    //弹出景点面板
    div.addEventListener("click", function (e) {
        $("#detailPanel").css("display", "block");
        $.getJSON("/map/detail/", {
            'name': that._name
        }, function (json) {
            $("#detailTitle").text(that._name);
            $("#introduction").text(json.introduction);
            //图片轮播设置
            var $detailImage = $("#detailImage");
            $detailImage.addClass("slide");
            for (var i = 0; i < json.images.length; i++) {
                $detailImage.children("ol").append('<li data-target="carousel-generic"></li>');
                $detailImage.find("li:last").attr("data-slide-to", i);
                $detailImage.children("div").append('<div class="item">' +
                    '<a href="javascript:void(0);"><img src="" class="detail-img">' +
                    '</a></div>');
                $detailImage.find("img:last").attr("src", json.images[i]);
            }
            $detailImage.children("ol").children("li:first").addClass("active");
            $detailImage.children("div").children("div:first").addClass("active");
        });
        var $mask = $("#mask");
        $mask.css("z-index", "2");
        $mask.css("background-color", "rgba(0, 0, 0, 0.5)");
        e.stopPropagation();
    });

    //图片
    var img = this._img = document.createElement("img");
    img.style.width = "auto";
    img.style.height = "auto";
    img.style.maxHeight = "100%";
    img.style.maxWidth = "100%";
    //img.style.verticalAlign = "middle";
    img.setAttribute("src", this._imgURL);
    div.appendChild(img);
    //框内文字
    //var span = this._span = document.createElement("span");
    //div.appendChild(span);
    //span.appendChild(document.createTextNode(this._text));
    //var that = this;
    //箭头
    var arrow = this._arrow = document.createElement("div");
    arrow.style.background = "url(static/map/images/label.png) no-repeat";
    arrow.style.position = "absolute";
    arrow.style.width = "11px";
    arrow.style.height = "10px";
    arrow.style.top = "59px";
    arrow.style.left = "10px";
    arrow.style.overflow = "hidden";
    arrow.style.backgroundPosition = "0px -20px";
    div.appendChild(arrow);
    div.onmouseout = function () {
        this.style.backgroundColor = "#6BADCA";
        this.style.borderColor = "#5188A5";
        //this.getElementsByTagName("span")[0].innerHTML = that._overText;
        arrow.style.backgroundPosition = "0px -20px";
        this.style.zIndex *= 2.0;
    };

    div.onmouseover = function () {
        this.style.backgroundColor = "#EE5D5B";
        this.style.borderColor = "#BD3D3A";
        //this.getElementsByTagName("span")[0].innerHTML = that._text;
        arrow.style.backgroundPosition = "0px 0px";
        this.style.zIndex /= 2.0;
    };

    map.getPanes().labelPane.appendChild(div);

    return div;
};
AttractionOverlay.prototype.draw = function () {
    var map = this._map;
    var pixel = map.pointToOverlayPixel(this._point);
    this._div.style.left = pixel.x - parseInt(this._arrow.style.left) + "px";
    this._div.style.top = pixel.y - 69 + "px";
};

attractionOverlayArray = [];
//实时更新标记景点
function clearAttractionOverlay() {
    for (var i = 0; i < attractionOverlayArray.length; i++) {
        map.removeOverlay(attractionOverlayArray[i]);
    }
    attractionOverlayArray = [];
}

function getCurrentAttractions() {
    if (!infoBoxOn) {
        var bs = map.getBounds(),
            bsSouthWest = bs.getSouthWest(),
            bsNorthEast = bs.getNorthEast(),
            zoomLevel = map.getZoom();
        $.getJSON("/map/show/", {
            "south-lng": bsSouthWest.lng,
            "west-lat": bsSouthWest.lat,
            "north-lng": bsNorthEast.lng,
            "east-lat": bsNorthEast.lat,
            "zoom": zoomLevel,
            'tag': current_tag
        }, function (json) {
            clearAttractionOverlay();
            for (var i = 0; i < json.content.length; i++) {
                if (json.content[i].lng && json.content[i].lat) {
                    var attractionOverlay = new AttractionOverlay(
                        new BMap.Point(json.content[i].lng, json.content[i].lat),
                        json.content[i].name, json.content[i].img
                    );
                    attractionOverlayArray.push(attractionOverlay);
                    map.addOverlay(attractionOverlay);
                }
            }
        });
    }
}

map.addEventListener("zoomend", getCurrentAttractions);
map.addEventListener("dragend", getCurrentAttractions);

//信息面板关闭
$("#infoDismiss").on("click", function () {
    infoBoxOn = false;
    clearMap();
    getCurrentAttractions();
    var $infoBox = $("#infoBox");
    $infoBox.css("height", "0");
    $infoBox.one("transitionend", function () {
        $("#result").css("display", "none");
        $infoBox.css("display", "none");
        $("#genRoute").removeClass("disabled");
    });
});