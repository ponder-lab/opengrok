#!/usr/bin/env python3

#
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# See LICENSE.txt included in this distribution for the specific
# language governing permissions and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at LICENSE.txt.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#

#
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
#

import os

import pytest

from opengrok_tools.utils.commandsequence import CommandSequence, \
    CommandSequenceBase


def test_str():
    cmds = CommandSequence(CommandSequenceBase("opengrok-master",
                                               [{"command": ['foo']},
                                                {"command": ["bar"]}]))
    assert str(cmds) == "opengrok-master"


@pytest.mark.skipif(not os.path.exists('/bin/sh')
                    or not os.path.exists('/bin/echo'),
                    reason="requires Unix")
def test_run_retcodes():
    cmd_list = [{"command": ["/bin/echo"]},
                {"command": ["/bin/sh", "-c",
                 "echo " + CommandSequence.PROJECT_SUBST + "; exit 0"]},
                {"command": ["/bin/sh", "-c",
                 "echo " + CommandSequence.PROJECT_SUBST + "; exit 1"]}]
    cmds = CommandSequence(CommandSequenceBase("opengrok-master", cmd_list))
    cmds.run()
    assert cmds.retcodes == {
        '/bin/echo opengrok-master': 0,
        '/bin/sh -c echo opengrok-master; exit 0': 0,
        '/bin/sh -c echo opengrok-master; exit 1': 1
    }


@pytest.mark.skipif(not os.path.exists('/bin/sh')
                    or not os.path.exists('/bin/echo'),
                    reason="requires Unix")
def test_terminate_after_non_zero_code():
    cmd_list = [{"command": ["/bin/sh", "-c",
                 "echo " + CommandSequence.PROJECT_SUBST + "; exit 255"]},
                {"command": ["/bin/echo"]}]
    cmds = CommandSequence(CommandSequenceBase("opengrok-master", cmd_list))
    cmds.run()
    assert cmds.retcodes == {
        '/bin/sh -c echo opengrok-master; exit 255': 255
    }


@pytest.mark.skipif(not os.path.exists('/bin/sh')
                    or not os.path.exists('/bin/echo'),
                    reason="requires Unix")
def test_exit_2_handling():
    cmd_list = [{"command": ["/bin/sh", "-c",
                 "echo " + CommandSequence.PROJECT_SUBST + "; exit 2"]},
                {"command": ["/bin/echo"]}]
    cmds = CommandSequence(CommandSequenceBase("opengrok-master", cmd_list))
    cmds.run()
    assert cmds.retcodes == {
        '/bin/sh -c echo opengrok-master; exit 2': 2
    }
    assert not cmds.failed


@pytest.mark.skipif(not os.path.exists('/bin/sh')
                    or not os.path.exists('/bin/echo'),
                    reason="requires Unix")
def test_driveon_flag():
    cmd_list = [{"command": ["/bin/sh", "-c",
                 "echo " + CommandSequence.PROJECT_SUBST + "; exit 2"]},
                {"command": ["/bin/echo"]},
                {"command": ["/bin/sh", "-c",
                             "echo " + CommandSequence.PROJECT_SUBST +
                             "; exit 1"]},
                {"command": ["/bin/sh", "-c",
                             "echo " + CommandSequence.PROJECT_SUBST]}]
    cmds = CommandSequence(CommandSequenceBase("opengrok-master",
                                               cmd_list, driveon=True))
    cmds.run()
    assert cmds.retcodes == {
        '/bin/sh -c echo opengrok-master; exit 2': 2,
        '/bin/echo opengrok-master': 0,
        '/bin/sh -c echo opengrok-master; exit 1': 1
    }
    assert cmds.failed


@pytest.mark.skipif(not os.path.exists('/bin/echo'),
                    reason="requires Unix")
def test_project_subst():
    cmd_list = [{"command": ["/bin/echo", CommandSequence.PROJECT_SUBST]}]
    cmds = CommandSequence(CommandSequenceBase("test-subst", cmd_list))
    cmds.run()

    assert cmds.outputs['/bin/echo test-subst'] == ['test-subst\n']
