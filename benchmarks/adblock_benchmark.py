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

workset1 = [
"https://stackoverflow.com/questions/17739095/changing-processor-architecture-with-node-gyp-configure",
"https://www.reddit.com/r/legaladvice/comments/9yyyru/ne_co_my_mom_wants_to_have_me_repossessed_from/",
"https://www.wired.com/story/butterball-turkey-talk-line-alexa-return-calls/",
"https://www.theguardian.com/world/2018/nov/21/steve-bannons-rightwing-europe-operation-undermined-by-election-laws",
"https://www.telegraph.co.uk/politics/2018/11/21/germany-threatens-snub-brexit-summit-unless-eu-ends-infighting/",
"https://www.nytimes.com/2018/11/20/us/politics/trump-khashoggi-statement.html",
"https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/edit",
"https://github.com/brave/brave-browser",
"https://www.metoffice.gov.uk/public/weather/forecast/gcpvn15h9#?date=2018-11-21",
]

workset2 = [
"https://boston.com",
"https://theblaze.com",
"https://thedailybeast.com",
"https://independent.co.uk",
"https://nypost.com",
"https://salon.com",
"https://cnn.com",
"https://sfgate.com",
"https://latimes.com",
"https://mirror.co.uk",
]

class NewTabAdblock(page.Page):

  def __init__(self, page_set, name, workset):
    url = 'chrome://newtab'
    self.workset = workset
    super(NewTabAdblock, self).__init__(
        url=url,
        name=name,
        page_set=page_set)

  def RunPageInteractions(self, action_runner):
    tabs = action_runner.tab.browser.tabs
    for (i, url) in enumerate(self.workset):
      new_tab = tabs.New()
      new_tab.action_runner.Navigate(url)

    for (i, url) in enumerate(self.workset):
      try:
        # tabs[i].action_runner.WaitForNavigate()
        tabs[i].action_runner.Wait(seconds=5)
      except py_utils.TimeoutException:
        logging.warning('WaitForNavigate() timeout')

    action_runner.MeasureMemory(deterministic_mode=True)

class AdblockWorkset1(story.StorySet):
  def __init__(self):
    super(AdblockWorkset1, self).__init__(
        archive_data_file='data/adblock.json',
        cloud_storage_bucket=story.PARTNER_BUCKET)
    self.AddStory(NewTabAdblock(self, "iteration1", workset1))
    self.AddStory(NewTabAdblock(self, "iteration2", workset1))
    self.AddStory(NewTabAdblock(self, "iteration3", workset1))

class AdblockWorkset2(story.StorySet):
  def __init__(self):
    super(AdblockWorkset2, self).__init__(
        archive_data_file='data/adblock.json',
        cloud_storage_bucket=story.PARTNER_BUCKET)
    self.AddStory(NewTabAdblock(self, "iteration1", workset2))
    self.AddStory(NewTabAdblock(self, "iteration2", workset2))
    self.AddStory(NewTabAdblock(self, "iteration3", workset2))


class AdblockBenchW1(MemoryInfra):

  def CreateStorySet(self, options):
    return AdblockWorkset1()

  @classmethod
  def Name(cls):
    return 'memory.adblock.workset1'

class AdblockBenchW2(MemoryInfra):

  def CreateStorySet(self, options):
    return AdblockWorkset2()

  @classmethod
  def Name(cls):
    return 'memory.adblock.workset2'
