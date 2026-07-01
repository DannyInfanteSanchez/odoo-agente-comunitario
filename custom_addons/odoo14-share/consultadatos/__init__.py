from odoo.exceptions import ValidationError

from . import models  # noqa

try:
    from mpi_client import client as mpiclient
    from mpi_client import version as mpi_client_version
except Exception as e:
    mpiclient = None

#from models.constants import mpi_client_version_min, mpi_msg_not_install

mpi_msg_min_version = (
    mpiclient
    and u"La versión {} actual de mpi_client debe ser al menos {}".format(
        mpi_client_version, models.constants.mpi_client_version_min
    )
)


def pre_init_hook(cr):
    if not mpiclient:
        raise ValidationError(mpi_msg_not_install)

    if not mpi_client_version >= models.constants.mpi_client_version_min:
        raise ValidationError(mpi_msg_min_version)
