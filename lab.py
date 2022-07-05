from typing import List

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
import urllib3
from getpass import getpass
import os

# The WSDL is a local file which contains the CUCM Schema
WSDL_FILE = 'schema/AXLAPI.wsdl'
CUCM_ADDRESS = '10.10.20.1'


# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        # Format the request body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print=True, encoding='unicode')

        print(f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')

    def ingress(self, envelope, http_headers, operation):
        # Format the response body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print=True, encoding='unicode')

        print(f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}')


# Connect to CUCM and create ProxyService
def connect_to_cucm(username: str, password: str) -> Client.service:
    # Change to true to enable output of request/response headers and XML
    DEBUG = False

    session = Session()
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session.auth = HTTPBasicAuth(username, password)

    # Create a Zeep transport and set a reasonable timeout value
    transport = Transport(session=session, timeout=10)

    # strict=False is not always necessary, but it allows zeep to parse imperfect XML
    settings = Settings(strict=False, xml_huge_tree=True)

    # If debug output is requested, add the MyLoggingPlugin callback
    plugin = [MyLoggingPlugin()] if DEBUG else []

    # Create the Zeep client with the specified settings
    client = Client(WSDL_FILE, settings=settings, transport=transport, plugins=plugin)

    # Return the ServiceProxy object
    return client.create_service('{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                 f'https://{CUCM_ADDRESS}:8443/axl/')


# Function to create a test application User
def add_app_user(uc, userid: str, password: str, presence_group_name: str):
    app_user = {
        'userid': userid,
        'password': password,
        'presenceGroupName': presence_group_name,
        'associatedDevices': {
            'device': []
        }
    }
    try:
        resp = uc.addAppUser(app_user)
        print("\naddAppUser response:\n")
        print(resp, "\n")
    except Exception as err:
        print(f"\nError: addAppUser: {err}")


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def add_location(uc, name):
    location = {
        'name': name,
        'relatedLocations': {
            'relatedLocation': []
        },
        'withinAudioBandwidth': '0',
        'withinVideoBandwidth': '0',
        'withinImmersiveKbits': '0',
        'betweenLocations': {
            'betweenLocation': []
        }
    }
    related_location = {
        'locationName': 'Hub_None',
        'rsvpSetting': 'Use System Default'
    }
    between_location = {
        'locationName': 'Hub_None',
        'weight': '50',
        'audioBandwidth': '0',
        'videoBandwidth': '0',
        'immersiveBandwidth': '0'
    }
    location['relatedLocations']['relatedLocation'].append(related_location)
    location['betweenLocations']['betweenLocation'].append(between_location)

    try:
        resp = uc.addLocation(location)
    except Fault as err:
        print(f'Zeep error: addLocation: {err}')


if __name__ == '__main__':
    running = True
    cucm = connect_to_cucm('administrator', 'ciscopsdt')

    add_location(cucm, 'TestLocation3')

    # while running:
    #     cls()
    #     print("\nWhat would you like to do?\n(1) Create an Application User")
    #     option = input('\nEnter a number (or type Q to quit): ')
    #     if option.lower() == 'q':
    #         input('\nYou have Quit.\nPress Enter to exit...')
    #         cls()
    #         running = False
    #     elif option == '1':
    #         # Test calling the add app user function
    #         add_app_user(cucm, input("New Application User's Username: "), 'Cisco1234', 'Standard Presence Group', )
    #     else:
    #         print("Invalid entry...")
    #
    #     input('Press Enter to continue...')
