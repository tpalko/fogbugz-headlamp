$(document).on("click", "#finalize_invoice", function(e){

	var button = $(this);
	var invoice_id = $(button).data('invoiceid');
	
	$.ajax({
		url: '{{ url_for("invoicing.invoice_finalize") }}',
		type: 'PUT',
		data: { invoice_id: invoice_id },
		dataType: 'json',
		success: function(data){

			if(data.success){
				document.location = data.redirect_url;	
			}			
		},
		error: function(data){

		}
	})
});