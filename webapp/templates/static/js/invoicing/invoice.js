$(document).on("click", "#create_invoice", function(e){

	$.ajax({
		url: '{{ url_for("invoicing.invoice") }}',
		type: 'POST',
		dataType: 'json',
		success: function(data){

			document.location = document.location;	
			
		},
		error: function(data){

		}
	})
});