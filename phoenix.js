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