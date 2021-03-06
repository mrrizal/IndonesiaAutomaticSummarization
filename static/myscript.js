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
			    if(data['success']!=null) {
			    	if(data['evaluationMainTopic']!= null) {
			    		swal({   
			    			title: "Save to database ?",   
			    			text: "Main Topic Score : "+data['evaluationMainTopic']+
				    		"\nTerm Significance Score : "+data['evaluationTermSignificance'],   
			    			type: "info",   
			    			showCancelButton: true,   
			    			confirmButtonColor: "#DD6B55",   
			    			confirmButtonText: "Save",   
			    			closeOnConfirm: false }, function(){   
			    				$.ajax({
			    					url : '/save_evaluation',
			    					type : 'POST',
			    					data : {
			    						'dtmMethod' : data['dtmMethod'],
			    						'sentenceSelectionMethod' : data['sentenceSelectionMethod'],
			    						'aspectRatio' : data['ratio'],
			    						'evaluationMainTopic' : data['evaluationMainTopic'],
			    						'evaluationTermSignificance' : data['evaluationTermSignificance']
			    					},
			    					success : function(data) {
			    						if(data=='success') {
			    							swal("Done", "Save to database", "success");	
			    						}
			    					}
			    				});
			    		});	
				    }
				    else {
				    	swal("Done", "", "success");	
				    }	
			    }
			    $('#text').val(data['result']);
			    $('#loader').hide();
       			$('#text').show();
			}
		})
	});

	// button save settings
	$('body').on('click', '#saveSettings', function(e) {
		e.preventDefault();
		ratio = $('#ratio :selected').val();
		dtm = $('#dtm :selected').val();
		sentenceSelection = $('#sentenceSelection :selected').val();
		formatFile = $('#formatFile :selected').val();
		evaluate = $('#evaluate').is(':checked') ? 1 : 0;
		if(ratio!=0 && dtm != 0 && sentenceSelection != 0 && formatFile != 0) {
			$.ajax({
				'url' : '/settings',
				'type' : 'POST',
				data : {
					'ratio' : ratio,
					'dtm' : dtm,
					'sentenceSelection' : sentenceSelection,
					'formatFile' : formatFile,
					'evaluate' : evaluate
				},
				success : function(data) {
					if(data=='sukses') {
						swal({   
							title: "success save settings !",   
							type : "success",   
							timer: 1000,   
							showConfirmButton: false 
						}, function() {
							window.location.reload();	
						});
						
					}
				}
			});
		}
		else {
			swal("Failed", "Fill all field !", "error")
		}
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

	function getAdminData(page, username) {
		//page = $('#currentPage').text();
        $.ajax({
            url : '/admin/admindata',
            type : 'POST',
            data : { 'page': page, 'username' : username },
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
    }

    function getEvaluationData(page, dtmMethod=0, sentenceSelectionMethod=0, aspectRatio=0, getTotalPage=0) {
    	//page = $('#currentPage').text();
        $.ajax({
            url : '/admin/evaluationdata',
            type : 'POST',
            data : {
            	'page':page, 
            	'dtmMethod' : dtmMethod, 
            	'sentenceSelectionMethod' : sentenceSelectionMethod, 
            	'aspectRatio' : aspectRatio,
            	'getTotalPage' : getTotalPage
            },
            success : function(data) {
            	if(getTotalPage!=0) {
            		currentPage = parseInt($('#currentPage').text());
            		totalPage = data['totalPage'];
            		if(totalPage==0) {
            			totalPage=1;
            		}
            		if(currentPage>totalPage) {
						currentPage = totalPage;
					} 
            		$('#pagination').twbsPagination('destroy');
					$('#pagination').twbsPagination({
						startPage : currentPage,
			            totalPages: totalPage,
			            visiblePages: 5,
			            onPageClick: function (event, page) {
			                getFilter2(page);
			                $('#currentPage').text(page);
			                // console.log('tes');
			            }
			        });
            		
            	}
            	else {
            		result = "";
	                for (var i = 1; i < data.length; i++) {
	                    result += " <tr><td>"+(parseInt(i)+((page-1)*10))+"</td><td>"+data[i].admin+"</td><td>"+data[i].dtmMethod+"</td><td>"+data[i].sentenceSelectionMethod+"</td><td><center>"+data[i].aspectRatio+" %</center></td><td>"+
	                    data[i].mainTopic+"</td><td>"+data[i].termSignificance+"</td><td><center><button type='button' class='btn btn-danger btn-xs' id='deleteDataEvaluation' value="+data[i].id+">Delete</button></center></td></tr>"
	                }
	                $('#evaluationData').html(result);	
	                $('#currentPage').text(page);
	            }
                
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
				getAdminData(page=1, username=$('#username').val());
				currentPage = parseInt($('#currentPage').text());
				totalPage = parseInt(data);
				if(currentPage>totalPage) {
					currentPage = totalPage;
				} 
				$('#pagination').twbsPagination('destroy');
				if($('#username').val()=="") {
					$('#pagination').twbsPagination({
						startPage : currentPage,
			            totalPages: totalPage,
			            visiblePages: 5,
			            onPageClick: function (event, page) {
			                getAdminData(page=page, username=$('#username').val());
			                $('#currentPage').text(page);
			                // console.log('tes');
			            }
			        });	
				}
				
			}
		});
	});

	// button delete data evaluation
	$('body').on('click', '#deleteDataEvaluation', function() {
		$.ajax({
			url : '/admin/evaluation_delete',
			type : 'POST',
			data : { 'id':$(this).val() },
			success : function(data) {
				// console.log(data);
				currentPage = parseInt($('#currentPage').text());
				totalPage = parseInt(data);
				if(totalPage==0) {
					totalPage=1;
				}
				if(currentPage>totalPage) {
					currentPage = totalPage;
				} 
				$('#pagination').twbsPagination('destroy');
				$('#pagination').twbsPagination({
					startPage : currentPage,
		            totalPages: totalPage,
		            visiblePages: 5,
		            onPageClick: function (event, page) {
		                getFilter(page);
		                $('#currentPage').text(page);
		                // console.log('tes');
		            }
		        });		
			}
		});
	});

	// search by username
	$('body').on('keyup', '#username', function() {
		getAdminData(page=1,username=$(this).val());

		if($(this).val()!="") {
			$('#pagination').twbsPagination('destroy');	
		}
		else {
			getAdminData(page=1);
			$.ajax({
				url : '/admin/admin_data',
				type : 'POST',
				success : function(data) {
					totalPage = data
					$('#pagination').twbsPagination({
			            totalPages: totalPage,
			            visiblePages: 5,
			            onPageClick: function (event, page) {
			                getAdminData(page);
			                $('#currentPage').text(page);
			                // console.log('tes');
			            }
			        });		
				}
			});
		}
	});

	// change password admin
	$('body').on('click', '#changePassword', function() {
		if($('#newPassword').val().trim()=="") {
			$('#errMessageChangePassword').text("New Password field blank");
			$('#successAlertChangePassword').hide();
			$('#errAlertChangePassword').show();
		}
		else {
			$.ajax({
				url : '/admin/change_password',
				type : 'POST',
				data : { 'newPassword' : $('#newPassword').val() },
				success : function(data) {
					if(data['message']=='success') {
						$('#successMessageChangePassword').text("Password has been changed");
						$('#errAlertChangePassword').hide();
						$('#successAlertChangePassword').show();
					}
				}
			});	
		}
		return false;
	});

	function getFilter2(page=1) {
		dtmMethod = $('#dtmMethod :selected').val();
		sentenceSelectionMethod = $('#sentenceSelectionMethod :selected').val();
		aspectRatio = $('#aspectRatio :selected').val();
		getEvaluationData(page=page, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, aspectRatio=aspectRatio);
			
	}

	// for filter evaluation
	function getFilter(page=1) {
		dtmMethod = $('#dtmMethod :selected').val();
		sentenceSelectionMethod = $('#sentenceSelectionMethod :selected').val();
		aspectRatio = $('#aspectRatio :selected').val();
		getEvaluationData(page=page, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, aspectRatio=aspectRatio);
		getEvaluationData(page=page, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, aspectRatio=aspectRatio, getTotalPage=1);		
	}

	// button filter on evaluation data page
	$('body').on('click', '#filterEvaluationData', function() {
		getFilter();
		return false;
	});

	function getEvaluationResult(page, dtmMethod=0, sentenceSelectionMethod=0, aspectRatio=0, getTotalPage=0) {
    	//page = $('#currentPage').text();
        $.ajax({
            url : '/admin/evaluationResult',
            type : 'POST',
            data : {
            	'page':page, 
            	'dtmMethod' : dtmMethod, 
            	'sentenceSelectionMethod' : sentenceSelectionMethod, 
            	'aspectRatio' : aspectRatio,
            	'getTotalPage' : getTotalPage
            },
            success : function(data) {
            	if(getTotalPage!=0) {
            		currentPage = parseInt($('#currentPage').text());
            		totalPage = data['totalPage'];
            		if(totalPage==0) {
            			totalPage=1;
            		}
            		if(currentPage>totalPage) {
						currentPage = totalPage;
					} 
            		$('#pagination').twbsPagination('destroy');
					$('#pagination').twbsPagination({
						startPage : currentPage,
			            totalPages: totalPage,
			            visiblePages: 5,
			            onPageClick: function (event, page) {
			                getFilterEvaluationResult2(page);
			                $('#currentPage').text(page);
			                // console.log('tes');
			            }
			        });
            		
            	}
            	else {
            		result = "";
                    for (var i = 1; i < data.length; i++) {
                        result += " <tr><td>"+(parseInt(i)+((page-1)*10))+"</td><td>"+data[i].dtmMethod+"</td><td>"+
                        data[i].sentenceSelectionMethod+"</td><td>"+data[i].aspectRatio+
                        "</td><td><center>"+parseFloat(data[i].max_mainTopic).toFixed(4)+
                        " </center></td><td><center>"+parseFloat(data[i].min_mainTopic).toFixed(4)+
                        " </center></td><td><center>"+parseFloat(data[i].avg_mainTopic).toFixed(4)+
                        " </center></td><td><center>"+parseFloat(data[i].max_termSignificance).toFixed(4)+
                        " </center></td><td><center>"+parseFloat(data[i].min_termSignificance).toFixed(4)+
                        " </center></td><td><center>"+parseFloat(data[i].avg_termSignificance).toFixed(4)+
                        " </center></td></tr>"
                    }
                    $('#evaluationResult').html(result);
                    $('#currentPage').text(page);
	            }
                
            }
        });
    }

    function getFilterEvaluationResult2(page=1) {
		dtmMethod = $('#dtmMethod :selected').val();
		sentenceSelectionMethod = $('#sentenceSelectionMethod :selected').val();
		aspectRatio = $('#aspectRatio :selected').val();
		getEvaluationResult(page=page, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, aspectRatio=aspectRatio);
			
	}

	// for filter evaluation
	function getFilterEvaluationResult(page=1) {
		dtmMethod = $('#dtmMethod :selected').val();
		sentenceSelectionMethod = $('#sentenceSelectionMethod :selected').val();
		aspectRatio = $('#aspectRatio :selected').val();
		getEvaluationResult(page=page, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, aspectRatio=aspectRatio);
		getEvaluationResult(page=page, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, aspectRatio=aspectRatio, getTotalPage=1);		
	}

	// button filter on evaluation result page
	$('body').on('click', '#filterEvaluationResult', function() {
		getFilterEvaluationResult();
		return false;
	});

	// save summarization result
	$('body').on('click', '#saveResult', function() {
		if($('#text').val().trim()!="") {
			swal({   
				title: "Input File Name!",   
				type: "input",   
				showCancelButton: true,   
				closeOnConfirm: false,   
				animation: "slide-from-top",   
				inputPlaceholder: "Write something" 
			}, 
			function(inputValue){   
				if (inputValue === false) 
					return false;      
				if (inputValue === "") {     
					swal.showInputError("You need to write something!");     
					return false   
				}      
				formatFile = $('#formatFileValue').text();
				if (formatFile=="pdf") {
					data = $('#text').val().replace(/\r\n|\r|\n/g,"<br />");
					$.ajax({
						url : '/saveResult',
						type : 'POST',
						data : { 'result' : data, 'fileName' : inputValue+".pdf" },
						success : function(data) {
							console.log(data);
							window.location.href = '/getPDF/'+inputValue+".pdf";
						}
					});	
				}
				else {
					data = $('#text').val();
					var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
					saveAs(blob, inputValue+".txt");
				}
				swal("Done!","","success"); 
			});	
		}	
	});
});
