# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
MAST Core
=========

This the base class for MAST queries.
"""

import warnings

from astropy.utils import deprecated
from astropy.utils.exceptions import AstropyDeprecationWarning

from ..query import QueryWithLogin

from . import utils
from .auth import MastAuth
from .cloud import CloudAccess
from .discovery_portal import PortalAPI
from .services import ServiceAPI


class MastQueryWithLogin(QueryWithLogin):
    """
    Super class for MAST functionality.
    """

    def __init__(self, mast_token=None):

        super().__init__()

        # Initializing API connections
        self._portal_api_connection = PortalAPI(self._session)
        self._service_api_connection = ServiceAPI(self._session)

        if mast_token:
            self._authenticated = self._auth_obj = MastAuth(self._session, mast_token)
        else:
            self._auth_obj = MastAuth(self._session)

        self._cloud_connection = None

    def _login(self, token=None, store_token=False, reenter_token=False):
        """
        Log into the MAST portal.

        Parameters
        ----------
        token : string, optional
            Default is None.
            The token to authenticate the user.
            This can be generated at
            https://auth.mast.stsci.edu/token?suggested_name=Astroquery&suggested_scope=mast:exclusive_access.
            If not supplied, it will be prompted for if not in the keyring or set via $MAST_API_TOKEN
        store_token : bool, optional
            Default False.
            If true, MAST token will be stored securely in your keyring.
        reenter_token :  bool, optional
            Default False.
            Asks for the token even if it is already stored in the keyring or $MAST_API_TOKEN environment variable.
            This is the way to overwrite an already stored password on the keyring.
        """

        return self._auth_obj.login(token, store_token, reenter_token)

    @deprecated(since="v0.3.9", message=("The get_token function is deprecated, "
                                         "session token is now the token used for login."))
    def get_token(self):
        return None

    def session_info(self, silent=None, verbose=None):
        """
        Displays information about current MAST user, and returns user info dictionary.

        Parameters
        ----------
        silent :
            Deprecated. Use verbose instead.
        verbose : bool, optional
            Default True. Set to False to suppress output to stdout.

        Returns
        -------
        response : dict
        """

        # Dealing with deprecated argument
        if (silent is not None) and (verbose is not None):
            warnings.warn(("Argument 'silent' has been deprecated, "
                           "will be ignored in favor of 'verbose'"), AstropyDeprecationWarning)
        elif silent is not None:
            warnings.warn(("Argument 'silent' has been deprecated, "
                           "and will be removed in the future. "
                           " Use 'verbose' instead."), AstropyDeprecationWarning)
            verbose = not silent
        elif (silent is None) and (verbose is None):
            verbose = True

        return self._auth_obj.session_info(verbose)

    def logout(self):
        """
        Log out of current MAST session.
        """
        self._auth_obj.logout()
        self._authenticated = False

    @deprecated(since="v0.3.9", alternative="enable_cloud_dataset")
    def enable_s3_hst_dataset(self):
        return self.enable_cloud_dataset()

    def enable_cloud_dataset(self, provider="AWS", profile=None, verbose=True):
        """
        Enable downloading public files from S3 instead of MAST.
        Requires the boto3 library to function.

        Parameters
        ----------
        provider : str
            Which cloud data provider to use.  We may in the future support multiple providers,
            though at the moment this argument is ignored.
        profile : str
            Profile to use to identify yourself to the cloud provider (usually in ~/.aws/config).
        verbose : bool
            Default True.
            Logger to display extra info and warning.
        """

        self._cloud_connection = CloudAccess(provider, profile, verbose)

    @deprecated(since="v0.3.9", alternative="disable_cloud_dataset")
    def disable_s3_hst_dataset(self):
        return self.disable_cloud_dataset()

    def disable_cloud_dataset(self):
        """
        Disables downloading public files from S3 instead of MAST
        """
        self._cloud_connection = None

    def resolve_object(self, objectname):
        """
        Resolves an object name to a position on the sky.

        Parameters
        ----------
        objectname : str
            Name of astronomical object to resolve.

        Returns
        -------
        response : `~astropy.coordinates.SkyCoord`
            The sky position of the given object.
        """
        return utils.resolve_object(objectname)
