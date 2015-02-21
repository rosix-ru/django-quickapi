/* 
 * jquery.quicktable.js - jQuery plugin for django-quickapi application
 * 
 * depends:
 *      jquery.quickapi.js - jQuery plugin for django-quickapi
 * recommends:
 *      Twitter bootstrap >= 3.0
 * 
 * Copyright 2014 Grigoriy Kramarenko <root@rosix.ru>
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
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
     *   var $table = $('#my-table').quickTable({
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

    $.fn[pluginName] = function(opts) {

        if (!opts.url || !opts.method) {
            console.error(
                "Not valid options for "+pluginName,
                {url:opts.url, method:opts.method}
            );
        };

        if ($.type(opts.columns) != 'array' || $.isEmptyObject(opts.columns)) {

            console.error(
                "Not valid options for "+pluginName,
                {columns:opts.columns},
                'columns must be not empty array!'
            );

            console.info('EXAMPLE:\n',
            'columns = [ {name:"id", hidden:true, notmanaged:true}, {name:"name", title:"Name"} ]\n',
            'where `name` - object attribute, `hidden` - hidden column,',
            ' `notmanaged` - the column is not managed, `title` - title of column.'
            );

        };

        this.each(function() {

            var table = this,
                id = $(table).attr('id');

            if (!id) { return this }; // not valid

            var options = $.extend({
                    url: undefined,
                    method: undefined,
                    columns: undefined,
                    type: 'GET',
                    timeout: 10000,
                    async: true,
                    autoload: true,
                    autorender_settings: true,
                    delay: 500,
                    min_char: 3,
                    page: 1,
                    limit: 25,
                    limit_list: [25, 50, 75, 100],
                    filters: {},
                    ordering: [],
                    multiordering: false,
                    table_type: 'table', // variants: 'stack'
                    text_pager_prev: '&laquo;',
                    text_pager_next: '&raquo;',
                    text_not_found: 'Not found',
                    // the following variables are strongly advised not to change
                    _selector_filtering: '[data-filtering='+id+']',
                    _selector_ordering: '[data-ordering='+id+'][name]',
                    _selector_limiting: 'input[data-limiting='+id+']:checked, select[data-limiting='+id+']',
                    _selector_colswitcher: 'input[data-colswitcher='+id+']',
                    _selector_settings: '#'+id+'_settings',
                    _selector_pager: '#'+id+'_pager',
                    _selector_pager_links: 'li:not(.disabled) a:not(.disabled)',
                    _selector_info: '#'+id+'_info',
                    _selector_thead: '#'+id+' thead',
                    _selector_tbody: '#'+id+' tbody',
                    _default_filter_key: '_search_',
                    _managed_columns: [],
                    _column_names: {},
                }, opts);

            table.options = options; // link
            table.request = null; // current jqxhr
            table.fn = {}; // storage for functions

            options.replace = true; // append or overwrite tbody

            $.each(options.columns, function(i, col) {
                options._column_names[col.name] = col;
                if (col.hidden) $(table).addClass('table-col-'+i+'-hidden');
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

            /* Twitter bootstrap .pager inner HTML */
            table.fn._render_bs_pager = function(page, num_pages, hide_prev) {

                var html = '';

                if (page >1 && !hide_prev) {
                    html += '<li><a href="#" value="'+(page-1)+'">'+options.text_pager_prev+'</a></li>';
                } else {
                    html += '<li class="disabled"><span>'+options.text_pager_prev+'</span></li>';
                }

                if (page < num_pages) {
                    html += '<li><a href="#" value="'+(page+1)+'">'+options.text_pager_next+'</a></li>';
                } else {
                    html += '<li class="disabled"><span>'+options.text_pager_next+'</span></li>';
                }

                $(options._selector_pager).html(html);

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
                    html += '<li><a href="#" value="'+(page-1)+'">'+options.text_pager_prev+'</a></li>';
                } else {
                    html += '<li class="disabled"><span>'+options.text_pager_prev+'</span></li>';
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
                        html += '<li><a href="#" value="'+item+'">'+item+'</a></li>';
                    }

                });

                if (page < num_pages) {
                    html += '<li><a href="#" value="'+(page+1)+'">'+options.text_pager_next+'</a></li>';
                } else {
                    html += '<li class="disabled"><span>'+options.text_pager_next+'</span></li>';
                }

                $(options._selector_pager).html(html);

            };

            /* Use default pagination */
            table.fn.render_pager = function(page, num_pages) {

                if (options.table_type == 'stack') {
                    return table.fn._render_bs_pager(page, num_pages, true);
                }

                return table.fn._render_bs_pagination(page, num_pages);

            }

            /* Rendering information */
            table.fn.render_info = function(html) {
                $(options._selector_info).html(html);
            };

            /* Rendering settings */
            table.fn.render_settings = function() {

                var html = '';

                $.each(options.columns, function(i, col) {

                    if (!col.notmanaged) {
                        html += '<label>'
                             +'<input type="checkbox" name="'+id+'_colswitcher" value="'+i+'" '
                             +(!col.hidden ? ' checked' : '')+'/>'
                             +(col.title||col.name)
                             +'</label>'
                    }

                });

                html += '<div class="btn-group" data-toggle="buttons">'
  
                $.each(options.limit_list, function(i, limit) {

                    html += '<label class="btn'+(options.limit == limit ? ' active': '')+'">'
                            +'<input type="checkbox" name="'+id+'_limit" '
                            +(options.limit == limit ? ' checked': '')+'>'
                            + limit
                            +'</label>'

                });

                html += '</div>'

                $(options._selector_settings).html(html);

            };

            /* Returns class for <tr> */
            table.fn.get_class_tr = function(object) { return object ? '' : 'row-danger' };

            /* Rendering one object */
            table.fn.render_object = function(index, object) {

                if (object == null && options.text_not_found == null) return;

                var html = '';

                html += '<tr class="'+table.fn.get_class_tr(object)+'">';

                if (object) {

                    $.each(options.columns, function(i, col) {

                        html += '<td>'+object[col.name]+'</td>';

                    });
                } else {
                    html += '<td colspan="'+options.columns.length+'">'+options.text_not_found+'</td>'
                }


                html += '</tr>';

                $(options._selector_tbody).append(html);

            };

            /* Callback of jqxhr. Rendering all objects, pagination, etc. */
            table.fn.render = function(json, replace) {

                var data = json.data;

                if (replace) $(options._selector_tbody).html('');

                if ($.isEmptyObject(data.objects)) {
                    table.fn.render_object(0, null)
                } else {
                    $.each(data.objects, function(i, item) {
                        table.fn.render_object(i, item)
                    })
                }

                table.fn.render_pager(data.page, data.num_pages);

                if (data.info) table.fn.render_info(data.info);

            };

            /* Request to server on quickAPI. Returns jqxhr. */
            table.fn.get = function() {

                var replace = options.replace;

                if (table.request) table.request.abort();

                table.request = $.quickAPI({
                    url: options.url,
                    timeout: options.timeout,
                    type: options.type,
                    async: options.async,
                    args: {
                        method: options.method,
                        kwargs: {
                            filters: options.filters,
                            ordering: options.ordering,
                            page: options.page,
                            limit: options.limit,
                        },
                    },
                    callback: function(json, status, xhr) { return table.fn.render(json, replace) },
                    showAlert: options.showAlert,
                })
                .always(function() {table.request = null});

                return table.request

            };

            /* Request to server from first page by force. */
            table.fn.get_first_page = function() {

                options.page = 1;
                options.replace = true;

                return table.fn.get();

            };

            /*** END FUNCTIONS ***/

            /*** START BINDING TABLE CONTROLLERS ON BODY OF DOCUMENT ***/

            $('body')

            /* Keyup on filters */
            .off('keyup', options._selector_filtering)
            .on('keyup', options._selector_filtering, function(e) {

                var old = options.filters[(this.name || options._default_filter_key)],
                    min = Number($(this).data('minimum')) || 0;

                if (this.value != old && this.value.length >= min) {

                    options.filters[(this.name || options._default_filter_key)] = this.value;
                    table.fn.delay(table.fn.get_first_page, options.delay);

                }

            })

            /* Change limit on page */
            .off('change', options._selector_limiting)
            .on('change', options._selector_limiting, function(e) {

                options.limit = this.value;
                table.fn.get_first_page();

            })

            /* Change visible of column */
            .off('change', options._selector_colswitcher)
            .on('change', options._selector_colswitcher, function(e) {

                var i = this.value;

                if (this.checked) {
                    $(table).removeClass('table-col-'+i+'-hidden');
                    options.columns[i].hidden = false;
                } else {
                    $(table).addClass('table-col-'+i+'-hidden');
                    options.columns[i].hidden = true;
                }

            })

            /* Change ordering on columns */
            .off('click', options._selector_ordering)
            .on('click', options._selector_ordering, function(e) {

                var column = this.name,
                    L = options.ordering,
                    i = $.inArray(column, L);

                if (!options.multiordering) {
                    $(options._selector_ordering).removeClass('sorting_asc')
                                                 .removeClass('sorting_desc')
                                                 .addClass('sorting');
                }

                if (i > -1) {
                    //~ console.debug('exists', i, column);
                    if (!options.multiordering) {
                        L = ['-'+column];
                    } else {
                        L[i] = '-'+column;
                    }

                    $(this).removeClass('sorting').addClass('sorting_desc');
                } else {
                    //~ console.debug('not exists', i, column);
                    i = $.inArray('-'+column, L);
                    if (i > -1) {
                        //~ console.debug('remove', i, '-'+column);
                        if (!options.multiordering) {
                            L = [];
                        } else {
                            L = L.slice(0,i).concat(L.slice(i+1));
                        }

                        $(this).removeClass('sorting_desc').addClass('sorting');
                    }
                }

                if (i == -1){
                    //~ console.debug('not exists', i, '-'+column);
                    if (!options.multiordering) {
                        L = [column];
                    } else {
                        L.push(column);
                    }

                    $(this).removeClass('sorting').addClass('sorting_asc');
                }

                options.ordering = L;

                table.fn.get_first_page();

            });

            /* Click on pagination */
            $(options._selector_pager)
            .off('click', options._selector_pager_links)
            .on('click', options._selector_pager_links, function(e) {

                e.preventDefault();
                options.page = $(this).val();
                if (options.table_type == 'stack') { options.replace = false };
                table.fn.get();

            });

            /*** END BINDING TABLE CONTROLLERS ***/

            /* Starting table */
            if (options.autorender_settings) table.fn.render_settings();
            if (options.autoload) table.fn.get_first_page();

        });
 
        return this;
 
    };

}(jQuery));


