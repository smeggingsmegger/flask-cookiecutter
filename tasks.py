#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Invoke tasks."""
import os
import json
import shutil

from invoke import task, run

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'cookiecutter.json'), 'r') as fp:
    COOKIECUTTER_SETTINGS = json.load(fp)
# Match default value of app_name from cookiecutter.json
COOKIE = os.path.join(HERE, COOKIECUTTER_SETTINGS['app_name'])
REQUIREMENTS = os.path.join(COOKIE, 'requirements.txt')


@task
def build(ctx):
    """Build the cookiecutter."""
    run('cookiecutter {0} --no-input'.format(HERE))


@task
def clean(ctx):
    """Clean out generated cookiecutter."""
    if os.path.exists(COOKIE):
        shutil.rmtree(COOKIE)
        print('Removed {0}'.format(COOKIE))
    else:
        print('App directory does not exist. Skipping.')


def _run_manage_command(command):
    run('python {0} {1}'.format(os.path.join(COOKIE, 'manage.py'), command), echo=True, pty=True)


@task(pre=[clean, build])
def test(ctx):
    """Run lint commands and tests."""
    run('pip install -r {0} --ignore-installed'.format(REQUIREMENTS), echo=True, pty=True)
    os.chdir(COOKIE)
    _run_manage_command('lint')
    _run_manage_command('test')
