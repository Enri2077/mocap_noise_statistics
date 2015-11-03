#!/usr/bin/env python
import time, os
from math import sqrt

import rospy
from geometry_msgs.msg import Pose2D
from geometry_msgs.msg import Point

# distance distribution interval
D_INTERVAL = 0.00015

def d(p1, p2):
	return sqrt( (p1.x-p2.x)**2 + (p1.y-p2.y)**2 )

class MyNode():
	def __init__(self):
		rospy.init_node('poses_listener', anonymous=True)
		
		rospy.Subscriber("/stat/markerset/pose2d", Pose2D, self.pose_callback)
		rospy.loginfo('Subscribed to "/stat/markerset/pose2d"')
		
		rospy.loginfo('cwd: %s', os.getcwd())
		
		self.prev_pos = None
		
		self.n = 0
		self.sum_d = 0
		self.avg = None
		
		self.d_distribution = {}
		
 
	def pose_callback(self, pose):
		self.n = self.n + 1
		
		if self.prev_pos:
			
			if self.prev_pos == pose:
			
				if 'lost' in self.d_distribution.keys():
					self.d_distribution['lost'] = self.d_distribution['lost'] + 1
				else:
					self.d_distribution['lost'] = 1
					
			else:
				
				delta = d(pose, self.prev_pos)
				n = int(delta/D_INTERVAL)
				if n in self.d_distribution.keys():
					self.d_distribution[n] = self.d_distribution[n] + 1
				else:
					self.d_distribution[n] = 1
					
			
			
			# save csv
			if not self.n%100:
				csv = ""
				for i in self.d_distribution.keys():
					if i != 'lost':
						csv = csv + "%f,%i\n" % (D_INTERVAL*i, self.d_distribution[i])
					else:
						csv = csv + "lost,%i\n" % (self.d_distribution[i])
				
				with open('log/mocap_noise_statistics.csv', 'w') as out:
					out.write(csv)
				
			# print distribution from 0 to 50
			if not self.n%10:
				print "\n\ndistance distribution"
				
				if 'lost' in self.d_distribution.keys():
					print "lost\t%s" % ("."*int(200.0*self.d_distribution['lost']/self.n))
				else:
					print "lost\t"
			
				for i in range(0, 50):
					if i in self.d_distribution.keys():
						print "%.5f\t%s" % (D_INTERVAL*i, "."*int(200.0*self.d_distribution[i]/self.n))
					else:
						print "%.5f" % (D_INTERVAL*i)
				
			#	self.sum_d = self.sum_d + delta
				
		self.prev_pos = pose
	

if __name__ == '__main__':
	try:
		MyNode()
		rospy.spin()
	except rospy.ROSInterruptException:
		rospy.loginfo("ROSInterrupt")
		

