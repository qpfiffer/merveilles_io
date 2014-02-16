last_height = 0;
function search() {
    var term = $("#search_box").val();
    window.location = search_url + term;
}
String.prototype.hashCode = function(){
    var hash = 0;
    if (this.length == 0) return hash;
    for (i = 0; i < this.length; i++) {
        char = this.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

$(function() {
    $("#search_button").click(search);
    $("#search_box").keypress(function(e) {
        if (e.keyCode == 13) {
            search();
        }
    });
    $(".the_animal").each(function(iter, val) {
        // Let's generate some faces
        var username = $(val).attr("class").replace("the_animal ", "");
        var canvas = val.appendChild(document.createElement('canvas'));
        canvas.width = canvas.height = 32;
        var con = canvas.getContext('2d');
        drawHexFace(con, username.hashCode(), 'rgb(255,255,255)', 'rgb(68,68,68)');
    });
    $(".link").each(function(iter, val) {
        $(val).click(function(e) {
            var key= $(val).data().key;
            $.ajax({
                  url: single_item_url.replace("0", key),
            }).done(function(response) {
                $("#murder_me").html(response);
            });
            return false;
        });
    });
    $(window).scroll(function(e) {
        $("#murder_me").css("top", window.pageYOffset);
    });
});
