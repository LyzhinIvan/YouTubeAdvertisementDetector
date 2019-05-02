from os.path import exists, join

from AdDetectorUtils.paths import get_dir, get_video_path

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector


class SceneDetectionManager:
    def __init__(self):
        self.cache = {}

    def detect_scenes(self, video_id):
        if video_id in self.cache:
            return self.cache[video_id]

        stats_file_path = join(get_dir(video_id), video_id + '.stats.csv')

        video_manager = VideoManager([get_video_path(video_id)])
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        scene_manager.add_detector(ContentDetector())
        base_timecode = video_manager.get_base_timecode()

        try:
            if exists(stats_file_path):
                with open(stats_file_path, 'r') as stats_file:
                    stats_manager.load_from_csv(stats_file, base_timecode)

            # Set downscale factor to improve processing speed (no args means default).
            video_manager.set_downscale_factor()

            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            self.cache[video_id] = scene_manager.get_scene_list(base_timecode)

            # We only write to the stats file if a save is required:
            if stats_manager.is_save_required():
                with open(stats_file_path, 'w') as stats_file:
                    stats_manager.save_to_csv(stats_file, base_timecode)

            return self.cache[video_id]
        finally:
            video_manager.release()
