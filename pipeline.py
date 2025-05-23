import argparse
from utils import read_video, save_video
from utils import read_video, save_video
from trackers import Tracker
import numpy as np
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_distance_estimator import SpeedDistanceEstimator

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    return parser.parse_args()

def run_pipeline(input_path: str, output_path: str):
    # Read Video
    video_frames = read_video(input_path)

    tracker = Tracker("models/best.pt")

    tracks = tracker.get_object_tracks(video_frames)

    # camera movement estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames)

    # View Transformer
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)

    # Interpolate ball positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

    # Speed and distance estimator
    speed_and_distance_estimator = SpeedDistanceEstimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    # Assign player teams
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks["players"][0])

    # loop over each player in each team
    for frame_num, player_track in enumerate(tracks["players"]):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(
                video_frames[frame_num], track["bbox"], player_id
            )
            tracks["players"][frame_num][player_id]["team"] = team
            tracks["players"][frame_num][player_id]["team_color"] = (
                team_assigner.team_colors[team]
            )

    # Assign Ball Aquisition
    player_assigner = PlayerBallAssigner()
    team_ball_control = []
    for frame_num, player_track in enumerate(tracks["players"]):
        ball_bbox = tracks["ball"][frame_num][1]["bbox"]
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)

        if assigned_player != -1:
            tracks["players"][frame_num][assigned_player]["has_ball"] = True
            team_ball_control.append(
                tracks["players"][frame_num][assigned_player]["team"]
            )
        # else:
        #     team_ball_control.append(team_ball_control[-1])
    team_ball_control = np.array(team_ball_control)

    # Draw object tracks
    output_video_frames = tracker.draw_annotations(
        video_frames, tracks, team_ball_control
    )

    # Draw camera movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(
        output_video_frames, camera_movement_per_frame
    )

    ## Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

    # Save Video
    save_video(output_video_frames, output_path)

if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.input, args.output)
