#!/usr/bin/python
import unittest
import geocoder

'''Test Geocoder's functions with different queries, using new-york-small.osm test file'''

class TestGeocoder(unittest.TestCase):

    def test_match_house_number_and_street_correct_result(self):
        result = geocoder.match_house_number_and_street('722 broadway')
        self.assertIsInstance(result, int)

    def test_match_house_number_and_street_wrong_result(self):
        result = geocoder.match_house_number_and_street('aabbccxxyyzz')
        self.assertNotIsInstance(result, int)

    def test_match_postcode_and_city_correct_result(self):
        result = geocoder.match_postcode_and_city('10010 new york')
        self.assertIsInstance(result, int)

    def test_match_postcode_and_city_wrong_result(self):
        result = geocoder.match_postcode_and_city('1122334455667788')
        self.assertNotIsInstance(result, int)

    def test_match_site_name_correct_result(self):
        result = geocoder.match_site_name('starbucks')
        self.assertIsInstance(result, int)

    def test_match_site_name_wrong_result(self):
        result = geocoder.match_site_name('lsdjflsdjdksfj')
        self.assertNotIsInstance(result, int)

    def test_geocode_node_space_in_query(self):
        result = geocoder.geocode_node('washington square')
        self.assertIsInstance(result, int)

    def test_geocode_node_no_string(self):
        result = geocoder.geocode_node('')
        self.assertRaises(UnboundLocalError, result)

if __name__ == "__main__":
    unittest.main(verbosity=2)
