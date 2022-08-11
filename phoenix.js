function activate_tab(index)
{
    var search_tab=new RegExp('search_tab','i');
    var search_data=new RegExp('data_','i');
    var divs=document.getElementsByTagName('div');
    for (var i = 0; i < divs.length; i++)
    {    if (search_tab.test(divs[i].id))
		{
			var id = divs[i].id.substr(11);
			if (id==index)
				divs[i].className='search_tab on';
			else
				divs[i].className='search_tab';
		}
	 	if (search_data.test(divs[i].id))
		{
			var id = divs[i].id.substr(5);
			if (id==index)
				divs[i].style.display='';
			else
				divs[i].style.display='none';
		}
	}
}

////////////////////////////////////////////////////////////////////////////////////
// Turn display handling - needs to fail gracefully if we don't have access
function display_turn(file_name)
{
    var box=get_object('turn_frame');
    if (box)
       box.src=file_name
    var lp=get_object('left_panel');
    var rp=get_object('right_panel');
    if (lp && rp)
        var h=lp.clientHeight
        if (h<6000)
            h=6000;
        rp.style.height=h;

}
