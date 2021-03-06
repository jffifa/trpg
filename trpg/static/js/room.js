'use strict';
document.addEventListener("DOMContentLoaded", function(event) {
    // csrf ajax
    {
        let getCookie = function(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                let cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = $.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };
        let csrftoken = getCookie('csrftoken');
        let csrfSafeMethod = function(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        };
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    // current character name
    {
        window.TrpgEnv['cur_char_id'] = $('#characters-tab>.active[data-toggle="pill"]').data('characterId');
        window.TrpgEnv['cur_char_name'] = $('#characters-tab>.active[data-toggle="pill"]').data('characterName');
        $('#characters-tab>[data-toggle="pill"]').on('shown.bs.tab', function (e) {
            window.TrpgEnv['cur_char_id'] = $(e.target).data('characterId');
            window.TrpgEnv['cur_char_name'] = $(e.target).data('characterName');
        });
    }

    // side panel
    {
        $('input#silent-mode-switch').change(function (e) {
            var checkbox = $(this);
            var checked = checkbox.prop('checked');
            var data = {
                'mode_name':'silent',
                'mode_value': checked?1:0
            };
            $.ajax({
                type: 'POST',
                url: window.TrpgEnv['mode_change_url'],
                data: data,
                timeout: 1000
            }).done(function(data, textStatus, jqXHR){
                if (data['succ'] !== true) {
                    checkbox.prop('checked', !checked);
                }
            }).fail(function(jqXHR, textStatus, errorThrown){
                // do some fail log
                checkbox.prop('checked', !checked);
            });
        });
        $('#room-character-panel>button.character-expand').hide();
        $('#room-character-panel>button.character-collapse').click(function(e) {
            $('#characters-tabContent').hide();
            $(this).hide();
            $('#room-character-panel>button.character-expand').show();
            $('#room-character-panel').addClass('character-collapse');
        });
        $('#room-character-panel>button.character-expand').click(function(e) {
            $('#room-character-panel').removeClass('character-collapse');
            $(this).hide();
            $('#characters-tabContent').show();
            $('#room-character-panel>button.character-collapse').show();
        });
    }

    // records staff
    {
        let roomName = window.TrpgEnv['room_name'];
        let pullUrl = window.TrpgEnv['pull_url'];
        let pullInterval = 1000;

        let pullRecords = function() {
            let lastRecordID = window.TrpgEnv['last_record_id'];
            if (typeof lastRecordID === 'undefined') {
                lastRecordID = null;
            }
            let data = {'last_record_id':lastRecordID};
            return $.ajax({
                type: 'GET',
                url: pullUrl,
                data: data,
                timeout: pullInterval*2
            });
        };

        let genRollHtml = function(record) {
            // who
            let text = `<span class="roll-char text-secondary">${record['char']['char_name']}</span>`;
            text += '投掷了';

            // roll cmd
            if (record['details']['roll_hidden']) {
                text += '一次暗投';
                if (!record['details']['roll_show']) {
                    return text;
                }
            }
            text += `<span class="roll-cmd text-info">${record['details']['raw_roll_cmd']}</span>`;

            let _v;
            //against
            if (record['details']['roll_against']['comment']) {
                text += '对';
                // whose?
                if ((_v = record['details']['roll_against']['char_name']) && 
                    _v !==record['char']['char_name']) {
                    text += `<span class="roll-against-char text-secondary">${_v}</span>的`
                }
                text += `<span class="roll-against-prop text-info">${record['details']['roll_against']['comment']}</span>`;
                if (_v = record['details']['roll_against']['value_str']) {
                    text += `<span class="roll-against-value text-info">(${_v})</span>`
                }
                text += '进行检定';
            }
            
            //result
            text += `，结果为<span class="roll-result text-info">${record['details']['roll_result_text']}</span>`;
            if (_v = record['details']['roll_result_desc']['result']) {
                let desc, txtClass;
                switch (_v) {
                    case 'succ':
                        desc = '成功';
                        txtClass = 'text-success';
                        break;
                    case 'fail':
                        desc = '失败';
                        txtClass = 'text-danger';
                        break;
                    case 'g_succ':
                        desc = '大成功';
                        txtClass = 'text-success';
                        break;
                    case 'g_fail':
                        desc = '大失败';
                        txtClass = 'text-danger';
                        break;
                }
                text += `<span class="roll-result-desc ${txtClass}">(${desc})</span>`;
            }
            return text;
        };

        let genMsg = function(record) {
            let result;
            switch (record['record_type']) {
                case 'talk':
                    result = $('<p>').addClass('col media-text record-msg');
                    result.data('msgId', record['record_id']);
                    result.text(record['details']['message']);
                    if ('send_to_char_ids' in record['details']) {
                        let sendToSpan = $('<span>').addClass('text-secondary mr-1');
                        let send_to_str = '(私下对 ';
                        send_to_str += record['details']['send_to_char_names'].join(', ');
                        send_to_str += ' 说)';
                        sendToSpan.text(send_to_str);
                        result.prepend(sendToSpan);
                    }
                    // get raw html and replace line breaks
                    let rawHtml = result.html();
                    rawHtml = rawHtml.replace(/(\r?\n)+/, '<br>');
                    result.html(rawHtml);
                    break;
                case 'roll':
                    result = $('<p>').addClass('col media-text record-roll');
                    result.data('msgId', record['record_id']);
                    result.html(genRollHtml(record));
                    break;
            }
            return result;
        };

        let genMsgContainter = function(msgPara, char) {
            let msgBody = $('<div>').addClass('media-body');
            let msgChar = $('<h6>').addClass('msg-heading').text(char['char_name']);
            if (char['char_type']==='admin') {
                msgChar.addClass('text-danger');
            } else if (char['char_type']==='pc') {
                var is_self = window.TrpgEnv['characters'].some(function (e) {
                   return char['char_id']===e['char_id'] && e['control_by_user'];
                });
                if (is_self) {
                    msgChar.addClass('text-success');
                } else {
                    msgChar.addClass('text-primary');
                }
            }
            msgBody.append(msgChar);
            msgBody.append(msgPara);
            let msgContainer = $('<div>').addClass('media msg msg-normal').data('charId', char['char_id']);
            msgContainer.append(msgBody);
            return msgContainer;
        };
        
        let processSysMsg = function (record) {
            const MODE_FLAG_SILENT = 0x1;
            let details = record['details'];

            switch (details['type']) {
                case 'mode_change':
                    let silent = details['mode_flag'] & MODE_FLAG_SILENT;
                    if (silent && !window.TrpgEnv['is_admin']) {
                        $('#msg-form input:submit').prop('disabled', true);
                        $('#roll-form input:submit').prop('disabled', true);
                    } else {
                        $('#msg-form input:submit').prop('disabled', false);
                        $('#roll-form input:submit').prop('disabled', false);
                    }
                    break;
            }
        };
        
        let genSysMsgContainer = function(record) {
            let msgBody = $('<strong>').text(record['pure_text']);
            let msgContainer = $('<div>').addClass('alert alert-info msg msg-sys');
            msgContainer.append(msgBody);
            return msgContainer;
        };

        let parseRecords = function(data) {
            if (data['succ'] === true && data['records'].length > 0) {
                // remove old ones
                const MAX_MSG_COUNT = 256;
                let msgWrap = $('#msg-wrap');
                let msgs = msgWrap.children('.msg');
                if (msgs.length > MAX_MSG_COUNT) {
                    msgs.slice(0, msgs.length-MAX_MSG_COUNT).remove();
                }

                let prevMsgContainer = $('#msg-wrap>.msg:last');
                data['records'].forEach(function(record) {
                    window.TrpgEnv['last_record_id'] = record['record_id'];
                    if (record['record_type'] === 'sys') {
                        processSysMsg(record);
                        let msgContainer = genSysMsgContainer(record);
                        msgWrap.append(msgContainer);
                        prevMsgContainer = msgContainer;
                    } else {
                        // check if record should show
                        if (record['record_type'] === 'talk' && 'send_to_char_ids' in record['details']) {
                            var show = window.TrpgEnv['characters'].some(function(e){
                                return e['control_by_user'] && (
                                    record['char']['char_id']===e['char_id'] ||
                                    record['details']['send_to_char_ids'].indexOf(e['char_id'])>=0);
                            });
                            if (!show) return;
                        }

                        let msg = genMsg(record);
                        if (record['char']['char_id'] === prevMsgContainer.data('charId')) {
                            prevMsgContainer.children('.media-body').append(msg);
                        } else {
                            let msgContainer = genMsgContainter(msg, record['char']);
                            msgWrap.append(msgContainer);
                            prevMsgContainer = msgContainer;
                        }
                    } 
                });
                if (data['records'].length>0 && prevMsgContainer.length>0) {
                    prevMsgContainer[0].scrollIntoView(false);
                }
            }
        };

        let process = function() {
            pullRecords().done(function(data, textStatus, jqXHR){
                parseRecords(data);
                setTimeout(process, pullInterval);
            }).fail(function(jqXHR, textStatus, errorThrown){
                // do some fail log
                setTimeout(process, pullInterval*2);
            });
        };
        process();

        // clear button
        $('#msg-clear').click(function (e) {
            let msgs = $('#msg-wrap>.msg');
            msgs.remove();
        })
    }

    // roll panel staff
    // auto fill roll panel
    {
        $('.sortable').sortable({
            placeholder: 'col-4 mb-1 sortable-placeholder',
            tolerance: 'pointer',
        });
        $('.sortable').disableSelection();

        $('.char-prop').click(function (e) {
            let prop = $(this);
            let key = prop.find('.char-prop-key').text();
            let val = prop.find('.char-prop-val').text();
            let mark = prop.find('.char-prop-mark').val();
            if (!isNaN(parseInt(mark))) {
                val += mark;
            }
            let currentChar = window.TrpgEnv['cur_char_name'];

            $('#roll-against').val(`{c:${currentChar}}{v:${val}}${key}`);
        });
    }

    // msg-form panel
    {
        $('#send-to .button-checkbox').each(function () {
            // Settings
            var $widget = $(this),
                $button = $widget.find('button'),
                $checkbox = $widget.find('input:checkbox'),
                color = $button.data('color');

            // Event Handlers
            $button.on('click', function () {
                $checkbox.prop('checked', !$checkbox.prop('checked'));
                $checkbox.triggerHandler('change');
                updateDisplay();
            });
            $checkbox.on('change', function () {
                updateDisplay();
            });

            // Actions
            function updateDisplay() {
                var isChecked = $checkbox.prop('checked');

                // Update the button's color
                if (isChecked) {
                    $button.removeClass('btn-default').addClass(`btn-${color}`)
                        .addClass('active').prop('aria-pressed', 'true');
                } else {
                    $button.removeClass('active').removeClass(`btn-${color}`)
                        .addClass('btn-default').prop('aria-pressed', 'false');
                }
            }

            // Initialization
            updateDisplay();
        });
        //for toggle-all
        {
            var $widget = $('#send-to-toggle-all'),
                $button = $widget.find('button');
            $button.click(function () {
                var $self = $(this);
                var state = $self.data('state');
                if (state === 'on') {
                    $self.data('state', 'off');
                    $self.find('i').removeClass().addClass('far fa-square');
                    $('#send-to .button-checkbox.send-to-toggle-list input:checkbox').prop('checked', false).trigger('change');
                } else {
                    $self.data('state', 'on');
                    $self.find('i').removeClass().addClass('far fa-check-square');
                    $('#send-to .button-checkbox.send-to-toggle-list input:checkbox').prop('checked', true).trigger('change');
                }
            });
        }
    }

    // msg-form
    {
        window.TrpgEnv['msg_submit_key'] = $('#msg-form select.msg-submit-choice').val();
        $('#msg-form select.msg-submit-choice').change(function (e) {
            window.TrpgEnv['msg_submit_key'] = this.value;
        });

        $('#msg-box').keydown(function (e) {
            if (e.keyCode == 13) {
                if (window.TrpgEnv['msg_submit_key']!=='ctrlenter' || e.ctrlKey) {
                    $('#msg-form').trigger('submit');
                    e.preventDefault();
                }
            }
        });

        $('#msg-form').submit(function (e) {
            e.preventDefault();
            if (!this.checkValidity()) {
                return;
            }
            
            let form = $(this);
            let msg = form.find('#msg-box').val();
            let curCharId = window.TrpgEnv['cur_char_id'];
            let curCharName = window.TrpgEnv['cur_char_name'];
            let data = {
                'msg': msg,
                'cur_char_id': curCharId,
                'cur_char_name': curCharName
            };
            
            //check send-to
            var sendToCharIds = [];
            var sendToAll = true;
            $('#send-to .send-to-toggle-list').each(function(){
                var self = $(this);
                var checkbox = self.find('input:checkbox');
                if (checkbox.prop('checked')) {
                    sendToCharIds.push(self.data('characterId'));
                } else {
                    sendToAll = false;
                }
            });
            if (sendToCharIds.length === 0) return;
            if (!sendToAll) {
                data['send_to_char_ids'] = sendToCharIds;
            }

            if (curCharId) {
                let url = form.attr('action');
                form.find('.btn').prop('disabled', true);
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: data,
                    timeout: 2000
                }).done(function(data) {
                    form.find('#msg-box').val('');
                    form.find('.btn').prop('disabled', false);
                }).fail(function(jqXHR, textStatus, errorThrown){
                    form.find('.btn').prop('disabled', false);
                    // TODO: some fail log
                });
            }
        });
    }

    // roll-form
    {
        let submitRollForm = function(form, rollHidden=false) {
            let rollCmd = form.find('#roll-cmd').val();
            let rollAgainst = form.find('#roll-against').val();
            let curCharId = window.TrpgEnv['cur_char_id'];
            let curCharName = window.TrpgEnv['cur_char_name'];

            if (curCharName) {
                let url = form.attr('action');
                form.find('.btn').prop('disabled', true);
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: {
                        'roll_cmd': rollCmd,
                        'roll_against': rollAgainst,
                        'cur_char_id': curCharId,
                        'cur_char_name': curCharName,
                        'roll_hidden': rollHidden
                    },
                    timeout: 2000
                }).done(function(data) {
                    form.find('.btn').prop('disabled', false);
                }).fail(function(jqXHR, textStatus, errorThrown){
                    form.find('.btn').prop('disabled', false);
                    // TODO: some fail log
                });
            }
        };

        $('#roll-form').submit(function (e) {
            let form = $(this);
            submitRollForm(form);
            e.preventDefault();
        });
        $('#roll-form-roll-hidden').click(function (e) {
            let form = $('#roll-form');
            submitRollForm(form, true);
        })
    }
    
});
