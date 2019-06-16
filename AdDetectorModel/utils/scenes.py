import pickle
from os.path import exists, join

from AdDetectorUtils.paths import get_dir, get_video_path

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector, ThresholdDetector


class SceneDetectionManager:
    def __init__(self, detector_type='content', threshold=None, save_scenes=False, min_scene_len=25*5):
        assert detector_type in ['content', 'threshold']
        if threshold is None:
            # default values from documentaion PySceneDetect
            threshold = 20 if detector_type == 'content' else 12
        self.detector_type = detector_type
        self.threshold = threshold
        self.save_scenes = save_scenes
        self.min_scene_len = min_scene_len
        self.cache = {}

    def _create_detector(self):
        if self.detector_type == 'content':
            return ContentDetector(threshold=self.threshold, min_scene_len=self.min_scene_len)
        else:
            return ThresholdDetector(threshold=self.threshold, min_scene_len=self.min_scene_len)

    def _get_scenes_path(self, video_id):
        filename = '{}_{}_{}_len{}.scenes'.format(video_id, self.detector_type, self.threshold, self.min_scene_len)
        return join(get_dir(video_id), filename)

    def _get_stats_path(self, video_id):
        return join(get_dir(video_id), video_id + '_' + self.detector_type + '.stats.csv')

    def detect_scenes(self, video_id):
        if video_id in self.cache:
            return self.cache[video_id]
        scenes_file_path = self._get_scenes_path(video_id)
        if exists(scenes_file_path):
            print('loading scenes from ', scenes_file_path)
            with open(scenes_file_path, 'rb') as f:
                scenes = pickle.load(f)
            self.cache[video_id] = scenes
            return scenes

        print('Detecting scenes for {}'.format(video_id))

        stats_file_path = self._get_stats_path(video_id)

        video_manager = VideoManager([get_video_path(video_id)])
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        scene_manager.add_detector(self._create_detector())
        base_timecode = video_manager.get_base_timecode()

        try:
            if exists(stats_file_path):
                with open(stats_file_path, 'r') as stats_file:
                    stats_manager.load_from_csv(stats_file, base_timecode)

            # Set downscale factor to improve processing speed (no args means default).
            video_manager.set_downscale_factor()

            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            scenes_list = scene_manager.get_scene_list(base_timecode)
            scenes = [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scenes_list]
            self.cache[video_id] = scenes
            if self.save_scenes:
                scenes_file_path = self._get_scenes_path(video_id)
                print('saving scenes to ', scenes_file_path)
                with open(scenes_file_path, 'wb') as f:
                    pickle.dump(scenes, f)

            # We only write to the stats file if a save is required:
            if stats_manager.is_save_required():
                with open(stats_file_path, 'w') as stats_file:
                    stats_manager.save_to_csv(stats_file, base_timecode)

            return self.cache[video_id]
        finally:
            video_manager.release()
