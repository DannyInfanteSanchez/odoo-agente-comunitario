FROM odoo:14.0

USER root

# Copy the main custom module
COPY ./custom_addons/minsa_regcom /mnt/extra-addons/minsa_regcom

# Copy all individual modules from odoo14-share directly into /mnt/extra-addons/
COPY ./custom_addons/odoo14-share/ /mnt/extra-addons/

# Ensure correct permissions
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo
