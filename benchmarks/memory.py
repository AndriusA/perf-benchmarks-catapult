# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

import perf_benchmark

from telemetry import benchmark
from telemetry import story
from telemetry.timeline import chrome_trace_category_filter
from telemetry.timeline import chrome_trace_config
from telemetry.web_perf import timeline_based_measurement

import page_sets


# Regex to filter out a few names of statistics supported by
# Histogram.getStatisticScalar(), see:
#   https://github.com/catapult-project/catapult/blob/d4179a05/tracing/tracing/value/histogram.html#L645  pylint: disable=line-too-long
_IGNORED_STATS_RE = re.compile(
    r'(?<!dump)(?<!process)_(std|count|max|min|sum|pct_\d{4}(_\d+)?)$')


def CreateCoreTimelineBasedMemoryMeasurementOptions():
  """Creates necessary TBM options for measuring memory usage.

  Separated out so that code can be re-used in other benchmarks.
  """
  # Enable only memory-infra, to get memory dumps, and blink.console, to get
  # the timeline markers used for mapping threads to tabs.
  trace_memory = chrome_trace_category_filter.ChromeTraceCategoryFilter(
      filter_string='-*,blink.console,disabled-by-default-memory-infra')
  tbm_options = timeline_based_measurement.Options(
      overhead_level=trace_memory)
  tbm_options.config.enable_android_graphics_memtrack = True
  tbm_options.SetTimelineBasedMetrics(['memoryMetric'])
  # Setting an empty memory dump config disables periodic dumps.
  tbm_options.config.chrome_trace_config.SetMemoryDumpConfig(
      chrome_trace_config.MemoryDumpConfig())
  return tbm_options


def SetExtraBrowserOptionsForMemoryMeasurement(options):
  """Sets extra browser args necessary for measuring memory usage.

  Separated out so that code can be re-used in other benchmarks.
  """
  # Just before we measure memory we flush the system caches
  # unfortunately this doesn't immediately take effect, instead
  # the next page run is effected. Due to this the first page run
  # has anomalous results. This option causes us to flush caches
  # each time before Chrome starts so we effect even the first page
  # - avoiding the bug.
  options.clear_sytem_cache_for_browser_and_profile_on_start = True


def DefaultShouldAddValueForMemoryMeasurement(name):
  """Default predicate when measuring memory usage.

  Separated out so that code can be re-used in other benchmarks.
  """
  # TODO(crbug.com/610962): Remove this stopgap when the perf dashboard
  # is able to cope with the data load generated by TBMv2 metrics.
  return not _IGNORED_STATS_RE.search(name)


class MemoryInfra(perf_benchmark.PerfBenchmark):
  """Base class for new-generation memory benchmarks based on memory-infra.

  This benchmark records data using memory-infra (https://goo.gl/8tGc6O), which
  is part of chrome tracing, and extracts it using timeline-based measurements.
  """

  def CreateCoreTimelineBasedMeasurementOptions(self):
    return CreateCoreTimelineBasedMemoryMeasurementOptions()

  def SetExtraBrowserOptions(self, options):
    SetExtraBrowserOptionsForMemoryMeasurement(options)


class MemoryV8Benchmark(MemoryInfra):

  # Report only V8-specific and overall renderer memory values. Note that
  # detailed values reported by the OS (such as native heap) are excluded.
  _V8_AND_OVERALL_MEMORY_RE = re.compile(
      r'renderer_processes:'
      r'(reported_by_chrome:v8|reported_by_os:system_memory:[^:]+$)')

  def CreateCoreTimelineBasedMeasurementOptions(self):
    v8_categories = [
        'blink.console', 'renderer.scheduler', 'v8', 'webkit.console']
    memory_categories = ['blink.console', 'disabled-by-default-memory-infra']
    category_filter = chrome_trace_category_filter.ChromeTraceCategoryFilter(
        ','.join(['-*'] + v8_categories + memory_categories))
    options = timeline_based_measurement.Options(category_filter)
    options.SetTimelineBasedMetrics(['v8AndMemoryMetrics'])
    # Setting an empty memory dump config disables periodic dumps.
    options.config.chrome_trace_config.SetMemoryDumpConfig(
        chrome_trace_config.MemoryDumpConfig())
    return options

  @classmethod
  def ShouldAddValue(cls, name, _):
    if 'memory:chrome' in name:
      # TODO(petrcermak): Remove the first two cases once
      # https://codereview.chromium.org/2018503002/ lands in Catapult and rolls
      # into Chromium.
      return ('renderer:subsystem:v8' in name or
              'renderer:vmstats:overall' in name or
              bool(cls._V8_AND_OVERALL_MEMORY_RE.search(name)))
    return 'v8' in name


