import sys, unittest, re, os.path

from WorkflowTest import WorkflowTest
from SpiffWorkflow.storage import XmlReader
from xml.parsers.expat import ExpatError

class XmlReaderTest(WorkflowTest):
    def setUp(self):
        WorkflowTest.setUp(self)
        self.reader = XmlReader()

    def testParseString(self):
        self.assertRaises(ExpatError,
                          self.reader.parse_string,
                          '')
        self.reader.parse_string('<xml></xml>')


    def testParseFile(self):
        # File not found.
        self.assertRaises(IOError,
                          self.reader.parse_file,
                          'foo')

        # 0 byte sized file.
        file = os.path.join(os.path.dirname(__file__), 'specs', 'empty1.xml')
        self.assertRaises(ExpatError, self.reader.parse_file, file)

        # File containing only "<xml></xml>".
        file = os.path.join(os.path.dirname(__file__), 'specs', 'empty2.xml')
        self.reader.parse_file(file)

        # Read a complete workflow.
        file = os.path.join(os.path.dirname(__file__), 'specs', 'spiff', 'workflow1.xml')
        self.reader.parse_file(file)


    def testRunWorkflow(self):
        file = os.path.join(os.path.dirname(__file__), 'specs', 'spiff', 'workflow1.xml')
        workflow_list = self.reader.parse_file(file)
        for wf in workflow_list:
            self._runWorkflow(wf)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(XmlReaderTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
