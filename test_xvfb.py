#!/usr/bin/env python3

import os
import sys
import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from xvfbwrapper import Xvfb


class TestXvfb(unittest.TestCase):

    def reset_display(self):
        os.environ['DISPLAY'] = ':0'

    def setUp(self):
        self.reset_display()

    def test_xvfb_binary_not_exists(self):
        with patch('xvfbwrapper.Xvfb.xvfb_exists') as xvfb_exists:
            xvfb_exists.return_value = False
            with self.assertRaises(EnvironmentError):
                Xvfb()

    def test_start(self):
        xvfb = Xvfb()
        self.addCleanup(xvfb.stop)
        xvfb.start()
        display_var = ':{}'.format(xvfb.new_display)
        self.assertEqual(display_var, os.environ['DISPLAY'])
        self.assertIsNotNone(xvfb.proc)

    def test_stop(self):
        orig_display = os.environ['DISPLAY']
        xvfb = Xvfb()
        xvfb.start()
        self.assertNotEqual(orig_display, os.environ['DISPLAY'])
        xvfb.stop()
        self.assertEqual(orig_display, os.environ['DISPLAY'])
        self.assertIsNone(xvfb.proc)

    def test_stop_with_xquartz(self):
        # Check that xquartz pattern for display server is dealt with by
        # xvfb.stop() and restored appropriately
        xquartz_display = '/private/tmp/com.apple.launchd.CgDzCWvNb1/org.macosforge.xquartz:0'
        with patch.dict('os.environ',
           {
               'DISPLAY':xquartz_display
           }) as mocked_env:
            xvfb = Xvfb()
            xvfb.start()
            self.assertNotEqual(xquartz_display, os.environ['DISPLAY'])
            xvfb.stop()
            self.assertEqual(xquartz_display, os.environ['DISPLAY'])
            self.assertIsNone(xvfb.proc)

    def test_start_without_existing_display(self):
        del os.environ['DISPLAY']
        xvfb = Xvfb()
        self.addCleanup(xvfb.stop)
        self.addCleanup(self.reset_display)
        xvfb.start()
        display_var = ':{}'.format(xvfb.new_display)
        self.assertEqual(display_var, os.environ['DISPLAY'])
        self.assertIsNotNone(xvfb.proc)

    def test_start_with_specific_display(self):
        xvfb = Xvfb(display=42)
        xvfb2 = Xvfb(display=42)
        self.addCleanup(xvfb.stop)
        xvfb.start()
        self.assertEqual(xvfb.new_display, 42)
        self.assertIsNotNone(xvfb.proc)
        with self.assertRaises(ValueError):
            xvfb2.start()

    def test_as_context_manager(self):
        orig_display = os.environ['DISPLAY']
        with Xvfb() as xvfb:
            display_var = ':{}'.format(xvfb.new_display)
            self.assertEqual(display_var, os.environ['DISPLAY'])
            self.assertIsNotNone(xvfb.proc)
        self.assertEqual(orig_display, os.environ['DISPLAY'])
        self.assertIsNone(xvfb.proc)

    def test_start_with_kwargs(self):
        w = 800
        h = 600
        depth = 16
        xvfb = Xvfb(width=w, height=h, colordepth=depth)
        self.addCleanup(xvfb.stop)
        xvfb.start()
        self.assertEqual(w, xvfb.width)
        self.assertEqual(h, xvfb.height)
        self.assertEqual(depth, xvfb.colordepth)
        display_var = ':{}'.format(xvfb.new_display)
        self.assertEqual(display_var, os.environ['DISPLAY'])
        self.assertIsNotNone(xvfb.proc)

    def test_start_with_arbitrary_kwargs(self):
        xvfb = Xvfb(nolisten='tcp')
        self.addCleanup(xvfb.stop)
        xvfb.start()
        display_var = ':{}'.format(xvfb.new_display)
        self.assertEqual(display_var, os.environ['DISPLAY'])
        self.assertIsNotNone(xvfb.proc)

    def test_start_fails_with_unknown_kwargs(self):
        xvfb = Xvfb(foo='bar')
        with self.assertRaises(RuntimeError):
            xvfb.start()

    def test_get_next_unused_display_does_not_reuse_lock(self):
        xvfb = Xvfb()
        xvfb2 = Xvfb()
        xvfb3 = Xvfb()
        self.addCleanup(xvfb._cleanup_lock_file)
        self.addCleanup(xvfb2._cleanup_lock_file)
        self.addCleanup(xvfb3._cleanup_lock_file)
        side_effect = [11, 11, 22, 11, 22, 11, 22, 22, 22, 33]
        with patch('xvfbwrapper.randint',
                   side_effect=side_effect) as mockrandint:
            self.assertEqual(xvfb._get_next_unused_display(), 11)
            self.assertEqual(mockrandint.call_count, 1)
            if sys.implementation.name == 'cpython':
                # ResourceWarning is only raised on CPython because
                # of an implementation detail in it's garbage collector.
                # This does not occur on other Python implementations
                # (like PyPy)
                with self.assertWarns(ResourceWarning):
                    self.assertEqual(xvfb2._get_next_unused_display(), 22)
                    self.assertEqual(mockrandint.call_count, 3)
                    self.assertEqual(xvfb3._get_next_unused_display(), 33)
                    self.assertEqual(mockrandint.call_count, 10)
            else:
                self.assertEqual(xvfb2._get_next_unused_display(), 22)
                self.assertEqual(mockrandint.call_count, 3)
                self.assertEqual(xvfb3._get_next_unused_display(), 33)
                self.assertEqual(mockrandint.call_count, 10)
    
    def test_environ_keyword_isolates_environment_modification(self):
        with patch.dict('os.environ',
           {
               'DISPLAY':':0'
           }) as mocked_env:
            # Check that start and stop methods modified the environ dict if
            # passed and does not modify os.environ
            env_duped = os.environ.copy()
            xvfb = Xvfb(environ=env_duped)
            xvfb.start()
            new_display = ":{}".format(xvfb.new_display)
            self.assertEqual(':0', os.environ['DISPLAY'])
            self.assertEqual(new_display, env_duped['DISPLAY'])
            xvfb.stop()
            self.assertEqual(':0', os.environ['DISPLAY'])
            self.assertEqual(':0', env_duped['DISPLAY'])
            self.assertIsNone(xvfb.proc)

