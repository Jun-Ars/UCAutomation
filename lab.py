import base64
import os

import typer
import urllib3
from dotenv import load_dotenv
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault

# The WSDL is a local file which contains the CUCM Schema
WSDL_FILE = 'schema/AXLAPI.wsdl'
CUCM_ADDRESS = '10.10.20.1'

app = typer.Typer()


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


def connect_to_cucm(username: str, password: str) -> Client.service:
    # Change to true to enable output of request/response headers and XML
    debug = False

    session = Session()
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session.auth = HTTPBasicAuth(username, password)

    # Create a Zeep transport and set a reasonable timeout value
    transport = Transport(session=session, timeout=10)

    # strict=False is not always necessary, but it allows zeep to parse imperfect XML
    settings = Settings(strict=False, xml_huge_tree=True)

    # If debug output is requested, add the MyLoggingPlugin callback
    plugin = [MyLoggingPlugin()] if debug else []

    # Create the Zeep client with the specified settings
    client = Client(WSDL_FILE, settings=settings, transport=transport,
                    plugins=plugin)

    # Return the ServiceProxy object
    return client.create_service(
        '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
        f'https://{CUCM_ADDRESS}:8443/axl/')


@app.command()
def prep_env():
    """Prepare a fresh lab environment to mimic the existing production
    environment.
    """
    def prep_add_voice_gateway_sip_profile():
        sip = {
            'name': 'Voice Gateway SIP Profile',
            'description': 'Default SIP Profile',
            'defaultTelephonyEventPayloadType': 101,
            'redirectByApplication': 'false',
            'ringing180': 'false',
            'timerInvite': 180,
            'timerRegisterDelta': 5,
            'timerRegister': 3600,
            'timerT1': 500,
            'timerT2': 4000,
            'retryInvite': 6,
            'retryNotInvite': 10,
            'startMediaPort': 16384,
            'stopMediaPort': 32766,
            'startVideoPort': 0,
            'stopVideoPort': 0,
            'dscpForAudioCalls': None,
            'dscpForVideoCalls': None,
            'dscpForAudioPortionOfVideoCalls': None,
            'dscpForTelePresenceCalls': None,
            'dscpForAudioPortionOfTelePresenceCalls': None,
            'callpickupListUri': 'x-cisco-serviceuri-opickup',
            'callpickupGroupUri': 'x-cisco-serviceuri-gpickup',
            'meetmeServiceUrl': 'x-cisco-serviceuri-meetme',
            'userInfo': 'None',
            'dtmfDbLevel': 'Nominal',
            'callHoldRingback': 'Off',
            'anonymousCallBlock': 'Off',
            'callerIdBlock': 'Off',
            'dndControl': 'User',
            'telnetLevel': 'Disabled',
            'timerKeepAlive': 120,
            'timerSubscribe': 120,
            'timerSubscribeDelta': 5,
            'maxRedirects': 70,
            'timerOffHookToFirstDigit': 15000,
            'callForwardUri': 'x-cisco-serviceuri-cfwdall',
            'abbreviatedDialUri': 'x-cisco-serviceuri-abbrdial',
            'confJointEnable': 'true',
            'rfc2543Hold': 'false',
            'semiAttendedTransfer': 'true',
            'enableVad': 'false',
            'stutterMsgWaiting': 'false',
            'callStats': 'false',
            't38Invite': 'false',
            'faxInvite': 'false',
            'rerouteIncomingRequest': 'Never',
            'resourcePriorityNamespaceListName': {
                '_value_1': None,
            },
            'enableAnatForEarlyOfferCalls': 'false',
            'rsvpOverSip': 'Local RSVP',
            'fallbackToLocalRsvp': 'true',
            'sipRe11XxEnabled': 'Send PRACK if 1xx Contains SDP',
            'gClear': 'Disabled',
            'sendRecvSDPInMidCallInvite': 'false',
            'enableOutboundOptionsPing': 'true',
            'optionsPingIntervalWhenStatusOK': 60,
            'optionsPingIntervalWhenStatusNotOK': 120,
            'deliverConferenceBridgeIdentifier': 'false',
            'sipOptionsRetryCount': 6,
            'sipOptionsRetryTimer': 500,
            'sipBandwidthModifier': 'TIAS and AS',
            'enableUriOutdialSupport': 'f',
            'userAgentServerHeaderInfo': 'Send Unified CM Version Information as User-Agent Header',
            'allowPresentationSharingUsingBfcp': 'false',
            'scriptParameters': None,
            'isScriptTraceEnabled': 'false',
            'sipNormalizationScript': {
                '_value_1': None,
            },
            'allowiXApplicationMedia': 'false',
            'dialStringInterpretation': 'Phone number consists of characters 0-9, *, #, and + (others treated as URI addresses)',
            'acceptAudioCodecPreferences': 'Default',
            'mlppUserAuthorization': 'false',
            'isAssuredSipServiceEnabled': 'false',
            'enableExternalQoS': 'false',
            'resourcePriorityNamespace': {
                '_value_1': None,
            },
            'useCallerIdCallerNameinUriOutgoingRequest': 'false',
            'externalPresentationInfo': {
                'presentationInfo': {
                    'externalPresentationNumber': None,
                    'externalPresentationName': None
                },
                'isAnonymous': None,
            },
            'callingLineIdentification': 'Default',
            'rejectAnonymousIncomingCall': 'false',
            'callpickupUri': 'x-cisco-serviceuri-pickup',
            'rejectAnonymousOutgoingCall': 'false',
            'videoCallTrafficClass': 'Mixed',
            'sdpTransparency': {
                '_value_1': 'Pass all unknown SDP attributes',
            },
            'allowMultipleCodecs': 'false',
            'sipSessionRefreshMethod': 'Invite',
            'earlyOfferSuppVoiceCall': 'Disabled (Default value)',
            'cucmVersionInSipHeader': 'Major And Minor',
            'confidentialAccessLevelHeaders': 'Disabled',
            'destRouteString': 'false',
            'inactiveSDPRequired': 'false',
            'allowRRAndRSBandwidthModifier': 'false',
            'connectCallBeforePlayingAnnouncement': 'false',
        }

        print('\naddSipProfile response:\n')
        try:
            resp = cucm.addSipProfile(sip)
            print(f'SipProfile successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: addSipProfile: {err}')

    def prep_add_partition(name: str):
        partition = {
            'name': f'{name}',
            'description': f'{name}',
            'dialPlanWizardGenId': None,
            'timeScheduleIdName': {
                '_value_1': None,
            },
            'useOriginatingDeviceTimeZone': 'true',
            'timeZone': 'Etc/GMT'
        }
        print('\naddPartition response:\n')
        try:
            resp = cucm.addRoutePartition(partition)
            print(f'Partition successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: addPartition: {err}')

    def prep_add_markhamGW_incoming_css():
        css = {
            'description': 'MarkhamGW-Trunk-Incoming-CSS',
            'members': {
                'member': [
                    {
                        'routePartitionName': {
                            '_value_1': 'xMedius-Fax-PT',
                        },
                        'index': 1,
                    },
                    {
                        'routePartitionName': {
                            '_value_1': 'Chartwell-Internal-ALL',
                        },
                        'index': 2,
                    },
                    {
                        'routePartitionName': {
                            '_value_1': 'SIP-Incoming-DID-PT',
                        },
                        'index': 3,
                    }
                ]
            },
            'name': 'MarkhamGW-Trunk-Incoming-CSS',
        }

        print('\naddCSS response:\n')
        try:
            resp = cucm.addCss(css)
            print(f'CSS successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: addCSS: {err}')

    def prep_add_Incoming_ANI_E164_css():
        css = {
            'description': 'Incoming-ANI-E164-CSS',
            'members': {
                'member': [
                    {
                        'routePartitionName': {
                            '_value_1': 'Incoming-ANI-E164-PT',
                        },
                        'index': 1,
                    }
                ]
            },
            'name': 'Incoming-ANI-E164-CSS',
        }

        print('\naddCSS response:\n')
        try:
            resp = cucm.addCss(css)
            print(f'CSS successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: addCSS: {err}')

    def prep_add_centralized_ld_css():
        css = {
            'description': 'Centralized-LD-CSS',
            'members': {
                'member': [
                    {
                        'routePartitionName': {
                            '_value_1': 'Block-Toll-Fraud-ALL',
                        },
                        'index': 1,
                    },
                    {
                        'routePartitionName': {
                            '_value_1': 'Centralized-Local-PT',
                        },
                        'index': 2,
                    },
                    {
                        'routePartitionName': {
                            '_value_1': 'Centralized-LD-PT',
                        },
                        'index': 3,
                    },
                    {
                        'routePartitionName': {
                            '_value_1': 'Centralized-E164-PT',
                        },
                        'index': 4,
                    }
                ]
            },
            'name': 'Centralized-LD-CSS',
        }

        print('\naddCSS response:\n')
        try:
            resp = cucm.addCss(css)
            print(f'CSS successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: addCSS: {err}')

    def prep_add_local_rg():
        local_rgs = [
            {'name': '911 Primary',
             'description': 'Emergency Calls LRG'},
            {'name': '911 Secondary',
             'description': 'Emergency Calls LRG'},
            {'name': 'PSTN Primary',
             'description': 'Primary LRG for Local and LD Calls'},
            {'name': 'PSTN Secondary',
             'description': 'Seconday LRG for Local and LD Calls'}
        ]
        for rg in local_rgs:
            cucm.addLocalRouteGroup(rg)

    def prep_hub_gw_dp():
        dp = {
            "name": f'Hub-GW-DP',
            "dateTimeSettingName": 'CMLocal',  # update to state timezone
            "regionName": f'Hub-Region',
            "locationName": None,
            "localRouteGroup": [
                {"name": 'PSTN Primary', "value": f'Centralized-SIP-Trunk-RG'}
            ],
            "mediaResourceListName": 'Hub-MRGL',
            "srstName": {
                '_value_1': 'Disable'
            },
            "callManagerGroupName": 'HUB-CMG',
            "networkLocale": None,
        }

        print('\naddDevicePool response:\n')
        try:
            resp = cucm.addDevicePool(dp)
            print(f'Device Pool successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: addDevicePool: {err}')

    def prep_add_Markham_SIP_trunk(name):
        # Create an object with the new SIP trunk fields and data
        sip_trunk_data = {
            'name': 'Markham-GW-Trunk',
            'description': 'Markham-GW-Trunk',
            'product': 'SIP Trunk',
            'class': 'Trunk',
            'protocol': 'SIP',
            'protocolSide': 'Network',
            'devicePoolName': 'Hub-GW-DP',
            'locationName': 'Hub_None',
            'securityProfileName': 'Non Secure SIP Trunk Profile',
            'sipProfileName': 'Voice Gateway SIP Profile',
            'presenceGroupName': 'Standard Presence group',
            'callingAndCalledPartyInfoFormat': 'Deliver DN only in connected party',
            'destinations': [],
            'mtpRequired': 'true',
            'runOnEveryNode': 'true',
            'pstnAccess': 'true',
            'sipAssertedType': 'PAI',
            'unknownPrefix': '+1',
            'callingPartySelection': 'Last Redirect Number (External)',
            'callingSearchSpaceName': 'MarkhamGW-Trunk-Incoming-CSS',
            'dtmfSignalingMethod': 'OOB and RFC 2833',
            'useDevicePoolCgpnTransformCssUnkn': 'false'
        }

        # Create and add a Destination object to the Destinations array
        sip_trunk_data['destinations'].append(
            {'destination': {
                'addressIpv4': f'172.25.116.118', 'port': '5060',
                'sortOrder': 1}
            }
        )

        print('\nadd SIP Trunk response:\n')
        try:
            resp = cucm.addSipTrunk(sip_trunk_data)
            print(f'SIP Trunk successfully added:\n {resp}')
        except Fault as err:
            print(f'Error: add SIP Trunk: {err}')

    prep_add_voice_gateway_sip_profile()
    prep_add_partition('Chartwell-Internal-ALL')
    prep_add_partition('xMedius-Fax-PT')
    prep_add_partition('SIP-Incoming-DID-PT')
    prep_add_partition('Block-Toll-Fraud-ALL')
    prep_add_partition('Centralized-Local-PT')
    prep_add_partition('Centralized-LD-PT')
    prep_add_partition('Incoming-ANI-E164-PT')
    prep_add_partition('Centralized-E164-PT')
    prep_add_markhamGW_incoming_css()
    prep_add_Incoming_ANI_E164_css()
    prep_add_centralized_ld_css()
    prep_add_local_rg()
    add_region('Hub')
    cucm.addMediaResourceList({'name': 'Hub-MRGL', 'members': []})
    cucm.addCallManagerGroup(
        {'name': 'Hub-CMG', 'tftpDefault': 'false', 'members': []})
    cucm.addCallManagerGroup(
        {'name': 'Residence-CMG', 'tftpDefault': 'false', 'members': []})
    prep_hub_gw_dp()
    prep_add_Markham_SIP_trunk()


def add_location(name: str):
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

    print('\naddLocation response:\n')
    try:
        resp = cucm.addLocation(location)
        print(f'Location successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: addLocation: {err}')


def add_region(name: str):
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
                   cucm.listRegion(
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
        resp = cucm.addRegion(new_region)
        print(f'Region successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: addRegion: {err}')


def add_srst(name: str, ip: str):
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
        resp = cucm.addSrst(srst)
        print(f'SRST successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: addRegion: {err}')


def add_algo_time_period(name: str, open_time: str, close_time: str):
    time_period1 = {
        'name': f'{name}-Algo-Closed00-{open_time[:2]}MS',
        'startTime': '00:00',
        'endTime': f'{open_time}',
        'startDay': 'Mon',
        'endDay': 'Sun',
        'monthOfYear': 'None',
        'dayOfMonth': 0,
        'description': f'{name} Algo Closed 00:00 - {open_time} Mon - Sun',
        'isPublished': 'false',
        'dayOfMonthEnd': 0,
        'monthOfYearEnd': 'None',
    }
    time_period2 = {
        'name': f'{name}-Algo-Closed{close_time[:2]}-24MS',
        'startTime': f'{close_time}',
        'endTime': '24:00',
        'startDay': 'Mon',
        'endDay': 'Sun',
        'monthOfYear': 'None',
        'dayOfMonth': 0,
        'description': f'{name} Algo Closed {close_time} - 24:00 Mon - Sun',
        'isPublished': 'false',
        'dayOfMonthEnd': 0,
        'monthOfYearEnd': 'None',
    }
    time_period3 = {
        'name': f'{name}-Algo-OpenMS',
        'startTime': f'{open_time}',
        'endTime': f'{close_time}',
        'startDay': 'Mon',
        'endDay': 'Sun',
        'monthOfYear': 'None',
        'dayOfMonth': 0,
        'description': f'{name} Algo Open {open_time} - {close_time} Mon - Sun',
        'isPublished': 'false',
        'dayOfMonthEnd': 0,
        'monthOfYearEnd': 'None',
    }

    print('\nadd Time Period response:\n')
    try:
        resp = cucm.addTimePeriod(time_period1)
        print(f'Time Period 1 successfully added:\n {resp}')
        resp = cucm.addTimePeriod(time_period2)
        print(f'Time Period 2 successfully added:\n {resp}')
        resp = cucm.addTimePeriod(time_period3)
        print(f'Time Period 3 successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: add Time Period: {err}')


def add_algo_time_schedule(name: str, open_time: str, close_time: str):
    time_schedule_closed = {
        'name': f'{name}-Algo-Closed',
        'description': f'{name}-Algo-Closed',
        'members': {'member': [
            {'timePeriodName': f'{name}-Algo-Closed00-{open_time[:2]}MS'},
            {'timePeriodName': f'{name}-Algo-Closed{close_time[:2]}-24MS'}]}
    }
    time_schedule_open = {
        'name': f'{name}-Algo-Open',
        'description': f'{name}-Algo-Open',
        'members': {'member': [{'timePeriodName': f'{name}-Algo-OpenMS'}]}
    }

    print('\nadd Time Schedule response:\n')
    try:
        resp = cucm.addTimeSchedule(time_schedule_closed)
        print(f'Time Schedule Closed successfully added:\n {resp}')
        resp = cucm.addTimeSchedule(time_schedule_open)
        print(f'Time Schedule Open successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: add Time Schedule: {err}')


def add_SIP_trunk(name: str, ip: str):
    # Create an object with the new SIP trunk fields and data
    sip_trunk_data = {
        'name': f'{name}-GW',
        'description': f'{name}-GW',
        'product': 'SIP Trunk',
        'class': 'Trunk',
        'protocol': 'SIP',
        'protocolSide': 'Network',
        'devicePoolName': f'{name}-DP',
        'locationName': f'{name}-Loc',
        'securityProfileName': 'Non Secure SIP Trunk Profile',
        'sipProfileName': 'Voice Gateway SIP Profile',
        'presenceGroupName': 'Standard Presence group',
        'callingAndCalledPartyInfoFormat': 'Deliver DN only in connected party',
        'destinations': [],
        'mediaResourceListName': 'Hub-MRGL',
        'runOnEveryNode': 'true',
    }

    # Create and add a Destination object to the Destinations array
    sip_trunk_data['destinations'].append(
        {'destination': {
            'addressIpv4': f'{ip}', 'port': '5060', 'sortOrder': 1}
        }
    )

    print('\nadd SIP Trunk response:\n')
    try:
        resp = cucm.addSipTrunk(sip_trunk_data)
        print(f'SIP Trunk successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: add SIP Trunk: {err}')


def add_route_group(name: str):
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
                'deviceName':
                    cucm.getSipTrunk(name=f'{name}-GW')['return']['sipTrunk'][
                        'name'],
                'deviceSelectionOrder': 1,
                'port': '0'
            },
            {
                'deviceName':
                    cucm.getSipTrunk(name=f'Markham-GW-Trunk')['return'][
                        'sipTrunk']['name'],
                'deviceSelectionOrder': 2,
                'port': '0'
            }
        ]
    )
    print('\naddRouteGroup response:\n')
    try:
        resp = cucm.addRouteGroup(rg)
        print(f'Route Group successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: addRouteGroup: {err}')


def add_device_pool(name: str):
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
    dp_webex = {
        "name": f'{name}-WebEx-DP',
        "dateTimeSettingName": 'CMLocal',
        "regionName": f'{name}-Region',
        "locationName": f'{name}-Loc',
        "localRouteGroup": [
            {"name": '911 Primary', "value": f'{name}-RG'},
            {"name": 'PSTN Primary', "value": f'Centralized-SIP-Trunk-RG'}
        ],
        "mediaResourceListName": 'Hub-MRGL',
        "srstName": 'Disable',  # Test this!
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
        resp = cucm.addDevicePool(dp)
        resp_webex = cucm.addDevicePool(dp_webex)
        print(f'Device Pool successfully added:\n {resp} \nand\n {resp_webex}')
    except Fault as err:
        print(f'Error: addDevicePool: {err}')


def add_default_partitions(name: str, gmt_value: int = -5):
    gmt_string = f'Etc/GMT+{gmt_value * -1}'

    partition_closed = {
        'name': f'{name}-Algo-Closed-PT',
        'description': f'{name}-Algo-Closed-PT',
        'timeScheduleIdName': f'{name}-Algo-Closed',
        'useOriginatingDeviceTimeZone': 'false',
        'timeZone': f'{gmt_string}'
    }
    partition_open = {
        'name': f'{name}-Algo-Open-PT',
        'description': f'{name}-Algo-Open-PT',
        'timeScheduleIdName': f'{name}-Algo-Open',
        'useOriginatingDeviceTimeZone': 'false',
        'timeZone': f'{gmt_string}'
    }
    partition_internal = {
        'name': f'{name}-Internal-PT',
        'description': f'{name}-Internal-PT',
        'timeScheduleIdName': None,
        'useOriginatingDeviceTimeZone': 'true',
        'timeZone': 'Etc/GMT'
    }
    partition_mi = {
        'name': f'{name}-MI-PT',
        'description': f'{name}-MI-PT',
        'timeScheduleIdName': None,
        'useOriginatingDeviceTimeZone': 'true',
        'timeZone': 'Etc/GMT'
    }
    print('\nadd Partition response:\n')
    try:
        resp = cucm.addRoutePartition(partition_closed)
        print(f'Partition successfully added:\n {resp}')
        resp = cucm.addRoutePartition(partition_open)
        print(f'Partition successfully added:\n {resp}')
        resp = cucm.addRoutePartition(partition_internal)
        print(f'Partition successfully added:\n {resp}')
        resp = cucm.addRoutePartition(partition_mi)
        print(f'Partition successfully added:\n {resp}')
    except Fault as err:
        print(f'Error: addPartition: {err}')


@app.command()
def add_full_site(name: str, srst_ip: str, algo_open: str = '06:00',
                  algo_close: str = '20:00', gmt_value: int = -5):
    add_location(name)
    add_region(name)
    add_srst(name, srst_ip)
    add_device_pool(name)
    add_algo_time_period(name, algo_open, algo_close)
    add_algo_time_schedule(name, algo_open, algo_close)
    add_default_partitions(name, gmt_value)
    # add_CSS
    # Add_vm_pilot
    # add_vm_profile
    # add_route_pattern
    add_SIP_trunk(name,
                  srst_ip)  # needs {name}-Trunk-Incoming-CSS for inbound calls
    # add route_group
    add_route_group(
        name)  # needs route groups in order to update local route groups


if __name__ == '__main__':
    running = True
    load_dotenv()
    cucm = connect_to_cucm(
        os.getenv('USERNAME'),
        base64.b64decode(os.getenv('EN_PASSWORD')).decode("utf-8")
    )
    print(cucm.getCCMVersion())

    app()
