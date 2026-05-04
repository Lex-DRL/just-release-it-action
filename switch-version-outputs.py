#!/usr/bin/env python
# encoding: utf-8
"""
"""

from switch_outputs import *


def _enforce_pre_release(is_pre: bool, triplets: list[OutputsTuple]) -> list[OutputsTuple]:
	print(f"  Enforced pre-release state: {is_pre!r}")
	print('')
	triplets_dict = {x.out_name: x for x in triplets}

	value_str = 'true' if is_pre else 'false'
	triplets_dict['is_pre'] = OutputsTuple('is_pre', value_str, value_str)
	return list(triplets_dict.values())


def version_main(github_output_env: str = 'GITHUB_OUTPUT', ) -> None:
	switcher, triplets = switcher_parse_args(
		# Everything's hardcoded - same names as in the action:
		'switch', 'force_one_line',
		'tag', 'tag_skip', 'tag_std',
		'raw_version', 'raw_version_skip', 'raw_version_std',
		'is_pre', 'is_pre_skip', 'is_pre_std',
	)

	force_pre_str = get_env_var('force_pre', 'a force-pre-release env-var')
	if force_pre_str or switcher:
		triplets = _enforce_pre_release(is_true_str(force_pre_str), triplets)

	set_out_values(
		switcher, *triplets,
		github_output_env=github_output_env,
	)


if __name__ == '__main__':
	version_main()
