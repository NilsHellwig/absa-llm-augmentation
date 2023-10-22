from TASD.translate_sequence_to_tuples import preprocess_for_metrics
from TASD.evaluation import calculate_metrics_for_examples
from transformers import AutoTokenizer
from datasets import load_metric
import numpy as np
import constants


def compute_metrics(eval_pred):
    # Evtl später übertragen
    tokenizer = AutoTokenizer.from_pretrained(constants.MODEL_NAME_TASD)
    metric = load_metric("rouge")

    predictions, labels = eval_pred
    # Preprocess predictions
    decoded_preds, decoded_labels, pred_tuples, labels_tuples = preprocess_for_metrics(
        predictions, labels, tokenizer)

    # Text Based Metrics
    results = metric.compute(predictions=decoded_preds,
                             references=decoded_labels, use_stemmer=True)
    results = {key: value.mid.fmeasure * 100 for key, value in results.items()}
    prediction_lens = [np.count_nonzero(
        pred != tokenizer.pad_token_id) for pred in predictions]
    results["gen_len"] = np.mean(prediction_lens)
    results = {k: round(v, 4) for k, v in results.items()}

    # Calculate Total Metrics
    total_metrics = calculate_metrics_for_examples(labels_tuples, pred_tuples)

    for metric in ["f1", "recall", "precision", "accuracy"]:
        results[metric] = total_metrics[metric]

    # Calculate metrics for each aspect category
    for aspect_category in constants.ASPECT_CATEGORIES:
        pred_tuples_ac = [[tuple for tuple in example if tuple["aspect_category"]
                           == aspect_category] for example in pred_tuples]
        labels_tuples_ac = [[tuple for tuple in example if tuple["aspect_category"]
                             == aspect_category] for example in labels_tuples]
        ac_metrics = calculate_metrics_for_examples(
            labels_tuples_ac, pred_tuples_ac)
        for metric in ["f1", "recall", "precision", "accuracy"]:
            results[metric+"_"+aspect_category] = ac_metrics[metric]


def calculate_metrics_for_example(label, prediction):

    tp = 0
    tn = 0
    fp = 0
    fn = 0

    remove_from_prediction = []
    for item in prediction:
        if item in label:
            tp += 1
            label.remove(item)
            remove_from_prediction.append(item)
        else:
            fp += 1
            remove_from_prediction.append(item)

    for item in remove_from_prediction:
        prediction.remove(item)

    for item in label:
        if not (item in prediction):
            fn += 1

    return tp, tn, fp, fn


def calculate_metrics_for_examples(labels, predictions):
    tp_total = 0
    tn_total = 0
    fp_total = 0
    fn_total = 0

    labels = [[{key: tuple[key] for key in tuple if key in ['aspect_term',
                                                            'aspect_category', 'aspect_polarity']} for tuple in label] for label in labels]
    predictions = [[{key: tuple[key] for key in tuple if key in [
        'aspect_term', 'aspect_category', 'aspect_polarity']} for tuple in pred] for pred in predictions]

    for i in range(len(predictions)):
        tp, tn, fp, fn = calculate_metrics_for_example(
            labels[i], predictions[i])
        tn_total += tn
        tp_total += tp
        fp_total += fp
        fn_total += fn

    precision = tp_total / \
        (tp_total + fp_total) if (tp_total + fp_total) > 0 else 0
    recall = tp_total / \
        (tp_total + fn_total) if (tp_total + fn_total) > 0 else 0
    accuracy = (tp_total + tn_total) / \
        (tp_total + tn_total + fp_total + fn_total)

    f1 = 2 * (precision * recall) / (precision +
                                     recall) if (precision + recall) > 0 else 0

    return {"f1": f1, "recall": recall, "precision": precision, "accuracy": accuracy, "tp": tp_total, "tn": tn_total, "fp": fp_total, "fn": fn_total}