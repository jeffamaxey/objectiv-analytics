"""
CHECKLOCK HOLMES CLI
Usage:
    checklock-holmes.py [-x | --exitfirst] [-e | --engine=<engine>...] [--nb=<file>...] [--gh_issues_dir=<ghi>] [--dump_nb_scripts_dir=<nbs_dir>] [-t | --timeit]
    checklock-holmes.py -h | --help

Options:
    -h --help                       Show this screen.
    -x --exitfirst                  Stop checks after first fail.
    -e --engine=<engine>...         Engines to run checks. Current supported engines: [{supported_engines}] [default: all].
    --nb=<file>...                  Notebooks to be checked [default: {default_nb_dir}].
    --gh_issues_dir=<ghi>           Directory for logging github issues [default: {default_github_issues_dir}].
    --dump_nb_scripts_dir<nbs_dir>  Directory where to dump notebook scripts.
    -t --timeit                     Time each cell

Copyright 2022 Objectiv B.V.
"""
from docopt import docopt
from tqdm import tqdm

from checklock_holmes.models.nb_checker_models import (
    NoteBookCheckSettings, NoteBookMetadata
)
from checklock_holmes.nb_checker import NoteBookChecker
from checklock_holmes.utils.constants import (
    DEFAULT_GITHUB_ISSUES_DIR, DEFAULT_NOTEBOOKS_DIR, NOTEBOOK_EXTENSION
)
from checklock_holmes.utils.helpers import (
    display_check_results, get_github_issue_filename, store_github_issue,
    store_nb_script
)
from checklock_holmes.utils.supported_engines import SupportedEngine


def check_notebooks(check_settings: NoteBookCheckSettings, exit_on_fail: bool) -> None:
    checks = []
    github_issues_file_path = f'{check_settings.github_issues_dir}/{get_github_issue_filename()}'

    total_checks = len(check_settings.notebooks_to_check) * len(check_settings.engines_to_check)

    stop_checks = False
    with tqdm(total=total_checks) as pbar:
        for nb in check_settings.notebooks_to_check:
            nb_metadata = NoteBookMetadata(path=nb)
            nb_checker = NoteBookChecker(
                metadata=nb_metadata, display_cell_timing=check_settings.display_cell_timing,
            )
            for engine in check_settings.engines_to_check:
                pbar.set_description(f'Starting {engine} checks for {nb_metadata.name}.{NOTEBOOK_EXTENSION}...')

                if check_settings.dump_nb_scripts_dir:
                    script_path = f'{check_settings.dump_nb_scripts_dir}/{nb_checker.metadata.name}_{engine}.py'
                    store_nb_script(script_path, nb_checker.get_script(engine, is_execution=False))

                nb_check = nb_checker.check_notebook(engine)
                checks.append(nb_check)
                pbar.update(1)

                if nb_check.error:
                    store_github_issue(nb_check, github_issues_file_path)
                    if exit_on_fail:
                        stop_checks = True
                        break

            if stop_checks:
                break

    display_check_results(
        nb_checks=checks,
        github_files_path=github_issues_file_path,
        display_cell_timings=check_settings.display_cell_timing,
    )


if __name__ == '__main__':
    cli_docstring = __doc__.format(
        supported_engines=', '.join([engine for engine in SupportedEngine]),
        default_nb_dir=DEFAULT_NOTEBOOKS_DIR,
        default_github_issues_dir=DEFAULT_GITHUB_ISSUES_DIR,
    )
    arguments = docopt(cli_docstring, help=True, options_first=False)
    nb_check_settings = NoteBookCheckSettings(
        engines_to_check=arguments['--engine'],
        github_issues_dir=arguments['--gh_issues_dir'],
        dump_nb_scripts_dir=arguments['--dump_nb_scripts_dir'],
        notebooks_to_check=arguments['--nb'],
        display_cell_timing=arguments['--timeit']
    )
    check_notebooks(nb_check_settings, exit_on_fail=arguments['--exitfirst'])
