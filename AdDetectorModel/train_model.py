import json
from collections import defaultdict
from argparse import ArgumentParser

from sklearn.model_selection import StratifiedKFold

from AdDetectorModel.model import AdDetectorModel
from AdDetectorModel.utils.evaluation import evaluate


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--markups-file', type=str, help='path to file with markups')
    arg_parser.add_argument('--cv-splits', type=int, default=3, help='number of splits in CV')
    args = arg_parser.parse_args()
    if not args.markups_file:
        print('Please specify --markups-file')
        return
    with open(args.markups_file, 'r') as mf:
        markups = json.load(mf)
    video_ids = list(markups.keys())
    has_ads = [len(markups[video_id]) > 0 for video_id in video_ids]
    cv = StratifiedKFold(n_splits=args.cv_splits, shuffle=True, random_state=0)
    avg_metrics = defaultdict(lambda: 0)
    for train_idx, test_idx in cv.split(video_ids, has_ads):
        train_ids = [video_ids[idx] for idx in train_idx]
        test_ids = [video_ids[idx] for idx in test_idx]
        train_markups = {video_id: markups[video_id] for video_id in train_ids}
        test_markups = {video_id: markups[video_id] for video_id in test_ids}
        model = AdDetectorModel()
        model.train(train_markups)
        metrics = evaluate(model, test_markups)
        for metric, value in metrics.items():
            avg_metrics[metric] += value
    for metric in avg_metrics.keys():
        avg_metrics[metric] /= args.cv_splits
        print('{}: {}'.format(metric, avg_metrics[metric]))


if __name__ == "__main__":
    main()
