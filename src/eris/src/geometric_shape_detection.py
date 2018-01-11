"""
Created on Mon Nov 15 20:46:39 2017
Author: Bogdan Duchevski - M00498871
PDE3433 Assignment II

Script for detecting and labelling up to 7 geometric shapes from video stream.
Uses simple object extraction features for efficient shape detection and recognition.
Detect: Pentagon, Hexagon, Star, Triangle, Square, Rectangle, Circle
GUI bars (R,G,B) for outline color and (O) for outline weight
Press ESC to stop:
"""
#from __future__ import print_function
# print(__doc__)
import cv_bridge
import time
import cv2
import rospy

from baxter_interface import CameraController
from sensor_msgs.msg import Image
import cv2
import numpy as np
import time
import math




import sys
import baxter_interface
import tf
import struct


     
from geometry_msgs.msg import (
	PoseStamped,
	Pose,
	Point,
	Quaternion,
	)
  
from std_msgs.msg import Header
     
from baxter_core_msgs.srv import (
	SolvePositionIK,
	SolvePositionIKRequest,
	)

def intt():
    limb = 'left'
    #x2,y2 = center
    movement = [0.0,-.5,0.0]#[0,0.303,-0.303]
    moveCartesianSpace(limb,movement)


def ik_request(limb,pose):
    hdr = Header(stamp=rospy.Time.now(), frame_id='base')
    ikreq = SolvePositionIKRequest()
    ikreq.pose_stamp.append(PoseStamped(header=hdr, pose=pose))
    ns = "ExternalTools/" + limb + "/PositionKinematicsNode/IKService"
    iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
    try:
        resp = iksvc(ikreq) # actual intent to find inverse kinematics solutions
    except (rospy.ServiceException, rospy.ROSException), e:
        rospy.logerr("Service call failed: %s" % (e,))
        return False

    resp_seeds = struct.unpack('<%dB' % len(resp.result_type), resp.result_type) 
    if (resp_seeds[0] != resp.RESULT_INVALID): # Check if result is valid
        limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position)) # reformat to use in movement
        print("Valid IK Joint Solution found:\n{0}".format(limb_joints))
        return limb_joints
    else:
        rospy.logerr("INVALID POSE - No Valid Joint Solution Found.")
        return False
    

def moveCartesianSpace(limb_arg,displacement):
    #rospy.init_node("rsdk_ik_service_client")
    limb = baxter_interface.Limb(limb_arg)
    current_pose = limb.endpoint_pose() # get current endpoint pose
    [dx,dy,dz] = displacement
    ik_pose = Pose() #create new pose from old one + displacements
    ik_pose.position.x = current_pose['position'].x + dx
    ik_pose.position.y = current_pose['position'].y + dy
    ik_pose.position.z = current_pose['position'].z + dz
    # for orientation you can choose relative or absolute values
    ik_pose.orientation.x = np.pi/2 #current_pose['orientation'].x
    ik_pose.orientation.y = 0.0 #current_pose['orientation'].y
    ik_pose.orientation.z = 0.0 #current_pose['orientation'].z
    ik_pose.orientation.w = 0.0 #current_pose['orientation'].w
    print ik_pose.orientation
    joint_angles = ik_request(limb_arg,ik_pose) # call the ik solver for the new pose
    if joint_angles:
        limb.move_to_joint_positions(joint_angles) # move to new joint coordinates





b = 0
g = 0
r = 255
strk = 1
rospy.init_node('get_camera_image')

left_camera = CameraController('left_hand_camera')
left_camera.open()

camera_image = None


intt()
# - Insert Contours and Text
def drawf(frame,cnt,name):
    asd=frame
    cv2.drawContours(asd,[cnt],0,(b,g,r),strk)
    (x, y, w, h) = cv2.boundingRect(cnt)

    x2 = x + w/2
    y2 = y + h/2
    center=(x2,y2)
    
    cv2.putText(asd, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 0, 1)
    img_size = asd.shape
    fr_y = (img_size[0])/2
    fr_x = (img_size[1])/2
    cord=[fr_x,fr_y]
    wd, ht, _ = frame.shape
    wd = wd / 2
    ht = ht / 2
    cntr = wd, ht
    print 'img_size',img_size
    print 'cord',cord
    print 'center',center
    #print 'cntr',cntr

# - GUI Define    
def nothing(x):
    pass
def bogdan_code(camera_image):
    cv2.namedWindow('preview')
    cv2.createTrackbar('O','preview',0,15,nothing)
    cv2.createTrackbar('R','preview',0,255,nothing)
    cv2.createTrackbar('G','preview',0,255,nothing)
    cv2.createTrackbar('B','preview',0,255,nothing)


    strk = cv2.getTrackbarPos('O','preview')
    r = cv2.getTrackbarPos('R','preview')
    g = cv2.getTrackbarPos('G','preview')
    b = cv2.getTrackbarPos('B','preboundingRectview')

    # - Contours
    imgn = cv2.GaussianBlur(camera_image, (5, 5), 0)
    for gray in cv2.split(imgn):
        for thrs in xrange(80, 255, 26):
            if thrs == 0:
                bin1 = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin2 = cv2.dilate(bin1, None)
            else:
                retval, bin2 = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(bin2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)           

           # - Find vertices
            for cnt in contours:                  
                #cv2.MatchShapes(cnt, object2, method, parameter=0)
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.01*cnt_len, True)              
                
                # - Limit Size
                if cv2.contourArea(cnt) > 1000 and cv2.contourArea(cnt) < 25000:
                    
                    if len(cnt)==5 and cv2.isContourConvex(cnt):
                            drawf(camera_image,cnt,'Pentagon')
                    elif len(cnt)==6 and cv2.isContourConvex(cnt):

                        drawf(camera_image,cnt,'Hexagon')
                        
                    elif len(cnt)==10:
                        (x, y, w, h) = cv2.boundingRect(cnt)
                        if abs(w-h)<=10:
                            drawf(camera_image,cnt,'Star')
                            
                    elif len(cnt)==3 and cv2.isContourConvex(cnt):
                        drawf(camera_image,cnt,'Triangle')
                        
                    elif len(cnt) == 4 and cv2.isContourConvex(cnt):                         
                        (x, y, w, h) = cv2.boundingRect(cnt)
                        if abs(w-h)<=20:
                            drawf(camera_image,cnt,'Square')
                        else:
                            drawf(camera_image,cnt,'Rectangle')
    return camera_image
'''
# - Display
cv2.imshow("preview", frame)

key = cv2.waitKey(20)
if key == 27: # exit on ESC
    break
cv2.destroyWindow("preview")
'''




def get_img(msg):
    global camera_image
    camera_image = msg_to_cv(msg)
    camera_image = bogdan_code(camera_image)
    cv2.imshow('image',camera_image)
    cv2.waitKey(1)

def msg_to_cv(msg):
    return cv_bridge.CvBridge().imgmsg_to_cv2(msg)

camera_subscriber = rospy.Subscriber( 'cameras/left_hand_camera/image', Image, get_img)

while camera_image==None:
    pass

#print camera_image

rospy.spin()




