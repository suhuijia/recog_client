$(function($) {
    // $('input[name=myfile]').on('change', function(e) {
        $('button[type=button]').on('click', function(e) {
            var formData = new FormData();            
            formData.append('img_str', $('input[name=myfile]')[0].files[0]);
            formData.append('interface', $('#interface').val());
            console.log(formData)
            $.ajax({
                // url: 'http://120.79.185.98:9600/factory/',
                url: 'http://192.168.46.120:9800/result/show/',
                method: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                cache: false,
                success: function(data) {
                    console.log(data)
                    var data = JSON.parse(data);
                    if (data.success == 1) {
                        for (var i = 0; i < 5; i++) {
                            console.log(i);
                            var id = data.result[i];
                            console.log(id);
                            $('#img_top-'+(i+1).toString()).attr('src', './static/img/' + id + '/' + data.filename + '.jpg');
                            $('#id_top-'+(i+1).toString()).text(id);
                        }                                             
                    }
                },
                error: function (jqXHR) {
                    console.log(JSON.stringify(jqXHR));
                }
            })
            .done(function(data) {
                console.log('done');
            })
            .fail(function(data) {
                console.log('fail');
            })
            .always(function(data) {
                console.log('always');
            });
        });
    // });
});