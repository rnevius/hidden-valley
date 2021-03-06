"""Return useful data from any number of SNOTEL stations."""

from datetime import datetime, timedelta
from requests import Session
from zeep import Client
from zeep.transports import Transport

"""URI for the AWDB Web Service

See https://www.wcc.nrcs.usda.gov/web_service/AWDB_Web_Service_Reference.htm
for a complete reference, provided by the National Water and Climate Center (NWCC)"""
AWDB_URI = 'https://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL'

class Snotel(object):
    """
    Take a tuple of stations (as three-part strings)
    and use it to return useful snow depth and station data.
    """

    def __init__(self, stations=None):
        if not isinstance(stations, list):
            raise TypeError('stations must be a list')

        self.session = Session()
        self.session.verify = False
        transport = Transport(session=self.session)
        self.client = Client(AWDB_URI, transport=transport)

        self.stations = stations

    def get_data(self):
        """Gets instantaneous snow depth data for one or more stations."""

        begin_date = datetime.now() - timedelta(days=2)
        begin_date_str = begin_date.strftime('%Y-%m-%d')

        # Snow depth data, including suspect values
        snow_depth_data = self.client.service.getInstantaneousData(
            stationTriplets=self.stations,
            elementCd='SNWD',
            ordinal=1,
            beginDate=begin_date_str,
            endDate='9999-12-31',  # Arbitrary to capture the most recent data
            filter='ALL',
            unitSystem='ENGLISH'
        )

        # Filter out suspect ('S') values from station data
        for i, station in enumerate(snow_depth_data):
            snow_depth_data[i].values = [
                v for v in station.values if v.flag != 'S'
            ]

        return snow_depth_data

    def get_likely_snow_depth(self, station):
        """
        SNOTEL readings wobble.
        This method aims to provide a more accurate value for snow depth for a single station.
        """
        readings = [measurement.value for measurement in station.values]
        if not readings:
            raise ValueError('Station out of order.')

        if len(readings) < 3:
            return readings[-1]

        return max(readings[-3:])

    def get_metadata(self):
        """Retrieves station metadata for one or more stations in a single call."""
        if isinstance(self.stations, str):
            return self.client.service.getStationMetadata(self.stations)

        return self.client.service.getStationMetadataMultiple(self.stations)

    def get_snow_depth_range(self):
        """Return the range of current depths between stations."""
        snow_depths = [self.get_likely_snow_depth(station) for station in self.get_data()]
        min_depth = min(snow_depths)
        max_depth = max(snow_depths)

        if min_depth == max_depth:
            return '{}"'.format(min_depth)

        return '{}" - {}"'.format(min_depth, max_depth)
