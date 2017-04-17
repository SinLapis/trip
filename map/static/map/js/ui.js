//蒙版效果
$("#menuBtn").on("click", function () {
    $("#menu").css("left", "0");
    var $mask = $("#mask");
    $mask.css("z-index", "2");
    $mask.css("background-color", "rgba(0, 0, 0, 0.5)");
});
$("#mask").on("click", function () {
    $("#menu").css("left", "-350px");
    var $mask = $("#mask");
    $mask.css("background-color", "rgba(0, 0, 0, 0)");
    //添加监听器等待动画结束再改变蒙版的z值
    $mask.one("transitionend", function () {
        $mask.css("z-index", "-1");
    });
});

//搜索按钮功能
$("#searchBtn").on("click", function () {
    searchMap($("#search").val());
});

//信息面板
$("#infoDismiss").on("click", function () {
    clearMap();
    var $infoBox = $("#infoBox");
    $infoBox.css("height", "0");
    $infoBox.one("transitionend", function () {
        $("#result").css("display", "none");
        $infoBox.css("display", "none");
        $("#genRoute").removeClass("disabled");
    });
});