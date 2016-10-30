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
		$('#text').hide();
		$('#loader').show(); // loading image
		$.ajax({
			url : '/summarization',
			type : 'POST',
			data : {'text': $('#text').val(),},
			success : function(data) {
			    $('#text').val(data);
			    $('#loader').hide();
       			$('#text').show();
			}
		})
	});

	// button save settings
	$('body').on('click', '#saveSettings', function(e) {
		e.preventDefault();
		ratio = $('#ratio').val();
		dtm = $('#dtm :selected').val();
		sentenceSelection = $('#sentenceSelection :selected').val();
		formatFile = $('#formatFile :selected').val();
		$.ajax({
			'url' : '/settings',
			'type' : 'POST',
			data : {
				'ratio' : ratio,
				'dtm' : dtm,
				'sentenceSelection' : sentenceSelection,
				'formatFile' : formatFile,
			},
			success : function(data) {
				if(data=='sukses') {
					swal("Save changes", "", "success");
				}
			}
		})
	});
	
});
