# encoding: utf-8
"""Internal module with python code shared between different scripts."""

import typing as _t
from typing import Any as _A, Optional as _O, Union as _U


def cleanup_as_single_line(string: str | None) -> str:
	"""Ensure the given string is a single line one."""
	if not string:
		return ''
	parts = (x.strip() for x in str(string).strip().splitlines())
	parts = (x for x in parts if x)
	try:
		return next(parts)
	except StopIteration:
		return ''


def is_true_str(str_bool: _O[str]) -> bool:
	"""Convert GitHub-action's "boolean" string into an actual bool."""
	str_bool = '' if str_bool is None else str(str_bool)
	str_bool = str_bool.strip()
	if not str_bool or str_bool.lower() == 'false':
		return False
	return True
