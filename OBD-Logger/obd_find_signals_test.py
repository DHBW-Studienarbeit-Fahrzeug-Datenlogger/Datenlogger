"""
Created by: Max Vogt

Version: 1.0
Date: 30.12.2020
Description:
    Unittests for obd_find_signals module
"""

import unittest
from obd_find_signals import check_signal, obd_find_signals


class TestObdFindSignals(unittest.TestCase):
    """
    test find_signals function
    """
    def test_obd_find_signals_offline(self):
        """
        test offline variant
        default return values if obd can't connect
        """
        msg1, msg2, msg3, msg4, msg5, msg6, msg7 = obd_find_signals()
        self.assertEqual(type(msg1), str)
        self.assertEqual(msg1, "0")

    def test_obd_find_signals_online(self):
        """
        test online variant
        correct answer length
        """
        msg1, msg2, msg3, msg4, msg5, msg6, msg7 = obd_find_signals()
        self.assertEqual(type(msg1), str)
        self.assertEqual(len(msg1), 17)
        

class TestCheckSignal(unittest.TestCase):
    """
    test check signal function
    """
    def test_hex_to_bin(self):
        """
        test correct hex str to bin str transformation
        test ckecking specific positions
        """
        hex_str = "123456789ABCDEF"
        ret = check_signal(hex_str, 0)
        self.assertEqual(ret, True)
        ret = check_signal(hex_str, 4)
        self.assertEqual(ret, False)


if __name__ == '__main__':
    unittest.main()

