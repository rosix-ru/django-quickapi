/**
 * jQuery QuickAPI plugin 2.0
 *
 * @author Grigoriy Kramarenko, 2014
 * @license GNU General Public License 3 <http://www.gnu.org/licenses/>
 * 
 */

(function ($) {
    /* Общая функция для работы с django-quickapi
     * 
     * Использование:
     * /все параметры необязательны и приведены здесь по-умолчанию/
     * 
     * $.quickAPI({
     *   url: "/api/", 
     *   args: {
     *     method: "name_your_method",
     *       kwargs: {
     *         method_param1: "value",
     *         ...
     *      },
     *   },
     *   type: "POST",
     *   sync: false,
     *   async: true,
     *   timeout: 3000,
     *   language: 'ru',
     *   log: undefined, // аргумент для console.log(...)
     *   callback: function(json, status, xhr) {},
     *   handlerShowAlert: function(head, msg, cls, cb) {//см. код ниже//},
     * })
     * 
     */
    $.quickAPI = function(options) {
        var options = options || new Object();
        
        options.args = options.args || { method: "quickapi.test" };

        var settings = {
                type: options.type || "POST",
                async: options.sync === true ? false : options.async === false ? false : true,
                timeout: options.timeout || window.AJAX_TIMEOUT || 3000,
                url: options.url || window.QUICKAPI_URL || '/api/',
                data: {
                    jsonData: $.toJSON(options.args),
                    language: options.language || window.LANGUAGE_CODE,
                },
                dataType: 'json',
            },
            callback = options.callback || function(json, status, xhr) {},
            showAlert = options.handlerShowAlert || window.handlerShowAlert ||
                function(head, msg, cls, cb) {
                    if ($.type(msg) == 'object') {
                        msg = $.toJSON(msg)
                            .replace(/\,\"/g, ', "')
                            .replace(/\"\:/g, '": ');
                    }
                    alert(head +'\n'+ msg);
                    if (cb) { return cb() };
                    return null;
                },
            jqxhr = $.ajax(settings)
                // Обработка ошибок протокола HTTP
                .fail(function(xhr, status, err) {
                    // Если есть переадресация, то выполняем её
                    if (xhr.getResponseHeader('Location')) {
                        var location = xhr.getResponseHeader('Location')
                            .replace(/\/[\#\-\w]*$/, "/?")
                            .replace(/\?.*$/, "?next=" + window.location.pathname);
                        window.location.replace(location);
                        console.info("REDIRECT:" + xhr.getResponseHeader('Location'));
                    } else {
                        if (xhr.responseText) {
                            // Иначе извещаем пользователя ответом и в консоль
                            console.error("ERROR:" + xhr.responseText);
                            var msg = (xhr.responseText.length <= 255) ?
                                xhr.responseText : xhr.responseText.substring(0, 255) + '...';
                            showAlert("ERROR:", msg, 'alert-danger');
                        };
                    };
                })
                // Обработка полученных данных
                .done(function(json, status, xhr) {
                    if (options.log && window.DEBUG) {console.debug(options.log)};
                    /* При переадресации нужно отобразить сообщение на некоторое время,
                     * а затем выполнить переход по ссылке, добавив GET-параметр для
                     * возврата на текущую страницу
                     */
                    if ((json.status >=300) && (json.status <400) && (json.data.Location != undefined)) {
                        var location = json.data.Location
                            .replace(/\/[\#\-\w]*$/, "/?")
                            .replace(/\?.*$/, "?next=" + window.location.pathname),
                            redirect = function() { window.location.replace(location) };
                        console.info("REDIRECT:" + location);
                        if (json.message) {
                            showAlert("REDIRECT:", json.message, 'alert-danger', redirect);
                        }
                        else { redirect() };
                    }
                    /* При ошибках извещаем пользователя полученным сообщением */
                    else if (json.status >=400) {
                        showAlert("ERROR:", json.message, 'alert-danger');
                    }
                    /* При нормальном возврате в debug-режиме выводим в консоль
                     * сообщение
                     */
                    else {
                        if (window.DEBUG) {
                            console.debug($.toJSON(json.message));
                            if (options.args.method == "quickapi.test") {
                                o = new Object;
                                $.extend(true, o, json.data);
                                console.debug(o);
                                showAlert('', o, 'alert-success');
                            };
                        };
                        return callback(json, status, xhr);
                    };
                });
        return jqxhr
    };

}(jQuery));
