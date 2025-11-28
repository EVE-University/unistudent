"""
unistudent Test
"""

# Django
from django.test import TestCase


class TestUnistudent(TestCase):
    """
    TestUnistudent
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Test setup
        :return:
        :rtype:
        """

        super().setUpClass()

    def test_unistudent(self):
        """
        Dummy test function
        :return:
        :rtype:
        """

        self.assertEqual(True, True)
