import unittest
from io import BytesIO
from eth.util.netstring import (header, encode, FileEncoder,
                                decode_file, Decoder)


class TestNetstring(unittest.TestCase):

    def setUp(self):
        self.test_data = b"Netstring module by Will McGugan"
        self.encoded_data = b"9:Netstring,6:module,2:by,4:Will,7:McGugan,"

    def test_header(self):

        tests = [ (b"netstring", b"9:"),
                  (b"Will McGugan", b"12:"),
                  (b"", b"0:") ]

        for test, result in tests:
            self.assertEqual(header(test), result)

    def test_encode(self):

        tests = [ (b"netstring", b"9:netstring,"),
                  (b"Will McGugan", b"12:Will McGugan,"),
                  (b"", b"0:,") ]

        for test, result in tests:
            self.assertEqual(encode(test), result)

    def test_file_encoder(self):

        file_out = BytesIO()
        data = self.test_data.split()

        encoder = FileEncoder(file_out)

        for s in data:
            encoder.write(s)

        encoded_data = file_out.getvalue()
        self.assertEqual(encoded_data, self.encoded_data)

    def test_decode_file(self):

        data = self.test_data.split()

        for buffer_size in range(1, len(self.encoded_data)):

            file_in = BytesIO(self.encoded_data[:])
            decoded_data = list(decode_file(file_in, buffer_size=buffer_size))
            self.assertEqual(decoded_data, data)

    def test_decoder(self):

        encoded_data = self.encoded_data

        for step in range(1, len(encoded_data)):

            i = 0
            chunks = []
            while i < len(encoded_data):
                chunks.append(encoded_data[i:i+step])
                i += step

            decoder = Decoder()

            decoded_data = []
            for chunk in chunks:
                for s in decoder.feed(chunk):
                    decoded_data.append(s)

            self.assertEqual(decoded_data, self.test_data.split())