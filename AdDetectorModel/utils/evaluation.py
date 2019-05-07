from AdDetectorUtils.types import *
from AdDetectorModel.model import AdDetectorModel


def evaluate(model: AdDetectorModel, test_markups: Markups) -> Dict[str, float]:
    predicted_markups = {}
    for idx, video_id in enumerate(test_markups):
        print('Predicting for video {} ({}/{})'.format(video_id, idx + 1, len(test_markups)))
        predicted_markups[video_id] = model.find_ads(video_id)
        print('{}: real {}, pred {}'.format(video_id, test_markups[video_id], predicted_markups[video_id]))
    eval_results = {
        'IoU': calc_IoU(test_markups, predicted_markups),
        'precision': calc_precision(test_markups, predicted_markups),
        'recall': calc_recall(test_markups, predicted_markups)
    }
    eval_results['f1'] = f_score(eval_results['precision'], eval_results['recall'])

    return eval_results


def calc_IoU(real_markups: Markups, predicted_markups: Markups) -> float:
    assert all(video_id in real_markups for video_id in predicted_markups)
    intersection = 0
    union = 0
    for video_id in predicted_markups:
        intersection += calc_intersection(real_markups[video_id], predicted_markups[video_id])
        union += calc_union(real_markups[video_id], predicted_markups[video_id])

    return 1 if union == 0 else intersection / union


def calc_intersection(real_ads: AdsList, predicted_ads: AdsList) -> float:
    inter = 0
    for real_ad in real_ads:
        for pred_ad in predicted_ads:
            inter += _calc_intersection_one(real_ad, pred_ad)
    return inter


def calc_union(real_ads: AdsList, predicted_ads: AdsList) -> float:
    union = 0
    for real_ad in real_ads:
        union += real_ad[1] - real_ad[0]
    for pred_ad in predicted_ads:
        union += pred_ad[1] - pred_ad[0]
    union -= calc_intersection(real_ads, predicted_ads)
    return union


def calc_precision(real_markups: Markups, predicted_markups: Markups) -> float:
    assert all(video_id in real_markups for video_id in predicted_markups)
    tp = 0
    fp = 0

    for video_id in predicted_markups:
        tp += calc_intersection(real_markups[video_id], predicted_markups[video_id])
        fp += calc_diff(predicted_markups[video_id], real_markups[video_id])

    return 0 if tp + fp == 0 else tp / (tp + fp)


def calc_recall(real_markups: Markups, predicted_markups: Markups) -> float:
    assert all(video_id in real_markups for video_id in predicted_markups)
    tp = 0
    fn = 0

    for video_id in predicted_markups:
        tp += calc_intersection(real_markups[video_id], predicted_markups[video_id])
        fn += calc_diff(real_markups[video_id], predicted_markups[video_id])

    return 0 if tp + fn == 0 else tp / (tp + fn)


def calc_diff(first_ads: AdsList, second_ads: AdsList):
    diff = 0
    for ad_one in first_ads:
        diff += ad_one[1] - ad_one[0]
        for ad_two in second_ads:
            diff -= _calc_intersection_one(ad_one, ad_two)
    return diff


def f_score(precision: float, recall: float, beta: float = 1) -> float:
    x = (1 + beta ** 2) * precision * recall
    y = (beta ** 2 * precision + recall)
    return 0 if y == 0 else x / y


def _calc_intersection_one(real_ad: Ad, pred_ad: Ad) -> float:
    max_l = max(real_ad[0], pred_ad[0])
    min_r = min(real_ad[1], pred_ad[1])
    return max(0, min_r - max_l)


def _calc_union_one(real_ad: Ad, pred_ad: Ad) -> float:
    len1 = real_ad[1] - real_ad[0]
    len2 = pred_ad[1] - pred_ad[0]
    return len1 + len2 - _calc_intersection_one(real_ad, pred_ad)
