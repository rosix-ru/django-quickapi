/**
 * jquery.quickapi.js - jQuery plugin for QuickAPI application
 * 
 * Copyright 2014-2015 Grigoriy Kramarenko <root@rosix.ru>
 *
 * This file is part of QuickAPI.
 *
 * QuickAPI is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License
 * as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * QuickAPI is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public
 * License along with QuickAPI. If not, see
 * <http://www.gnu.org/licenses/>.
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
     *   data: {
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
     *   simple_request: undefined, // аргумент для передачи данных
     *                              // в простом виде (не в jsonData)
     *   callback: function(json, status, xhr) {},
     *   handlerShowAlert: function(head, msg, cls, cb) {//см. код ниже//},
     * })
     * 
     */

    $.quickAPI = function(opts) {

        var data, options = opts || new Object();

        // `args` is deprecation option
        if (!options.data) options.data = options.args || { method: "quickapi.test" };

        if (options.simple_request) {

            data = options.data;
            if (!data.language) data.language = options.language || window.LANGUAGE_CODE

        } else {

            data = {
                jsonData: $.toJSON(options.data),
                language: options.language || window.LANGUAGE_CODE
            }

        }

        var jqxhr,
            settings = {
                type: options.type || "POST",
                async: options.sync === true ? false : options.async === false ? false : true,
                timeout: options.timeout || window.AJAX_TIMEOUT || 3000,
                url: options.url || window.QUICKAPI_URL || '/api/',
                data: data,
                dataType: 'json',
            },
            callback = options.callback || function(json, status, xhr) {},
            showAlert = options.handlerShowAlert || window.handlerShowAlert || function(head, msg, cls, cb) {

                var match;

                if ($.type(msg) == 'object') {
                    msg = $.toJSON(msg)
                                .replace(/\,\"/g, ', "')
                                .replace(/\"\:/g, '": ')
                }
                else if (msg.match(/<\!DOCTYPE/)) {
                    match = msg.match(/<[title,TITLE]+>(.*)<\/[title,TITLE]+>/);
                    if (match) head = match[1];

                    match = msg.match(/<[body,BODY]+>([^+]*)<\/[body,BODY]+>/);
                    if (match) msg = match[1]
                                    .replace(/<\/?[^>]+>/g, '')
                                    .replace(/ [ ]+/g, ' ')
                                    .replace(/\n[\n]+/g, '\n')
                }

                if (msg.length > 512) {
                    msg = msg.substring(0, 512) + ' ...'
                };

                alert(head +'\n'+ msg);

                if (cb) { return cb() };

                return null
            };

        jqxhr = $.ajax(settings)
                // Обработка ошибок протокола HTTP
                .fail(function(xhr, status, err) {

                    // Если есть переадресация, то выполняем её
                    if (xhr.getResponseHeader('Location')) {

                        location.replace(xhr.getResponseHeader('Location'));

                    } else if (xhr.responseText) {
                        // Иначе извещаем пользователя ответом и в консоль
                        console.error("ERROR:", xhr.responseText);

                        showAlert("ERROR:", xhr.responseText, 'alert-danger')
                    }
                })

                // Обработка полученных данных
                .done(function(json, status, xhr) {

                    if (options.log && window.DEBUG) {console.debug(options.log)};

                    /* При переадресации нужно отобразить сообщение на некоторое время,
                     * а затем выполнить переход по ссылке
                     */
                    if ((json.status >=300) && (json.status <400) && (json.data.Location != undefined)) {

                        var loc = json.data.Location, redirect;

                        redirect = function() { location.replace(loc) };

                        console.info("REDIRECT:" + loc);

                        if (json.message) {
                            showAlert("REDIRECT:", json.message, 'alert-danger', redirect)
                        } else {
                            redirect()
                        }
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

                            if (options.data.method == "quickapi.test") {
                                console.debug(json.data)
                            }
                        };

                        return callback(json, status, xhr)
                    }
                });

        return jqxhr
    }

}(jQuery));


