$(document).on("click", "#refund_deliverable", function(e){

	var button = $(this);
	var deliverable_id = $(button).data('deliverableid');
	
	var refund_deliverable_url = '{{ url_for("invoicing.deliverable_refund", deliverable_id=0) }}';

	$.ajax({
		url: refund_deliverable_url.replace(/0/, deliverable_id),
		type: 'PUT',
		dataType: 'json',
		success: function(data){
			document.location = document.location;				
		},
		error: function(data){

		}
	})
});