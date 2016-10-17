$(document).ready(function() {

	$('body').on('change', '#file', function() {	
		var form_data = new FormData($('#upload-file')[0]);
		$('#text').hide();
		$('#loader').show(); // loading image
		$.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
            	$('#text').val(data);
            	$('#loader').hide();
       			$('#text').show();
            },
        });

	});

	// button upload
	$('body').on('click', '#upload', function() {
		$('#file').trigger('click');

	});

	
	// button clear
	$('body').on('click', '#clear', function() {
		$('#text').val("");

	});

	// button summarization
	$('body').on('click', '#summarization', function() {
		$.ajax({
			url : '/summarization',
			type : 'POST',
			data : {'text': $('#text').val(),},
			success : function(data) {
				console.log(data);
			}
		})
	});
	
});