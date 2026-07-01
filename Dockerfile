FROM odoo:14.0

USER root

# Copy the main custom module
COPY ./agente_comite_comunitario-develop/agente_comite_comunitario-develop/minsa_regcom /mnt/extra-addons/minsa_regcom

# Copy any additional dependency modules (like renipress or toponimos_peru) placed in custom_addons
COPY ./custom_addons /mnt/extra-addons/

# Ensure correct permissions
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo
