import rospy
import rostopic
import geometry_msgs.msg
import tf2_ros


class Listener:
    def __init__(self, topic):
        self.msg = None
        msg_type = rostopic.get_topic_class(topic)[0]
        self.sub = rospy.Subscriber(topic, msg_type, self.set_msg)

    def set_msg(self, msg):
        self.msg = msg


def wait_for_message(topic):
    msg_type = rostopic.get_topic_class(topic)[0]
    return rospy.wait_for_message(topic, msg_type)


def pose_to_transform(pose):
    tf = geometry_msgs.msg.Transform()
    tf.translation.x = pose.position.x
    tf.translation.y = pose.position.y
    tf.translation.z = pose.position.z
    tf.rotation.w = pose.orientation.w
    tf.rotation.x = pose.orientation.x
    tf.rotation.y = pose.orientation.y
    tf.rotation.z = pose.orientation.z
    return tf


rospy.init_node('ambf_state_publisher')
ambf_static = {
    'psm1/baselink': wait_for_message('/ambf/env/psm1/baselink/State'),
    'psm2/baselink': wait_for_message('/ambf/env/psm2/baselink/State'),
}
ambf_moving = {
    'Needle': Listener('/ambf/env/Needle/State'),
    'CameraFrame': Listener('/ambf/env/CameraFrame/State'),
    'cameraL': Listener('/ambf/env/cameras/cameraL/State'),
    'cameraR': Listener('/ambf/env/cameras/cameraR/State'),
    'Entry1': Listener('/ambf/env/Entry1/State'),
    'Entry2': Listener('/ambf/env/Entry2/State'),
    'Entry3': Listener('/ambf/env/Entry3/State'),
    'Entry4': Listener('/ambf/env/Entry4/State'),
    'Exit1': Listener('/ambf/env/Exit1/State'),
    'Exit2': Listener('/ambf/env/Exit2/State'),
    'Exit3': Listener('/ambf/env/Exit3/State'),
    'Exit4': Listener('/ambf/env/Exit4/State'),
    'psm1/toolyawlink': Listener('/ambf/env/psm1/toolyawlink/State'),
    'psm2/toolyawlink': Listener('/ambf/env/psm2/toolyawlink/State'),
    'psm1/toolpitchlink': Listener('/ambf/env/psm1/toolpitchlink/State'),
    'psm2/toolpitchlink': Listener('/ambf/env/psm2/toolpitchlink/State'),
    'psm2/maininsertion2link': Listener('/ambf/env/psm2/maininsertion2link/State'),
    'psm1/maininsertionlink': Listener('/ambf/env/psm1/maininsertionlink/State'),
    # 'psm1/toolrolllink': Listener('/ambf/env/psm1/toolrolllink/State'),
    # 'psm2/toolrolllink': Listener('/ambf/env/psm2/toolrolllink/State'),

}

tf_static_broadcaster = tf2_ros.StaticTransformBroadcaster()
tf_broadcaster = tf2_ros.TransformBroadcaster()
transforms = []

for k, v in ambf_static.items():
    tf = geometry_msgs.msg.TransformStamped()
    tf.header.stamp = rospy.Time.now()
    tf.header.frame_id = 'world'
    tf.child_frame_id = k
    tf.transform = pose_to_transform(v.pose)
    transforms.append(tf)

tf_static_broadcaster.sendTransform(transforms)
rate = rospy.Rate(30)

while not rospy.is_shutdown():
    transforms = []

    for k, v in ambf_moving.items():
        if v.msg is None:
            continue

        tf = geometry_msgs.msg.TransformStamped()
        tf.header.stamp = rospy.Time.now()
        try:
            tf.header.frame_id = v.msg.parent_name.data.replace('BODY ', '')
        except AttributeError:
            tf.header.frame_id = 'world'
        tf.child_frame_id = k
        tf.transform = pose_to_transform(v.msg.pose)
        transforms.append(tf)

    tf_broadcaster.sendTransform(transforms)
    rate.sleep()