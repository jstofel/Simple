

/* ACCORDIAN: Toggle between adding and removing the "active" and "show" classes when the user clicks on one of the "Section" buttons. 
 The "active" class is used to add a background color to the current button when its belonging panel is open. 
 The "show" class is used to open the specific accordion panel */

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
    acc[i].onclick = function(){
        this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("show");
    }
    acc[i].onmouseover = function(){
        this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("show");
    }
    acc[i].onmouseout = function(){
	this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("hide");
    }

}


/**Try It Editor **/

    function runCode()
{
    var content = document.getElementById('sourceCode').value;
    var iframe = document.getElementById('targetCode');
    iframe = (iframe.contentWindow) ? iframe.contentWindow : (iframe.contentDocument.document) ? iframe.contentDocument.document : iframe.contentDocument;
    iframe.document.open();
    iframe.document.write(content);
    iframe.document.close();
    return false;
}


/**  Use ShowDown to convert markdown to HTML **/
function runConverter() {
    var text = document.getElementById('sourceTA').value,
	target = document.getElementById('targetDiv'),
	converter = new showdown.Converter(),
	html = converter.makeHtml(text);

    target.innerHTML = html;
}
