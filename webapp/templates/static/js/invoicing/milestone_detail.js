var case_category_create_url = "{{ url_for('invoicing.case_category_create', case_id=0) }}";
var case_action_url = "{{ url_for('invoicing.case_action', case_id=0) }}";

$(document).on('click', "#milestone_categories tr", function(e){

	var row = $(this);
	category_id = $(this).data('categoryid');
	category_name = $(this).find("td.category_name").html().trim();
	
	if(category_name.toLowerCase() == 'uncategorized'){
		category_name = "";
	}

	if(category_name != null){

		$("#milestone_cases td.category_label span.category_name").each(function(i, e){

			if($(e).html().trim() == category_name){
				$(e).closest("tr").show();
			}else{
				$(e).closest("tr").hide();
			}
		});
	}
});

$(document).on('change', "select[name^='action_']", function(e){

	var row = $(this).closest("tr");
	var case_id = $(this).attr('name').split('_')[1];
	var action = $(this).val();

	$.ajax({
		url: case_action_url.replace(/0/, case_id),
		data: { 'action': action },
		type: "POST",
		success: function(data){
			$(row).replaceWith($(data));
		},
		error: function(data){
			alert(data);
		}
	});
});

$(document).on('change', "select[name^='category_']", function(e){

	var select = $(this);
	var category_id = $(this).val();
	var case_id = $(this).attr('name').split('_')[1];

	$.ajax({
		url: case_category_create_url.replace(/0/, case_id),
		data: { 'category_id': category_id },
		type: "POST",
		dataType: "json",
		success: function(data){			

			$(select).closest("tr").find(".category_label span.category_name").html(data.category_name);

			if(data.category_id != null){

				var existing_row = $("#milestone_categories").find("tr[data-categoryid='" + data.category_id + "']");

				if(existing_row.length == 0){ 
					var newRow = $("<tr>").attr("data-categoryid", data.category_id);
					$("<td>").addClass("category_name").html(data.category_name).appendTo(newRow);
					$("<td>").addClass("category_case_count").html(data.category_case_count).appendTo(newRow);
					$("<td>").addClass("category_case_cost").html("$" + data.category_case_cost).appendTo(newRow);	
					$(newRow).appendTo($("#milestone_categories"));
				}else{
					$(existing_row).find("td.category_case_count").html(data.category_case_count);
					$(existing_row).find("td.category_case_cost").html("$" + data.category_case_cost);
				}
			}
			
			if(data.original_category_id != null){
				var existing_row = $("#milestone_categories").find("tr[data-categoryid='" + data.original_category_id + "']");
				$(existing_row).find("td.category_case_count").html(data.original_category_case_count);	
				$(existing_row).find("td.category_case_cost").html("$" + data.original_category_case_cost);	
			}			

			var uncategorized_row = $("#milestone_categories").find("tr:not([data-categoryid])");
			$(uncategorized_row).find("td.category_case_count").html(data.uncategorized_case_count);
			$(uncategorized_row).find("td.category_case_cost").html("$" + data.uncategorized_case_cost);
		},
		error: function(data){

		}
	})
});