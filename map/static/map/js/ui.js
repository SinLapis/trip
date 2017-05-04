//蒙版效果
$("#menuBtn").on("click", function () {
    $("#menu").css("left", "0");
    var $mask = $("#mask");
    $mask.css("z-index", "2");
    $mask.css("background-color", "rgba(0, 0, 0, 0.5)");
    $mask.one("click", function () {
        $("#menu").css("left", "-350px");
        var $mask = $("#mask");
        $mask.css("background-color", "rgba(0, 0, 0, 0)");
        //添加监听器等待动画结束再改变蒙版的z值
        $mask.one("transitionend", function () {
            $mask.css("z-index", "-1");
        });
    });
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