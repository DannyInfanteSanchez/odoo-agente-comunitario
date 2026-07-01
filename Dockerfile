FROM odoo:14.0

USER root

# Copy the custom module into the extra-addons directory
COPY ./agente_comite_comunitario-develop/agente_comite_comunitario-develop/minsa_regcom /mnt/extra-addons/minsa_regcom

# Ensure correct permissions
RUN chown -R odoo:odoo /mnt/extra-addons/minsa_regcom

USER odoo
