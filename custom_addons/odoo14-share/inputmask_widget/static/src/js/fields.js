odoo.define('inputmask_widget.fields', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    const CE = 'contenteditable';

    const DATA_INPUTMASK_MIN = 'data-inputmask-min';
    const DATA_INPUTMASK_MAX = 'data-inputmask-max';
    const DATA_INPUTMASK_DIASTOLIC_MIN = 'data-inputmask-diastolic-min';
    const DATA_INPUTMASK_DIASTOLIC_MAX = 'data-inputmask-diastolic-max';
    const DATA_INPUTMASK_SYSTOLIC_MIN = 'data-inputmask-systolic-min';
    const DATA_INPUTMASK_SYSTOLIC_MAX = 'data-inputmask-systolic-max';
    const DATA_INPUTMASK_MEASURE = 'data-inputmask-measure';

    const BLOODPRESSURE_WIDGET = 'bloodpressure';
    const BLOODPRESSURE_WIDGET_ALIAS = 'widget-alias';
    const DATA_INPUTMASK_WIDGET_ALIAS = 'widget-alias';
    const DATA_TIPSO = 'data-tipso';
    const DATA_INPUTMASK_SHOW_TIPSO = 'data-inputmask-show-tipso';

    const OUT_OF_LIMIT_CLASS = 'out-of-limit-value';

    const SUFFIX = 'suffix';
    const INLINE_CLASS = 'inline';
    const SYSTOLIC_MIN = 'systolic-min';
    const SYSTOLIC_MAX = 'systolic-max';
    const DIASTOLIC_MIN = 'diastolic-min';
    const DIASTOLIC_MAX = 'diastolic-max';

    function mask_attrs(attrs) {
        var keyMask = 'data-inputmask';
        var attrsMask;
        attrsMask = Object.keys(attrs).reduce(function (filtered, key) {
            if (key.indexOf(keyMask) !== -1)
                filtered[key] = attrs[key];
            return filtered;
        }, {});
        if (!attrsMask)
            console.warn("The widget Mask expects the 'data-inputmask[-attribute]' attrsMask!");
        return attrsMask;
    }

    var AbstractFieldMask = {
        template: "FieldMask",
        attrsMask: {},
        maskType: undefined,
        init: function () {
            this._super.apply(this, arguments);
            if(CE in this.attrs)
                this.attrsMask[CE] = this.attrs[CE];
            this.attrsMask =  _.extend({}, this.attrsMask, mask_attrs(this.attrs));
        },
        _renderReadonly: function () {
            this._super();
            if(CE in this.attrsMask){                
                this.$el.inputmask(this.maskType);                
            }
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            var suffix_visible = true;
            if (this.$input !== undefined) {
                this.$input.inputmask(this.maskType,
                    { "onincomplete": function(e) {
                            console.log('inputmask incomplete');
                            if( ! e.currentTarget.inputmask.isValid()) {
                                var value = e.currentTarget.value.replace(/_/g, "");
                                if ( ! (Number(value) >= Number($(this).attr(DATA_INPUTMASK_MIN))
                                     && Number(value) <= Number($(this).attr(DATA_INPUTMASK_MAX))) ) {
                                  if (value != "") {
                                    $(this).addClass(OUT_OF_LIMIT_CLASS);
                                  } else {
                                    $(this).removeClass(OUT_OF_LIMIT_CLASS);
                                  }
                                } else {
                                    e.currentTarget.value = Number(value);
                                    $(this).removeClass(OUT_OF_LIMIT_CLASS);
                                    $(this).tipso('hide');
                                }
                            }
                        },
                      "oncomplete": function(e) {
                            $(this).tipso('hide');
                            $(this).removeClass(OUT_OF_LIMIT_CLASS);
                            if ($(this).attr(BLOODPRESSURE_WIDGET_ALIAS) == BLOODPRESSURE_WIDGET) {
                                var value = e.currentTarget.value.replace(/_/g, "").split("/");
                                if ( ! (parseInt(value[0]) >= parseInt($(this).attr(DATA_INPUTMASK_SYSTOLIC_MIN))
                                    && parseInt(value[0]) <= parseInt($(this).attr(DATA_INPUTMASK_SYSTOLIC_MAX))) ||
                                     ! (parseInt(value[1]) >= parseInt($(this).attr(DATA_INPUTMASK_DIASTOLIC_MIN))
                                    && parseInt(value[1]) <= parseInt($(this).attr(DATA_INPUTMASK_DIASTOLIC_MAX)))) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    $(this).addClass(OUT_OF_LIMIT_CLASS);
                                    $(this).tipso('show');
                                } else {
                                    if (parseInt(value[0]) <= parseInt(value[1])) {
                                        $(this).addClass(OUT_OF_LIMIT_CLASS);
                                        $(this).tipso('show');
                                    }else {
                                        $(this).removeClass(OUT_OF_LIMIT_CLASS);
                                        $(this).tipso('hide');
                                    }
                                }
                            } else {
                              if ($(this).attr(DATA_INPUTMASK_MIN) != undefined && $(this).attr(DATA_INPUTMASK_MAX) != undefined){
                                var value = e.currentTarget.value.replace(/_/g, "");
                                if ( ! (Number(value) >= Number($(this).attr(DATA_INPUTMASK_MIN))
                                     && Number(value) <= Number($(this).attr(DATA_INPUTMASK_MAX))) ) {
                                    $(this).addClass(OUT_OF_LIMIT_CLASS);
                                    $(this).tipso('show');
                                } else {
                                    $(this).removeClass(OUT_OF_LIMIT_CLASS);
                                    $(this).tipso('hide');
                                }
                              } else {
                                $(this).removeClass(OUT_OF_LIMIT_CLASS);
                                $(this).tipso('hide');
                              }
                            }
                        },
                });
                if(this.$input.hasClass('o_form_invisible')) { suffix_visible = false; }
                this.addAttr();
                this.addTipsoEventListeners(this.$input);
            } else {
                this.$el.val(this.$el.text());
                if(this.$el.hasClass('o_form_invisible')) { suffix_visible = false; }
            }
            suffix_visible = true;
            this.add_sufix(suffix_visible);
            this.addTipso();

            this.$input.inputmask(this.maskType);
            return def;
        },
        addTipso: function() {
            if(DATA_TIPSO in this.attrs) {
                if (this.$input !== undefined) {
                    this.$input.attr(DATA_TIPSO, this.attrs[DATA_TIPSO]);
                    var title = (this.attrs['title'] != undefined) ? this.attrs['title'] : 'Ayuda';

                    var measure = (this.attrs[DATA_INPUTMASK_MEASURE] != undefined) ? this.attrs[DATA_INPUTMASK_MEASURE] : ''
                    var desde = (this.attrs[DATA_INPUTMASK_MIN] != undefined) ? ' desde ' + this.attrs[DATA_INPUTMASK_MIN] : ''
                    var hasta = (this.attrs[DATA_INPUTMASK_MAX] != undefined) ? ' hasta ' + this.attrs[DATA_INPUTMASK_MAX] : ''
                    var message = this.attrs[DATA_TIPSO] + desde + hasta + measure

                    if (this.attrs[BLOODPRESSURE_WIDGET_ALIAS] == BLOODPRESSURE_WIDGET) {
                        message = 'Sistólica ('+
                            this.attrsMask[DATA_INPUTMASK_SYSTOLIC_MIN] +' a '+
                            this.attrsMask[DATA_INPUTMASK_SYSTOLIC_MAX]+') <br> Diastólica ('+
                            this.attrsMask[DATA_INPUTMASK_DIASTOLIC_MIN]+' a '+
                            this.attrsMask[DATA_INPUTMASK_DIASTOLIC_MAX]+ ')'
                    }
                    if (this.attrs[DATA_INPUTMASK_SHOW_TIPSO] == undefined ||
                        this.attrs[DATA_INPUTMASK_SHOW_TIPSO] == 'true' ||
                        this.attrs[DATA_INPUTMASK_SHOW_TIPSO] == '1')
                        this.$input.tipso({titleContent: title, content: message});
                }
            }
        },
        addAttr: function() {
            if(this.attrs[BLOODPRESSURE_WIDGET_ALIAS] == BLOODPRESSURE_WIDGET) {
                if(DIASTOLIC_MIN in this.attrs && DIASTOLIC_MAX in this.attrs) {
                    this.$input.attr(DATA_INPUTMASK_DIASTOLIC_MIN, this.attrs[DIASTOLIC_MIN]);
                    this.$input.attr(DATA_INPUTMASK_DIASTOLIC_MAX, this.attrs[DIASTOLIC_MAX]);
                    this.attrsMask[DATA_INPUTMASK_DIASTOLIC_MIN] = this.attrs[DIASTOLIC_MIN],
                    this.attrsMask[DATA_INPUTMASK_DIASTOLIC_MAX] = this.attrs[DIASTOLIC_MAX]
                }
                if(SYSTOLIC_MIN in this.attrs && SYSTOLIC_MAX in this.attrs) {
                    this.$input.attr(DATA_INPUTMASK_SYSTOLIC_MIN, this.attrs[SYSTOLIC_MIN]);
                    this.$input.attr(DATA_INPUTMASK_SYSTOLIC_MAX, this.attrs[SYSTOLIC_MAX]);
                    this.attrsMask[DATA_INPUTMASK_SYSTOLIC_MIN] = this.attrs[SYSTOLIC_MIN],
                    this.attrsMask[DATA_INPUTMASK_SYSTOLIC_MAX] = this.attrs[SYSTOLIC_MAX]
                }
            } else {
                if(DATA_INPUTMASK_MIN in this.attrs && DATA_INPUTMASK_MAX in this.attrs) {
                    this.$input.attr(DATA_INPUTMASK_MIN, this.attrs[DATA_INPUTMASK_MIN]);
                    this.attrsMask[DATA_INPUTMASK_MIN] = this.attrs[DATA_INPUTMASK_MIN];
                    this.$input.attr(DATA_INPUTMASK_MAX, this.attrs[DATA_INPUTMASK_MAX]);
                    this.attrsMask[DATA_INPUTMASK_MAX] = this.attrs[DATA_INPUTMASK_MAX];
                }
            }
            if(DATA_INPUTMASK_MEASURE in this.attrs) {
                this.$input.attr(DATA_INPUTMASK_MEASURE, this.attrs[DATA_INPUTMASK_MEASURE]);
                this.attrsMask[DATA_INPUTMASK_MEASURE] = this.attrs[DATA_INPUTMASK_MEASURE];
            }
            if(DATA_INPUTMASK_WIDGET_ALIAS in this.attrs) {
                this.$input.attr(DATA_INPUTMASK_WIDGET_ALIAS, this.attrs[DATA_INPUTMASK_WIDGET_ALIAS]);
            }
        },
        addTipsoEventListeners(input) {
            input.focusout(function(e) { $(this).tipso('hide'); });
            input.focus(function(e) { $(this).tipso('show'); });
            input.keypress(function(e) { $(this).tipso('show'); });
            input.mouseover(function(e) { $(this).tipso('show'); });
        },
        add_sufix: function (is_visible) {
            if (SUFFIX in this.attrs) {
                if (this.attrs[SUFFIX] == "true" || this.attrs[SUFFIX] == "1") {
                    var visible = is_visible == false ? 'o_form_invisible' : '';
                    var suffix = $("<span class='mask-suffix " + visible + " input-group-text'></span>").text(this.attrs[DATA_INPUTMASK_MEASURE]);
                    var container_div = $('<div class="input-group mb-3"></div>');
                    var prefix_div = $('<div class="input-group-prepend"></div>');
                    var sufix_div = $('<div class="input-group-append"></div>');

                    var domElement = $( this ).get( 0 );
                    var span = domElement.$el.parent()
                    if(span.is('td')) {
                        sufix_div.append(suffix);
                        container_div.append(prefix_div);
                        this.$el.addClass(INLINE_CLASS);
                        this.$el.detach().appendTo(container_div);
                        container_div.append(sufix_div);
                        container_div.addClass(INLINE_CLASS);
                        span.append(container_div);
                    } else {
                        this.$el.addClass(INLINE_CLASS);
                    }
                }
            }
        },
    };

    var FieldMask = basic_fields.FieldChar.extend(AbstractFieldMask);

     var FieldRegexMask = FieldMask.extend({
        maskType: "Regex"
    });

    return {FieldMask: FieldMask, FieldRegexMask: FieldRegexMask}
});