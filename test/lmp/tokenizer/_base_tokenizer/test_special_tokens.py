r"""Test `lmp.tokenizer.BaseTokenizer.special_tokens`.

Usage:
    python -m unittest \
        test/lmp/tokenizer/_base_tokenizer/test_special_tokens.py
"""

# built-in modules

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect
import unittest

from typing import Generator
from typing import Iterator

# self-made modules

from lmp.tokenizer import BaseTokenizer


class TestSpecialTokens(unittest.TestCase):
    r"""Test Case for `lmp.tokenizer.BaseTokenizer.special_tokens`."""

    def test_signature(self):
        r"""Ensure signature consistency."""
        msg = 'Inconsistent method signature.'

        self.assertEqual(
            inspect.signature(BaseTokenizer.special_tokens),
            inspect.Signature(
                parameters=None,
                return_annotation=Generator[str, None, None]
            ),
            msg=msg
        )

    def test_yield_value(self):
        r"""Return iterator which yield `str`."""
        msg = 'Must return iterator which yield `str`.'
        examples = ('[BOS]', '[EOS]', '[PAD]', '[UNK]')

        self.assertIsInstance(
            BaseTokenizer.special_tokens(),
            Iterator,
            msg=msg
        )

        out_tokens = list(BaseTokenizer.special_tokens())

        for i, ans_token in enumerate(examples):
            self.assertIsInstance(out_tokens[i], str, msg=msg)
            self.assertEqual(out_tokens[i], ans_token, msg=msg)


if __name__ == '__main__':
    unittest.main()
