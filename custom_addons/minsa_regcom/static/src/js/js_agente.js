odoo.define('minsa_regcom.open_map_sigrid_modal', function (require) {
    'use strict';

    function openMapSigridModal(usuario) {
        var url = 'https://sigrid.cenepred.gob.pe/sigridv3/componente_geocoder/' + usuario + '/create';
        var options = {
            'size': 'large',
            'dialogClass': 'modal-dialog',
            'width': '100%',
            'height': '600px',
            'border': 'solid 1px #0094ff',
        };
        session.open_url(url, options);
    }

    return {
        openMapSigridModal: openMapSigridModal,
    };
});
