var update_milestone_url = "{{ url_for('invoicing.milestone_update', milestone_id=0) }}";

$(document).on('click', "button.freeze, button.unfreeze", function(e){

	var milestone_id = $(this).closest("div[data-milestoneid]").data().milestoneid;

	$.ajax({
		url: update_milestone_url.replace(/0/, milestone_id),
		data: { action: 'toggle_freeze' },
		type: "POST",
		success: function(data){
			$("#milestone_buttons_" + milestone_id).html(data);
		}
	});
});

$(document).ready(function(){

	$(".various").fancybox({
		maxWidth	: 1000,
		maxHeight	: 600,
		fitToView	: false,
		width		: '100%',
		height		: '100%',
		autoSize	: true,
		closeClick	: false,
		openEffect	: 'none',
		closeEffect	: 'none'
	});
});	

$(document).on('click', '[disabled]', function(e){

	e.preventDefault();
	//alert('disabled!');
});