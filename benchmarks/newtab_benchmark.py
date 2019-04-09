# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from telemetry import benchmark
from telemetry.web_perf import timeline_based_measurement
from telemetry.timeline import chrome_trace_category_filter
from telemetry.page import shared_page_state
from telemetry.timeline import chrome_trace_config
# from telemetry import story as story_module

from telemetry import story
from telemetry import page

import logging
import py_utils

import re
import perf_benchmark
from memory import *


_DUMP_WAIT_TIME = 3

class NewTab50(page.Page):

  def __init__(self, page_set):
    url = 'chrome://newtab'
    super(NewTab50, self).__init__(
        url=url,
        name=url,
        page_set=page_set)

  def _DumpMemory(self, action_runner, phase):
    with action_runner.CreateInteraction(phase):
      action_runner.Wait(_DUMP_WAIT_TIME)
      action_runner.ForceGarbageCollection()
      action_runner.SimulateMemoryPressureNotification('critical')
      action_runner.Wait(_DUMP_WAIT_TIME)
      action_runner.MeasureMemory(deterministic_mode=True)

  def RunPageInteractions(self, action_runner):
    tabs = action_runner.tab.browser.tabs
    for _ in xrange(50):
      new_tab = tabs.New()
      new_tab.action_runner.Navigate(self._url)

    for i in xrange(50):
      try:
        tabs[i].action_runner.WaitForNetworkQuiescence()
      except py_utils.TimeoutException:
        logging.warning('WaitForNetworkQuiescence() timeout')

    self._DumpMemory(action_runner, 'post')

class NewTabs(story.StorySet):
  def __init__(self):
    super(NewTabs, self).__init__(
        archive_data_file='data/newtab.json',
        cloud_storage_bucket=story.PARTNER_BUCKET)
    self.AddStory(NewTab50(self))


class NewTabsBench(MemoryInfra):

  def CreateStorySet(self, options):
    return NewTabs()

  @classmethod
  def Name(cls):
    return 'memory.newtabs50'
