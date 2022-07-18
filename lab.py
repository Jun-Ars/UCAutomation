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
    client = Client(WSDL_FILE, settings=settings, transport=transport,
                    plugins=plugin)

    # Return the ServiceProxy object
    return client.create_service(
        '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
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
    """Tested and creating a location in the same fashion as exists in
    production.

    Create a Location in <uc> environment called <name> matching standards set
    at other locations in the environment."""
    location = {
        'name': f'{name}-Loc',
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
        'videoBandwidth': '384',
        'immersiveBandwidth': '384'
    }
    location['relatedLocations']['relatedLocation'].append(related_location)
    location['betweenLocations']['betweenLocation'].append(between_location)

    try:
        resp = uc.addLocation(location)
    except Fault as err:
        print(f'Error: addLocation: {err}')


def add_region(uc, name):
    """Tested in sandbox to be creating a region in the same fashion as exists in
    production.

    Create a Region in <uc> environment called <name>, matching standards set
    at other regions in the environment. The related region, 'G729-Region',
    sets the maximum audio bit rate to 8 kbps, as per the standard found in
    production."""
    # Create a region
    new_region = {
        'name': f'{name}-Region',
        'relatedRegions': {
            'relatedRegion': []
        }
    }

    # List of all regions
    all_regions = [region['name'] for region in
                   uc.listRegion(
                       searchCriteria={'name': '%'},
                       returnedTags={'name': xsd.Nil}
                   )['return']['region']]

    # Create a relatedRegion sub object per each region in all_regions
    for region in all_regions:
        related_region = {
            'regionName': region,
            'bandwidth': '64 kbps',
            'videoBandwidth': -2,
            'lossyNetwork': 'Use System Default',
            'codecPreference': {
                '_value_1': 'Use System Default',
                'uuid': ''
            },
            'immersiveVideoBandwidth': -2,
        }
        # Per standard, this specific region is set to a different bandwidth
        if region == 'G729-Region':
            related_region['bandwidth'] = '8 kbps'

        # Add the relatedRegion to the region.relatedRegions array
        new_region['relatedRegions']['relatedRegion'].append(related_region)

    # Execute the addRegion request
    print('\naddRegion response:\n')
    try:
        resp = uc.addRegion(new_region)
        print(resp, '\n')
    except Fault as err:
        print(f'Zeep error: addRegion: {err}')


def add_srst(uc, name, ip):
    """Tested in sandbox to be creating an SRST in the same fashion as exists in
    production.

    Create an SRST in <uc> environment called <name>, matching standards set
    at SRSTs in the environment."""
    srst = {
        'name': f'{name}-SRST',
        'port': 2000,
        'ipAddress': ip,
        'ipv6Address': None,
        'SipNetwork': ip,
        'SipPort': 5060,
        'srstCertificatePort': 2445,
        'isSecure': 'false',
    }
    # Execute the addRegion request
    print('\naddSRST response:\n')
    try:
        resp = uc.addSrst(srst)
        print(resp, '\n')
    except Fault as err:
        print(f'Error: addRegion: {err}')


def add_route_group(uc, name):
    """Tested in sandbox to be creating a Route Group in the same fashion as exists in production.

    Create a Route Group in <uc> environment called <name>, matching standards set at SRSTs in the environment.
    IMPORTANT: This function assumes that the Trunk "<name>-GW" already exists!"""
    rg = {
        'name': f'{name}-RG',
        'distributionAlgorithm': 'Top Down',
        'members': {'member': []}
    }
    rg['members']['member'].extend(
        [
            {
                'deviceName': uc.getSipTrunk(name=f'{name}-GW')['return']['sipTrunk']['name'],
                'deviceSelectionOrder': 1,
                'port': '0'
            },
            {
                'deviceName': uc.getSipTrunk(name=f'Markham-GW-Trunk')['return']['sipTrunk']['name'],
                'deviceSelectionOrder': 2,
                'port': '0'
            }
        ]
    )
    print('\naddRouteGroup response:\n')
    try:
        resp = uc.addRouteGroup(rg)
        print(resp, '\n')
    except Fault as err:
        print(f'Error: addRouteGroup: {err}')


def add_device_pool(uc, name):

    dp = {
        "name": f'{name}-DP',
        "dateTimeSettingName": 'CMLocal',  # update to state timezone
        "regionName": f'{name}-Region',
        "locationName": f'{name}-Loc',
        "localRouteGroup": [
            {"name": '911 Primary', "value": f'{name}-RG'},
            {"name": 'PSTN Primary', "value": f'Centralized-SIP-Trunk-RG'}
        ],
        "mediaResourceListName": 'Hub-MRGL',
        "srstName": f'{name}-SRST',
        "callManagerGroupName": 'Residence-CMG',
        "networkLocale": '',
        'cgpnTransformationCssName': 'Incoming-ANI-E164-CSS',
        'callingPartyNationalPrefix': '+1',
        'callingPartyInternationalPrefix': '+',
        'callingPartyUnknownPrefix': 'Default',
        'callingPartySubscriberPrefix': '+1',
    }

    print('\naddDevicePool response:\n')
    try:
        resp = uc.addDevicePool(dp)
        print(resp, '\n')
    except Fault as err:
        print(f'Error: addDevicePool: {err}')


if __name__ == '__main__':
    running = True
    cucm = connect_to_cucm('administrator', 'ciscopsdt')

    add_device_pool(cucm, 'test')
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
