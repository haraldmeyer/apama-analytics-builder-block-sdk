#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		
		# engine_receive process listening on all the channels.
		correlator.receive('all.evt')
		
		# This model will fail to deploy: missing a required param:
		modelId_failed = self.createTestModel('apamax.analyticsbuilder.samples.TimeWindow')
		
		# Checking that the model failed to load.
		self.assertGrep('all.evt', expr="Created.*No value provided for required parameter 'Duration.*'")

		# Deploying a new model with correct parameter.
		self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.TimeWindow', {'durationSecs':10.0})
		
		self.sendEventStrings(correlator,
		                      self.timestamp(1.9),
		                      self.inputEvent('value', 1, id = self.modelId),
		                      self.timestamp(3))
		
		# No output yet:
		self.assertBlockOutput('windowContents', [])
		
		self.sendEventStrings(correlator,
		                      self.timestamp(5.9),
		                      self.inputEvent('value', 2, id = self.modelId),
		                      self.timestamp(6.9),
		                      self.inputEvent('value', 3, id = self.modelId),
		                      self.timestamp(7.9),
		                      self.inputEvent('value', 4, id = self.modelId),
		                      self.timestamp(11.9),
							  self.inputEvent('value', 5, id = self.modelId),
		                      self.timestamp(14.9),
							  self.inputEvent('value', 6, id = self.modelId),
		                      self.timestamp(22),
							  self.inputEvent('reset', True, id = self.modelId),
							  self.timestamp(23.4),
							  self.inputEvent('value', 7, id = self.modelId),
							  self.timestamp(34),
							  )

	def validate(self):
		windowContents = [evt['properties']['timeWindow'] for evt in self.allOutputFromBlock(modelId = self.modelId) if evt['outputId'] == 'windowContents']
		def point(value, timestamp):
			return {'value': value, 'timestamp': timestamp}
		# As it's been 2 seconds since we sent the input, now the output should be generated.
		self.assertThat('outputLen == 3', outputLen = len(windowContents))
		self.assertThat('output == expected', output = windowContents[0], expected = [point(1,1), point(2, 5), point(3, 6), point(4, 7)])
		self.assertThat('output == expected', output = windowContents[1], expected = [point(4, 9), point(5, 11), point(6, 14)])
		self.assertThat('output == expected', output = windowContents[2], expected = [point(7, 22.5)])
