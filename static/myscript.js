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
			    console.log(data);
			    $('#text').val(data['result']);
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

	// button for add admin
	$('body').on('click', '#addAdmin', function() {
		username = $('#username').val();
		password = $('#password').val();
		superAdmin = $('#superAdmin').is(':checked') ? 1 : 0;
		if ((username.trim() == "") || (password.trim() == "")) {
			$('#successAlert').hide()
			$('#errAlert').show();
			$('#errMessage').text('Username and Password must be filled');
		}
		else {
			$('#errAlert').hide();
			$('#errMessage').text('');
			$.ajax({
				url : '/admin/add',
				type : 'POST',
				data : {
					'username' : username,
					'password' : password,
					'superAdmin' : superAdmin
				},
				success : function(data) {
					if(data['message']=='success') {
						$('#errAlert').hide();
						$('#successAlert').show();
						$('#successMessage').text(data['username']+ ' has been added');
						$('#username').val("");
						$('#password').val("");
						$('#superAdmin').removeAttr('checked');
					}
					else {
						$('#successAlert').hide();
						$('#errAlert').show();
						$('#errMessage').text(data['message']);
					}
				}
			});
		}
		return false;
	});

	function getDataAdmin() {
		page = $('#currentPage').text();
        $.ajax({
            url : '/admin/dataAdmin',
            type : 'POST',
            data : { 'page': page },
            success : function(data) {
                // console.log(data)
                result = "";
                number = (page-1)*10;
                number+= 1
                for (var i = 0; i < data.length; i++) {
                    result += "<tr><td>"+(number++)+"</td><td>"+data[i].username+"</td><td><center>"+data[i].superAdmin+
                    "</center></td><td><center><button type='button' id='deleteDataAdmin' class='btn btn-danger btn-xs' value="+data[i].id+">Delete</button></center></td></tr>";
                }
                $('#adminData').html(result);
                pagination();
            }
        });
    }

	// button delete data admin
	$('body').on('click', '#deleteDataAdmin', function() {
		$.ajax({
			url : '/admin/delete',
			type : 'POST',
			data : { 'id':$(this).val() },
			success : function(data) {
				// console.log(data);
				getDataAdmin();
			}
		});
	});

	$('body').on('keyup', '#username', function() {
		page = $('#currentPage').text();
		$.ajax({
            url : '/admin/dataAdmin',
            type : 'POST',
            data : { 'username' : $(this).val() },
            success : function(data) {
                // console.log(data)
                result = "";
                number = (page-1)*10;
                number+= 1
                for (var i = 0; i < data.length; i++) {
                    result += "<tr><td>"+(number++)+"</td><td>"+data[i].username+"</td><td><center>"+data[i].superAdmin+
                    "</center></td><td><center><button type='button' id='deleteDataAdmin' class='btn btn-danger btn-xs' value="+data[i].id+">Delete</button></center></td></tr>";
                }
                $('#adminData').html(result);
            }
        });
	});
});
