# Copyright (C) 2017 MongoDB Inc.
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Utility methods and classes for testing IDL passes."""

from __future__ import absolute_import, print_function, unicode_literals

import unittest

if __name__ == 'testcase':
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from context import idl
else:
    from .context import idl


def errors_to_str(errors):
    # type: (idl.errors.ParserErrorCollection) -> unicode
    """Dump the list of errors as a multiline text string."""
    if errors is not None:
        return "\n".join(errors.to_list())
    return "<empty>"


class IDLTestcase(unittest.TestCase):
    """IDL Test case base class."""

    def _parse(self, doc_str):
        # type: (unicode) -> idl.syntax.IDLParsedSpec
        """Parse a document and throw a unittest failure if it fails to parse as a valid YAML document."""

        try:
            return idl.parser.parse(doc_str)
        except:  # pylint: disable=bare-except
            self.fail("Failed to parse document:\n%s" % (doc_str))

    def _assert_parse(self, doc_str, parsed_doc):
        # type: (unicode, idl.syntax.IDLParsedSpec) -> None
        """Assert a document parsed correctly by the IDL compiler and returned no errors."""
        self.assertIsNone(parsed_doc.errors,
                          "Expected no parser errors\nFor document:\n%s\nReceived errors:\n\n%s" %
                          (doc_str, errors_to_str(parsed_doc.errors)))
        self.assertIsNotNone(parsed_doc.spec, "Expected a parsed doc")

    def assert_parse(self, doc_str):
        # type: (unicode) -> None
        """Assert a document parsed correctly by the IDL compiler and returned no errors."""
        parsed_doc = self._parse(doc_str)
        self._assert_parse(doc_str, parsed_doc)

    def assert_parse_fail(self, doc_str, error_id, multiple=False):
        # type: (unicode, unicode, bool) -> None
        """
        Assert a document parsed correctly by the YAML parser, but not the by the IDL compiler.

        Asserts only one error is found in the document to make future IDL changes easier.
        """
        parsed_doc = self._parse(doc_str)

        self.assertIsNone(parsed_doc.spec, "Expected no parsed doc")
        self.assertIsNotNone(parsed_doc.errors, "Expected parser errors")

        # Assert that negative test cases are only testing one fault in a test.
        # This is impossible to assert for all tests though.
        self.assertTrue(
            multiple or parsed_doc.errors.count() == 1,
            "For document:\n%s\nExpected only error message '%s' but received multiple errors:\n\n%s"
            % (doc_str, error_id, errors_to_str(parsed_doc.errors)))

        self.assertTrue(
            parsed_doc.errors.contains(error_id),
            "For document:\n%s\nExpected error message '%s' but received only errors:\n %s" %
            (doc_str, error_id, errors_to_str(parsed_doc.errors)))

