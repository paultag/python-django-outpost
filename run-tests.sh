#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=outpost.tests.settings
./admin migrate
py.test outpost --ds=outpost.tests.settings -vs
