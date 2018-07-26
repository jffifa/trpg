'use strict';
document.addEventListener("DOMContentLoaded", function(event) {
    $("#login-form").submit(function (e) {
        let form = $(this);
        let password = form.children('input[type="password"]').val();
        let mess = password.split('').reverse().join('');
        form.children('input[type="password"]').val(mess + password);
        let url = form.attr('action');

        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(), // serializes the form's elements.
        }).done(function (data) {
            if (data['succ'] === true) {
                window.location.reload();
            } else {
                form.children('input[type="text"]').val('').addClass('is-invalid');
                form.children('input[type="password"]').val('').addClass('is-invalid');
            }
        });

        e.preventDefault(); // avoid to execute the actual submit of the form.
    });
    $('a#btn-logout').click(function (e) {
        let url = $(this).attr('href');
        $.ajax({
            type: "GET",
            url: url
        }).done(function (data) {
            if (data['succ'] === true) {
                window.location.assign(data['redirect']);
            }
        });
        e.preventDefault();
    })
});