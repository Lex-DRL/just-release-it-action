#!/usr/bin/env python
# encoding: utf-8
"""
Utility script, acting as a single switch:
depending on a value of a single bool-like input, set the outputs either
from the corresponding ``true``- or ``false``-branch inputs.

The input/output names are provided as script arguments:
- first is the name of "switch" env-var,
- second is a string-boolean toggle to force one-line values in the output
- followed by triplets of names:
	- output
	- env-var with true-input value
	- env-var with false-input value
"""

import typing as _t
from typing import Any as _A, Optional as _O, Union as _U

from itertools import zip_longest
import os
import sys
import uuid

from _shared_just_release_it import *


class OutputsTuple(_t.NamedTuple):
	out_name: str
	true_value: str
	false_value: str

	def format(self) -> str:
		return f'{self.out_name}: {self.true_value!r} / {self.false_value!r}'


def _format_single_github_output(name: str, value: str, _print=False) -> str:
	assert name and isinstance(name, str)
	value = '' if value is None else str(value)
	if _print:
		print(f"  {name!r}: {value!r}")

	value_lines = value.splitlines()
	if len(value_lines) < 2:
		# Single-line value
		value = value_lines[0] if value_lines[0] else ''
		return f'{name}={value}\n'

	# Multi-line value
	delimiter = 'EOF'
	while delimiter in value:
		delimiter = uuid.uuid4().hex  # random, cannot be guessed/injected
		delimiter = f'EOF{delimiter}'
	return (
		f'{name}<<{delimiter}\n'
		f'{value}\n'
		f'{delimiter}\n'
	)


def set_out_values(
	switcher: bool, *triplets: OutputsTuple,
	github_output_env: str = 'GITHUB_OUTPUT',
):
	"""Depending on the switcher, set output values to either ``true`` inputs or ``false`` inputs."""
	def get_true_value(triplet: OutputsTuple):
		return triplet.true_value

	def get_false_value(triplet: OutputsTuple):
		return triplet.false_value

	get_value = get_true_value if switcher else get_false_value

	output_path = get_env_var(github_output_env, 'github-output env-var')
	if not output_path:
		raise ValueError(f"Empty path for github-output: {output_path!r}")

	print("Setting output values:")
	output_lines = [
		_format_single_github_output(
			repl.out_name, get_value(repl), _print=True
		)
		for repl in triplets
	]
	with open(output_path, 'at', encoding='utf-8') as f:
		f.writelines(output_lines)
	print("--- Outputs are set")


def _check_env_var_name(name: _O[str], what: str = 'an env-var') -> str:
	name = '' if name is None else str(name)
	if not name:
		raise ValueError(f"Empty name for {what}: {name!r}")
	return name


def get_env_var(name: str, what: str = 'an env-var') -> str:
	name = _check_env_var_name(name, what)
	value = os.environ.get(name)
	return str(value) if value else ''


def _dummy_f(val):
	return val


def _parse_triplet_args_gen(args: _t.Iterator[str], force_one_line=True) -> _t.Generator[OutputsTuple, _A, None]:
	"""Process replacement args sequence into valid ``OutputsTuple`` sequence."""
	triplets = zip_longest(args, args, args, fillvalue=None)
	cleanup = cleanup_as_single_line if force_one_line else _dummy_f
	for out_name, true_name, false_name in triplets:
		if true_name is None or false_name is None:
			raise RuntimeError(
				f"Not a valid env-names triplet: "
				f"{out_name!r}, {true_name!r}, {false_name!r}"
			)
		out_name = _check_env_var_name(out_name, 'an out env-var')
		true_value = cleanup(
			get_env_var(true_name, 'a true-value env-var')
		)
		false_value = cleanup(
			get_env_var(false_name, 'a false-value env-var')
		)
		yield OutputsTuple(out_name, true_value, false_value)


def switcher_parse_args(*args: str):
	"""Read the actual script values from the provided env-vars."""
	args = iter(args)
	try:
		switcher_name = next(args)
	except StopIteration:
		raise RuntimeError("First (switcher) env-name arg is required")
	try:
		is_oneliner_name = next(args)
	except StopIteration:
		raise RuntimeError("Second (force-single-line) env-name arg is required")

	switcher_str = os.environ.get(switcher_name)
	if switcher_str is None:
		raise RuntimeError(f"Switcher env-var ({switcher_name!r}) isn't set")
	switcher_bool = is_true_str(switcher_str)

	is_oneliner_str = os.environ.get(is_oneliner_name)
	if is_oneliner_name is None:
		raise RuntimeError(f"Switcher env-var ({is_oneliner_name!r}) isn't set")
	is_oneliner_bool = is_true_str(is_oneliner_str)

	triplets = list(_parse_triplet_args_gen(args, force_one_line=is_oneliner_bool))

	print("Detected switch-script settings:")
	print(f"  Switch value ({switcher_name!r}): {switcher_bool!r}")
	print(f"  Force single-line values ({is_oneliner_name!r}): {is_oneliner_bool!r}")
	print('')
	print(f"  Outputs (name / true-value / false-value):")
	for triplet in triplets:
		print(f"    {triplet.format()}")
	print('')

	return switcher_bool, triplets


def switcher_main(
	*args: str,
	github_output_env: str = 'GITHUB_OUTPUT',
) -> None:
	switcher_bool, triplets = switcher_parse_args(*args)
	set_out_values(
		switcher_bool, *triplets,
		github_output_env=github_output_env,
	)


if __name__ == '__main__':
	switcher_main(*sys.argv[1:])
