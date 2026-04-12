import unittest
from tests.test_alugueis_routes import TestAlugueisRoutes
import traceback

if __name__ == '__main__':
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestAlugueisRoutes)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except Exception as e:
        traceback.print_exc()
