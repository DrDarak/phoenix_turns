/////////////////////////////////////////////////////////////////////////////////////////////////////
// Tree Control Javascript
/////////////////////////////////////////////////////////////////////////////////////////////////////
function get_object(id)
{
	if (document.getElementById)
		return document.getElementById(id);
	return null;
}
function tree_toggle_cat(obj,cat_id,tree_id)
{
	var open=tree_toggle_img(obj);
	var cat_c=get_object('t_'+tree_id+'_c_'+cat_id);
	var cat_o=get_object('t_'+tree_id+'_o_'+cat_id);
	if (cat_o && cat_c)
	{
		cat_c.style.display=(open ? 'none' : '');
		cat_o.style.display=(open ? '' : 'none');
	}
}
function tree_toggle_data(obj,data_id,tree_id)
{
	var open=tree_toggle_img(obj);
	var data=get_object('t_'+tree_id+'_d_'+data_id);
	if (data)
		data.style.display=(open ? '' : 'none');
}
function tree_toggle_img(obj)
{
	// flips img and returns state
	var pattern=new RegExp('pos.gif','i');
	if (pattern.test(obj.src))
	{
		obj.src=obj.src.replace(/pos/i,'neg');
		return true; // closed
	}
	obj.src=obj.src.replace(/neg/i,'pos');
	return false; // open
}
