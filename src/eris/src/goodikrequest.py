#!/usr/bin/env python

import argparse
import sys
import rospy
import baxter_interface
import tf
import copy
     
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


def quaternion2cartesian(quaternion_pose):
    Cartesian_pose = list(quaternion_pose['position']) # x, y, z
    Cartesian_pose.extend(tf.transformations.euler_from_quaternion(quaternion_pose['orientation'])) # appending r, p, y
    return Cartesian_pose

def cartesian2quaternion(Cartesian_pose):
    quaternion_pose = {}
    quaternion_pose['position'] = Cartesian_pose[0:2]
    quaternion_pose['orientation'] = tf.transformations.quaternion_from_euler(Cartesian_pose[3],Cartesian_pose[4],Cartesian_pose[5])
    return quaternion_pose


def ik_test(limb_arg):
    rospy.init_node("rsdk_ik_service_client")
    ns = "ExternalTools/" + limb_arg + "/PositionKinematicsNode/IKService"
    iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
    ikreq = SolvePositionIKRequest()
    hdr = Header(stamp=rospy.Time.now(), frame_id='base')

    limb = baxter_interface.Limb(limb_arg)
    current_pose = limb.endpoint_pose()
    new_pose = Pose()
    new_pose.position.x = current_pose['position'].x + 0.05
    new_pose.position.y = current_pose['position'].y
    new_pose.position.z = current_pose['position'].z 
    new_pose.orientation.x = current_pose['orientation'].x
    new_pose.orientation.y = current_pose['orientation'].y
    new_pose.orientation.z = current_pose['orientation'].z
    new_pose.orientation.w = current_pose['orientation'].w
    #joint_angles = self.ik_request(ik_pose)
    # servo up from current pose
    #self._guarded_move_to_joint_position(joint_angles)
    ikreq.pose_stamp.append(PoseStamped(header=hdr, pose=new_pose))
    print("test")

    try:
        print("test1")
        rospy.wait_for_service(ns, 15.0)
        resp = iksvc(ikreq)
        print("test2")
    except (rospy.ServiceException, rospy.ROSException), e:
         rospy.logerr("Service call failed: %s" % (e,))
    return 1
    
    print resp
    print resp.isValid
    if (resp.isValid[0]):
        print("SUCCESS - Valid Joint Solution Found:")
        # Format solution into Limb API-compatible dictionary
        limb_joints = dict(zip(resp.joints[0].names, resp.joints[0].angles))
        print limb_joints
        limb.move_to_joint_positions(limb_joints)
    else:
        print("INVALID POSE - No Valid Joint Solution Found.")
     
    return 0

def main():
    """RSDK Inverse Kinematics Example

    A simple example of using the Rethink Inverse Kinematics
    Service which returns the joint angles and validity for
    a requested Cartesian Pose.

    Run this example, passing the *limb* to test, and the
    example will call the Service with a sample Cartesian
    Pose, pre-defined in the example code, printing the
    response of whether a valid joint solution was found,
    and if so, the corresponding joint angles.
    """
    arg_fmt = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=arg_fmt,
                                     description=main.__doc__)
    parser.add_argument(
        '-l', '--limb', choices=['left', 'right'], required=True,
        help="the limb to test"
    )
    args = parser.parse_args(rospy.myargv()[1:])

    return ik_test(args.limb)
 
if __name__ == '__main__':
   	 sys.exit(main())

