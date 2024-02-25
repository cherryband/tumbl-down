import os
import unittest

from io import StringIO
from common import history


class HistoryTest(unittest.TestCase):
    def test_write_line(self):
        buffer = StringIO()
        history._write_line(buffer, "1st line")
        buffer.seek(0)
        self.assertEqual("1st line", buffer.getvalue().strip())
        
        history._write_line(buffer, "2nd line")
        buffer.seek(0)
        self.assertEqual("1st line\n2nd line", buffer.getvalue().strip())
        
        history._write_line(buffer, "3rd line", 0)
        buffer.seek(0)
        self.assertEqual("3rd line\n2nd line", buffer.getvalue().strip())
        
        history._write_line(buffer, "4th line", 1)
        buffer.seek(0)
        self.assertEqual("3rd line\n4th line", buffer.getvalue().strip())
    
    def test_get_last_read(self):
        buffer = StringIO("x, a, 15, 0\nb, x, post, 43")
        
        self.assertEqual(None, history.get_last_read(buffer, 'x', 'b')) 
        self.assertEqual(None, history.get_last_read(buffer, 'a', 'x', True)) 
        
        self.assertEqual(history.Post('15', 0), history.get_last_read(buffer, 'x', 'a')) 
        self.assertEqual((history.Post('post', 43), 1), history.get_last_read(buffer, 'b', 'x', True)) 
        
