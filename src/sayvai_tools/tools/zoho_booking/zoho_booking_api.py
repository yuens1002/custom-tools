import requests
from os import path, getenv
import datetime as dt
from dotenv import load_dotenv
import pickle
import logging

load_dotenv()

# Basic logging setup
logging.basicConfig(level=logging.DEBUG)

# - the api requires an auth code
# - an access & refresh tokens are given in auth request
# - the access token expires in an hr
# - use the refresh token to get a new access token
# - be sure to call get_auth_tokens using the auth code before the expiration (defaults to 3mins)
# - be sure to send booking as data not json, and only serialize the customer_details object

# Get the directory of the current file
current_dir = path.dirname(path.abspath(__file__))

# Get the path to the parent directory
parent_dir = path.dirname(current_dir)

# Construct the path to 'token.pickle' in the parent directory
pickle_token_path = path.join(parent_dir, "token.pickle")


class Code_Error(ValueError):
    """Raised when code error is returned from the request"""

    pass


class ZohoBookingApi:
    def __init__(self):

        self._access_token_expires_at = None
        self._auth_base_url = "https://accounts.zoho.com/oauth/v2/token"
        self._booking_base_url = "https://www.zohoapis.com/bookings/v1/json"
        self._zoho_redirect_uri = "https://deluge.zoho.com/delugeauth/callback"
        self._client_id = getenv("ZOHO_CLIENT_ID")
        self._client_secret = getenv("ZOHO_CLIENT_SECRET")
        self._auth_code = getenv("ZOHO_AUTH_CODE")
        self.appointment_urls = {
            # the dict item value is used to append to the end of the api url
            "book": "appointment",
            "get": "getappointment",
            "update": "updateappointment",
            "reschedule": "rescheduleappointment",
            "availability": "availableslots",
        }

    def _get_saved_creds(self):
        # The file token.pickle stores the user's access and refresh tokens.
        if path.exists(pickle_token_path):
            with open(pickle_token_path, "rb") as token:
                return pickle.load(token)
        return None

    def _is_access_token_expired(self):
        if not self._access_token_expires_at:
            return True
        return dt.datetime.now() > self._access_token_expires_at

    def _set_access_token_expires_at(self, expires_in):
        self._access_token_expires_at = dt.datetime.now() + dt.timedelta(
            seconds=expires_in
        )

    def _get_valid_access_token(self):
        creds = self._get_saved_creds()
        if (
            creds is not None
            and "access_token" in creds
            and self._is_access_token_expired()
        ):
            self.refresh_access_token()  # updates the access token
        if creds is None:
            raise ValueError("Tokens not found or invalid")

        return creds["access_token"]  # works b/c dictionaries are references

    def get_auth_tokens(self):
        creds = self._get_saved_creds()
        if not creds:
            try:
                response = requests.post(
                    url=self._auth_base_url,
                    params={
                        "grant_type": "authorization_code",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "redirect_url": self._zoho_redirect_uri,
                        "code": self._auth_code,
                    },
                )
                if response.status_code == 200:
                    creds = response.json()
                    if "error" in creds:
                        raise Code_Error(creds["error"])
                    with open(pickle_token_path, "wb") as token:
                        pickle.dump(creds, token)  # save creds to a local file
                    self._set_access_token_expires_at(
                        creds["expires_in"]
                    )  # save the time when the access code is fetched
                response.raise_for_status()
            except Code_Error as e:
                logging.error(
                    f"Error: {e}, refer to https://www.zoho.com/bookings/help/api/v1/registerclient.html for more details"
                )
            except requests.exceptions.HTTPError as e:
                logging.error(f"An HTTP error occurred during auth token request: {e}")
            except (
                requests.exceptions.RequestException
            ) as e:  # Catch other potential issues
                logging.error(
                    f"A general request error occurred during auth token request: {e}"
                )

        return creds

    def refresh_access_token(self):
        creds = self.get_auth_tokens()  # get refresh_token
        if creds is not None:
            try:
                response = requests.post(
                    f"{self._auth_base_url}?refresh_token={creds['refresh_token']}&client_id={self._client_id}&client_secret={self._client_secret}&grant_type=refresh_token"
                )
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        raise Code_Error(data["error"])
                    with open(pickle_token_path, "rb") as token:
                        creds = pickle.load(token)
                    creds["access_token"] = data["access_token"]
                    with open(pickle_token_path, "wb") as token:
                        pickle.dump(creds, token)
                    self._set_access_token_expires_at(data["expires_in"])
                response.raise_for_status()  # Raise an exception if any or nothing
            except Code_Error as e:
                logging.error(
                    f"Error: {e}, refer to https://www.zoho.com/bookings/help/api/v1/refreshaccesstoken.html for more details"
                )
            except requests.exceptions.HTTPError as e:
                logging.error(
                    f"An HTTP error occurred during access token request: {e}"
                )
            except requests.exceptions.RequestException as e:
                logging.error(f"An error occurred during access token request: {e}")

    def appointment(self, url: str, form_data: dict):
        access_token = self._get_valid_access_token()
        try:
            url = f"{self._booking_base_url}/{self.appointment_urls[url]}"
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}

            response = requests.post(url=url, headers=headers, data=form_data)
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"An HTTP error occurred during booking request: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred during booking request: {e}")

    def availability(self, url: str, selected_date: str):
        access_token = self._get_valid_access_token()

        try:
            url = f"{self._booking_base_url}/{self.appointment_urls[url]}"
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
            params = {
                "service_id": getenv("SERVICE_ID"),
                "staff_id": getenv("STAFF_ID"),
                "selected_date": selected_date,
            }
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.error(f"An HTTP error occurred during availability request: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred during availability request: {e}")
