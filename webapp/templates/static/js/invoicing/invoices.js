$(document).on("click", "#update_invoice", function(e){

	var button = $(this);
	var invoice_id = $(button).data('invoiceid');
	var action = $(button).data('action');
	
	var update_invoice_url = '{{ url_for("invoicing.invoice_update", invoice_id=0) }}';

	$.ajax({
		url: update_invoice_url.replace(/0/, invoice_id),
		type: 'PUT',
		data: { action: action },
		dataType: 'json',
		success: function(data){

			document.location = document.location;	
			
		},
		error: function(data){

		}
	})
});