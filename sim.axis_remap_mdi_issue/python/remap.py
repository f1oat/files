import sys
import traceback
from interpreter import *
from emccanon import MESSAGE
from stdglue import *
from util import lineno, call_pydevd

def remap_m6(self, **words):
	MESSAGE("Tool change %d => %d" % (self.current_tool, self.selected_tool))
	print "Tool change %d => %d" % (self.current_tool, self.selected_tool)
	self.execute("G53 G0 Z20",lineno())
	self.execute("G53 G0 Z10",lineno())
	emccanon.CHANGE_TOOL(self.selected_pocket)
	self.current_pocket = self.selected_pocket
	self.selected_pocket = -1
	self.selected_tool = -1
	# cause a sync()
	self.set_tool_parameters()
	#self.toolchange_flag = True     # comment to avoid "/usr/bin/milltask (pid 6258) died on signal 11"
	yield INTERP_EXECUTE_FINISH
