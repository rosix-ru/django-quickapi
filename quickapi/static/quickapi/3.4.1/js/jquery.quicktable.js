/* 
 * jquery.quicktable.js - jQuery plugin for QuickAPI application
 * 
 * depends:
 *      jquery.quickapi.js - jQuery plugin for QuickAPI
 * recommends:
 *      Twitter bootstrap >= 3.0
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
    /* Главным условием работы является наличие id у таблицы, а также
     * переданных опций: url, method и columns.
     * 
     * Заметьте, что id таблицы используется для нахождения всех
     * зависимых объектов.
     * 
     * ПРИМЕР:
     * <table id="my-table">
     *   <thead><tr><th>Username</th></tr></thead>
     *   <tbody></tbody>
     * </table>
     * 
     * <script>
     *   var table = $('#my-table').quickTable({
     *     url: '/api/',
     *     method: 'auth.quicktable_users',
     *     columns: [
     *       { name: "id", hidden: true, notmanaged: true },
     *       { name: "username", title: "Username" },
     *     ]
     *   });
     * <script>
     * 
     */
    var pluginName="quickTable";

    $.fn[pluginName] = function(options) {

        if (!this.size()) { console.error('The selector found nothing'); return undefined };

        if ((!options.url && !window.QUICKAPI_URL) || !options.method) {
            console.error(
                "Not valid options for "+pluginName,
                {url:options.url, method:options.method, QUICKAPI_URL: window.QUICKAPI_URL}
            );
        };

        if ($.type(options.columns) != 'array' || $.isEmptyObject(options.columns)) {

            console.error(
                "Not valid options for "+pluginName,
                {columns:options.columns},
                'columns must be not empty array!'
            );

            console.info('EXAMPLE:\n',
            'columns = [ {name:"id", hidden:true, notmanaged:true}, {name:"name", title:"Name"} ]\n',
            'where `name` - object attribute, `hidden` - hidden column,',
            ' `notmanaged` - the column is not managed, `title` - title of column.'
            );

        };


        var table = this[0], id, opts;

        id = $(table).attr('id');
        if (!id) { return this }; // not valid

        opts = $.extend({
            url: window.QUICKAPI_URL,
            method: undefined,
            columns: undefined,
            type: 'POST',
            timeout: 10000,
            async: true,
            autoload: true,
            autorender_settings: true,
            delay: 500,
            page: 1,
            limit: 25,
            limit_list: [25, 50, 75, 100],
            filters: {},
            ordering: [],
            multiordering: false,
            table_type: 'table', // variants: 'stack' or 'pager'
            text_pager_prev: '&laquo;',
            text_pager_next: '&raquo;',
            // the following variables are strongly advised not to change
            _selector_filtering: '[data-filtering='+id+']',
            _selector_ordering: '#'+id+' th[class^=sorting][name]',
            _selector_limiting: 'input[data-limiting='+id+']:checked, select[data-limiting='+id+']',
            _selector_colswitcher: 'input[data-colswitcher='+id+']',
            _selector_settings: '#'+id+'_settings',
            _selector_pager: '#'+id+'_pager',
            _selector_pager_links: '#'+id+'_pager li:not(.disabled) a:not(.disabled)',
            _selector_info: '#'+id+'_info',
            _selector_thead: '#'+id+' thead',
            _selector_tbody: '#'+id+' tbody',
            _selector_alert_not_found: '[data-notfound='+id+']',
            _default_filter_key: '_search_',
            _managed_columns: [],
            _column_names: {},
        }, options);

        table.opts = opts; // link
        table.request = null; // current jqxhr
        table.fn = {}; // storage for functions

        opts.replace = true; // append or overwrite tbody

        $.each(opts.columns, function(i, col) {
            opts._column_names[col.name] = col;
            if (col.hidden) $(table).addClass('table-col-'+(i+1)+'-hidden');
        });

        /*** START FUNCTIONS ***/

        /* Delay for keyup in filters */
        table.fn.delay = (function(){

            var tid = 0;

            return function(callback, ms){
                clearTimeout(tid);
                tid = setTimeout(callback, ms);
            };

        })();

        /* Twitter bootstrap .pager as stack */
        table.fn._render_bs_stack = function(page, num_pages) {

            var p = opts._selector_pager, a = opts._selector_pager_links;

            if (page < num_pages) {
                $(a).data('page', (page+1));
                $(p).show();
            } else {
                $(a).data('page', '');
                $(p).hide();
            }
        };

        /* Twitter bootstrap .pager inner HTML */
        table.fn._render_bs_pager = function(page, num_pages, hide_prev) {

            var html = '', tp = opts.text_pager_prev, tn = opts.text_pager_next;

            if (page >1 && !hide_prev) {
                html += '<li><a href="#" data-page="'+(page-1)+'">'+tp+'</a></li>';
            } else {
                html += '<li class="disabled"><span>'+tp+'</span></li>';
            }

            if (page < num_pages) {
                html += '<li><a href="#" data-page="'+(page+1)+'">'+tn+'</a></li>';
            } else {
                html += '<li class="disabled"><span>'+tn+'</span></li>';
            }

            $(opts._selector_pager).html(html);

        };

        /* Twitter bootstrap .pagination inner HTML */
        table.fn._render_bs_pagination = function(page, num_pages, on_each_side, on_ends) {

            var html = '',
                on_each_side=on_each_side||3,
                on_ends=on_ends||2,
                dot='.',
                page_range = [],
                _push;

            if (page >1) {
                html += '<li><a href="#" data-page="'+(page-1)+'">'+opts.text_pager_prev+'</a></li>';
            } else {
                html += '<li class="disabled"><span>'+opts.text_pager_prev+'</span></li>';
            }

            _push = function(s, e) { for(var i=s; i<e; i++) { page_range.push(i) } };

            if (num_pages > 9) {

                if (page > (on_each_side + on_ends)) {
                    _push(1, on_each_side);
                    page_range.push(dot);
                    _push(page+1-on_each_side, page+1);
                } else {
                    _push(1, page+1)
                }

                if (page < (num_pages - on_each_side - on_ends + 1)) {
                    _push(page+1, page+on_each_side);
                    page_range.push(dot);
                    _push(num_pages-on_ends+1, num_pages+1);
                } else {
                    _push(page+1, num_pages+1)
                }
            } else {
                page_range = $.map($(Array(num_pages)), function(val, i) { return i+1; })
            };

            $.each(page_range, function(i, item) {

                if (item == dot) {
                    html += '<li class="disabled"><span>...</span></li>';
                } else if (item == page) {
                    html += '<li class="active"><span>'+page+'</span></li>';
                } else {
                    html += '<li><a href="#" data-page="'+item+'">'+item+'</a></li>';
                }

            });

            if (page < num_pages) {
                html += '<li><a href="#" data-page="'+(page+1)+'">'+opts.text_pager_next+'</a></li>';
            } else {
                html += '<li class="disabled"><span>'+opts.text_pager_next+'</span></li>';
            }

            $(opts._selector_pager).html(html);

        };

        /* Use default pagination */
        table.fn.render_pager = function(page, num_pages) {

            if (opts.table_type == 'stack') {
                return table.fn._render_bs_stack(page, num_pages)
            }
            else if (opts.table_type == 'pager') {
                return table.fn._render_bs_pager(page, num_pages, true)
            }

            return table.fn._render_bs_pagination(page, num_pages);

        }

        /* Show/hide not found text */
        table.fn.alert_not_found = function(show) {

            var $alert = $(opts._selector_alert_not_found);

            show ? $alert.show() : $alert.hide();
        };

        /* Rendering information */
        table.fn.render_info = function(html) {
            $(opts._selector_info).html(html);
        };

        /* Rendering settings */
        table.fn.render_settings = function() {

            var html = '';

            $.each(opts.columns, function(i, col) {

                if (!col.notmanaged) {
                    html += '<label>'
                         +'<input type="checkbox" name="'+id+'_colswitcher" value="'+(i+1)+'" '
                         +(!col.hidden ? ' checked' : '')+'/>'
                         +(col.title||col.name)
                         +'</label>'
                }

            });

            html += '<div class="btn-group" data-toggle="buttons">'

            $.each(opts.limit_list, function(i, limit) {

                html += '<label class="btn'+(opts.limit == limit ? ' active': '')+'">'
                        +'<input type="checkbox" name="'+id+'_limit" '
                        +(opts.limit == limit ? ' checked': '')+'>'
                        + limit
                        +'</label>'

            });

            html += '</div>'

            $(opts._selector_settings).html(html);

        };

        /* Returns class for <tr> */
        table.fn.get_class_tr = function(object) { return object ? '' : 'danger' };

        /* Rendering one object */
        table.fn.render_object = function(index, object) {

            if (object == null) return;

            var html = '';

            html += '<tr class="'+table.fn.get_class_tr(object)+'">';

            $.each(opts.columns, function(i, col) {

                html += '<td>'+object[col.name]+'</td>';

            });

            html += '</tr>';

            $(opts._selector_tbody).append(html);

        };

        /* Callback of jqxhr. Rendering all objects, pagination, etc. */
        table.fn.render = function(json, replace) {

            var data = json.data;

            if (replace) $(opts._selector_tbody).html('');

            if ($.isEmptyObject(data.objects)) {
                table.fn.alert_not_found(true)
            } else {
                table.fn.alert_not_found(false)
                $.each(data.objects, function(i, item) {
                    table.fn.render_object(i, item)
                })
            }

            table.fn.render_pager(data.page, data.num_pages);

            if (data.info) table.fn.render_info(data.info);

        };

        /* Request to server on quickAPI. Returns jqxhr. */
        table.fn.get = function(filters) {

            var replace = opts['replace'], F = filters || {};

            if (table.request) table.request.abort();

            table.request = $.quickAPI({
                url: opts.url,
                timeout: opts.timeout,
                type: opts.type,
                async: opts.async,
                args: {
                    method: opts.method,
                    kwargs: {
                        filters: $.extend({}, opts.filters, F),
                        ordering: opts.ordering,
                        page: opts.page,
                        limit: opts.limit,
                    },
                },
                callback: function(json, status, xhr) { return table.fn.render(json, replace) },
                showAlert: opts.showAlert,
            })
            .always(function() {table.request = null});

            return table.request

        };

        /* Request to server from first page by force. */
        table.fn.get_first_page = function(filters) {

            opts.page = 1;
            opts.replace = true;

            return table.fn.get(filters);

        };

        /*** END FUNCTIONS ***/

        /*** START BINDING TABLE CONTROLLERS ON DOCUMENT BODY ***/

        $('body')

        /* Keyup on filters */
        .off('keyup', opts._selector_filtering)
        .on('keyup', opts._selector_filtering, function(e) {

            var fname = this.name || opts._default_filter_key,
                old = opts.filters[fname],
                min = Number($(this).data('minimum')) || 0,
                len = this.value.length;

            if (this.value != old && (!len || len >= min)) {

                opts.filters[fname] = this.value;
                table.fn.delay(table.fn.get_first_page, opts.delay);

            }

        })

        /* Change limit on page */
        .off('change', opts._selector_limiting)
        .on('change', opts._selector_limiting, function(e) {

            opts.limit = this.value;
            table.fn.get_first_page();

        })

        /* Change visible of column */
        .off('change', opts._selector_colswitcher)
        .on('change', opts._selector_colswitcher, function(e) {

            var n = this.value,
                cls = 'table-col-'+n+'-hidden';

            if (!n) return;

            if (this.checked) {
                $(table).removeClass(cls);
                opts.columns[n-1].hidden = false;
            } else {
                $(table).addClass(cls);
                opts.columns[n-1].hidden = true;
            }

        })

        /* Change ordering on columns */
        .off('click', opts._selector_ordering)
        .on('click', opts._selector_ordering, function(e) {

            var column = $(this).attr('name'), L, i;
            
            if (!column) return;

            L = opts.ordering;
            i = $.inArray(column, L);

            if (!opts.multiordering) {
                $(opts._selector_ordering).removeClass('sorting-asc')
                                             .removeClass('sorting-desc')
                                             .addClass('sorting');
            }

            if (i > -1) {
                //~ console.debug('exists', i, column);
                if (!opts.multiordering) {
                    L = ['-'+column];
                } else {
                    L[i] = '-'+column;
                }

                $(this).removeClass('sorting').addClass('sorting-desc');
            } else {
                //~ console.debug('not exists', i, column);
                i = $.inArray('-'+column, L);
                if (i > -1) {
                    //~ console.debug('remove', i, '-'+column);
                    if (!opts.multiordering) {
                        L = [];
                    } else {
                        L = L.slice(0,i).concat(L.slice(i+1));
                    }

                    $(this).removeClass('sorting-desc').addClass('sorting');
                }
            }

            if (i == -1){
                //~ console.debug('not exists', i, '-'+column);
                if (!opts.multiordering) {
                    L = [column];
                } else {
                    L.push(column);
                }

                $(this).removeClass('sorting').addClass('sorting-asc');
            }

            opts.ordering = L;

            table.fn.get_first_page();

        })

        /* Click on pagination */
        .off('click', opts._selector_pager_links)
        .on('click', opts._selector_pager_links, function(e) {

            e.preventDefault();
            opts.page = $(this).data('page');
            if (opts.table_type == 'stack') { opts.replace = false };
            table.fn.get();

        });

        /*** END BINDING TABLE CONTROLLERS ***/

        /* Starting table */
        if (opts.autorender_settings) table.fn.render_settings();
        if (opts.autoload) table.fn.get_first_page();
 
        return table;
 
    };

}(jQuery));


