
from telemetry import benchmark
from telemetry.web_perf import timeline_based_measurement
from telemetry.timeline import chrome_trace_category_filter
from telemetry.page import shared_page_state
from telemetry.timeline import chrome_trace_config
from telemetry.page import cache_temperature
# from telemetry import story as story_module

from telemetry import story
from telemetry import page

import logging
import py_utils

from memory import *


class TrivialPageWithAds(page.Page):
  def __init__(self, page_set, deterministic_mode):
    self.deterministic_mode = deterministic_mode
    super(TrivialPageWithAds, self).__init__(
      url='chrome://newtab',
      name=self.__class__.__name__,
      # cache_temperature=cache_temperature.COLD,
      page_set=page_set)

  def RunPageInteractions(self, action_runner):
    action_runner.Wait(1)
    action_runner.Navigate('http://127.0.0.1:8080/verge.html')
    action_runner.Wait(3)
    action_runner.MeasureMemory(deterministic_mode=self.deterministic_mode)

class TrivialPageMoreAds(page.Page):
  def __init__(self, page_set, deterministic_mode):
    self.deterministic_mode = deterministic_mode
    super(TrivialPageMoreAds, self).__init__(
      url='http://127.0.0.1:8080/verge_moreads.html',
      name=self.__class__.__name__,
      page_set=page_set)

  def RunPageInteractions(self, action_runner):
    action_runner.Wait(3)
    action_runner.MeasureMemory(deterministic_mode=self.deterministic_mode)

class TrivialPageBlank(page.Page):
  def __init__(self, page_set, deterministic_mode):
    self.deterministic_mode = deterministic_mode
    super(TrivialPageBlank, self).__init__(
      url='http://127.0.0.1:8080/verge_blank.html',
      name=self.__class__.__name__,
      page_set=page_set)

  def RunPageInteractions(self, action_runner):
    action_runner.Wait(3)
    action_runner.MeasureMemory(deterministic_mode=self.deterministic_mode)

class BlockingWorkset(story.StorySet):
  def __init__(self):
    super(BlockingWorkset, self).__init__(
        archive_data_file='data/adblock_response_overheads_benchmark_blocking.json',
        cloud_storage_bucket=story.PARTNER_BUCKET)
    self.AddStory(TrivialPageWithAds(self, deterministic_mode = False))
    # self.AddStory(TrivialPageMoreAds(self, deterministic_mode = False))
    # self.AddStory(TrivialPageBlank(self, deterministic_mode = False))

class OverheadBlocking(MemoryInfra):
  options = {'pageset_repeat': 5}
  def CreateStorySet(self, options):
    return BlockingWorkset()

  @classmethod
  def Name(cls):
    return 'memory.adblock_overhead.blocking'
