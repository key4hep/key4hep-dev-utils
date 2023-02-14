import parse
import sys
import unittest

def test(self, out):
    vals = parse.main()
    self.assertEqual(out, vals)

class OneUrlTest(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      Depends on https://github.com/jmcarcell/k4FWCore/pull/1
      """
      out = ['jmcarcell k4FWCore fix-warnings']
      sys.argv = ['', inp]

      test(self, out)

class NoUrlTest(unittest.TestCase):
    def test(self):
      inp = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu depends on"""
      out = []
      sys.argv = ['', inp]
      test(self, out)

class OneUrlBreakline(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu depends on
      https://github.com/jmcarcell/k4FWCore/pull/1
      """
      out = ['jmcarcell k4FWCore fix-warnings']
      sys.argv = ['', inp]
      test(self, out)

class OneUrlInconsistentSpacing(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      depends     on               https://github.com/jmcarcell/k4FWCore/pull/1
      """
      out = ['jmcarcell k4FWCore fix-warnings']
      sys.argv = ['', inp]
      test(self, out)

class TwoUrlCommaSeparated(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      depends on https://github.com/jmcarcell/k4FWCore/pull/1, https://github.com/key4hep/EDM4hep/pull/1
      """
      out = ['jmcarcell k4FWCore fix-warnings', 'vvolkl EDM4HEP build_infrastructure']
      sys.argv = ['', inp]
      test(self, out)

class TwoUrlCommaSeparatedNoSpace(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      depends on https://github.com/jmcarcell/k4FWCore/pull/1,https://github.com/key4hep/EDM4hep/pull/1
      """
      out = ['jmcarcell k4FWCore fix-warnings', 'vvolkl EDM4HEP build_infrastructure']
      sys.argv = ['', inp]
      test(self, out)

class TwoUrlAndSeparated(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      depends on https://github.com/jmcarcell/k4FWCore/pull/1 and https://github.com/key4hep/EDM4hep/pull/1
      """
      out = ['jmcarcell k4FWCore fix-warnings', 'vvolkl EDM4HEP build_infrastructure']
      sys.argv = ['', inp]
      test(self, out)

class ThreeUrlCommaSeparated(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      depends on https://github.com/jmcarcell/k4FWCore/pull/1,
      https://github.com/key4hep/EDM4hep/pull/1,https://github.com/AIDASoft/podio/pull/12
      """
      out = ['jmcarcell k4FWCore fix-warnings', 'vvolkl EDM4HEP build_infrastructure', 'gaede podio extracode_in_components']
      sys.argv = ['', inp]
      test(self, out)

class ThreeUrlCommaAndSeparated(unittest.TestCase):
    def test(self):
      inp = """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
      eiusmod tempor incididunt ut labore et dolore magna asaeu
      depends on https://github.com/jmcarcell/k4FWCore/pull/1,
      https://github.com/key4hep/EDM4hep/pull/1 and https://github.com/AIDASoft/podio/pull/12
      """
      out = ['jmcarcell k4FWCore fix-warnings', 'vvolkl EDM4HEP build_infrastructure', 'gaede podio extracode_in_components']
      sys.argv = ['', inp]
      test(self, out)
