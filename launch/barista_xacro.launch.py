import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Define paths
    pkg_share = FindPackageShare('barista_robot_description').find('barista_robot_description')
    xacro_file = os.path.join(pkg_share, 'xacro', 'barista_robot_model.urdf.xacro')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'barista.rviz')
    
    gazebo_models_path = os.path.join(pkg_share, 'meshes')
    install_dir = os.path.dirname(pkg_share)
    gazebo_model_path = os.path.join(pkg_share)
    set_gazebo_model_path = SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path)

    # Set GAZEBO_MODEL_PATH and GAZEBO_PLUGIN_PATH
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    # Print the paths to verify they are set correctly
    print("GAZEBO MODELS PATH: " + str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH: " + str(os.environ["GAZEBO_PLUGIN_PATH"]))

    # Declare arguments
    use_sim_time = DeclareLaunchArgument(
        name='use_sim_time', default_value='true', description='Use simulation clock'
    )
    
    include_laser = DeclareLaunchArgument(
        'include_laser', default_value='true',
        description='Include laser scanner'
    )



    robot_description_content = Command(
        [FindExecutable(name='xacro'), ' ',
         xacro_file, ' ',
         ]
    )



    # Robot State Publisher Node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content, 'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # Joint State Publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
    )

    # RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # Gazebo launch file (launches Gazebo)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            FindPackageShare('gazebo_ros').find('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items()
    )

    # Spawn Robot Node
    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description', '-entity', 'barista_robot'],
        output='screen'
    )

    return LaunchDescription([
        set_gazebo_model_path,
        use_sim_time,
        include_laser,
        robot_state_publisher,
        joint_state_publisher,
        rviz_node,
        gazebo_launch,
        spawn_robot_node
    ])


