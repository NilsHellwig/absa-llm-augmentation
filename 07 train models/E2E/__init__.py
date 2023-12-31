from E2E.preprocessing import get_preprocessed_data_E2E
from helper import format_seconds_to_time_string
from E2E.model import get_trainer_E2E
from transformers import AutoTokenizer
import subprocess
import numpy as np
import constants
import shutil
import time


def train_E2E_model(LLM_NAME, N_REAL, N_SYNTH, TARGET, LLM_SAMPLING, train_dataset, test_dataset, validation_dataset):
    results = {
        "LLM_NAME": LLM_NAME,
        "N_REAL": N_REAL,
        "N_SYNTH": N_SYNTH,
        "TARGET": TARGET,
        "LLM_SAMPLING": LLM_SAMPLING,
        "single_split_results": []
    }

    metrics_classwise_prefix = [
        "accuracy", "precision", "recall", "f1", "tp", "tn", "fp", "fn"]
    metrics_total_prefix = ["f1_micro", "f1_macro", "precision",
                            "recall", "accuracy", "f1", "tp", "tn", "fp", "fn"]
    metrics_total = {f"{metric}": [] for metric in metrics_total_prefix}
    metrics_total.update({f"{metric}_{ac}": []
                         for metric in metrics_classwise_prefix for ac in constants.POLARITIES})

    eval_loss = []
    n_samples_train = []
    n_samples_test = []
    n_samples_validation = []
    n_epochs_best_validation_score = []
    log_history = {}

    tokenizer = AutoTokenizer.from_pretrained(constants.MODEL_NAME_E2E)

    start_time = time.time()

    for cross_idx in range(constants.N_FOLDS):
        # Load Data
        train_data = train_dataset[cross_idx]
        test_data = test_dataset[cross_idx]
        valid_data = validation_dataset[cross_idx]

        train_data, test_data, valid_data = get_preprocessed_data_E2E(
            train_data, test_data, valid_data, tokenizer)
        

        n_samples_train.append(len(train_data))
        n_samples_test.append(len(test_data))
        n_samples_validation.append(len(valid_data))
        
        # in order to save the prediction and labels for each split, results will also be handed over
        trainer = get_trainer_E2E(train_data, valid_data, tokenizer, results, cross_idx)
        trainer.train()

        # Get index of best epoch on validation data / save log history
        n_epochs_best_validation_score.append(trainer.state.epoch - constants.N_EPOCHS_EARLY_STOPPING_PATIENCE)
        log_history[cross_idx] = trainer.state.log_history        

        # Save Evaluation of Test Data
        eval_metrics = trainer.evaluate(test_data)
        print(f"Split {cross_idx}:", eval_metrics)
    
        # Save Evaluation of Split
        results["single_split_results"].append(eval_metrics)

        for m in metrics_total_prefix:
            metrics_total[m].append(eval_metrics[f"eval_{m}"])

        for polarity in constants.POLARITIES:
            for classwise_metric in metrics_classwise_prefix:
                metrics_total[f"{classwise_metric}_{polarity}"].append(
                    eval_metrics[f"eval_{classwise_metric}_{polarity}"])
        
        eval_loss.append(eval_metrics["eval_loss"])

        # remove model output
        if TARGET == "aspect_category":
            prefix = constants.OUTPUT_DIR_ACD
        elif TARGET == "aspect_category_sentiment":
            prefix = constants.OUTPUT_DIR_ACSA
        elif TARGET == "end_2_end_absa":
            prefix = constants.OUTPUT_DIR_E2E
        elif TARGET == "target_aspect_sentiment_detection":
            prefix = constants.OUTPUT_DIR_TASD

        path_output = prefix + "_" + results["LLM_NAME"]+"_"+str(results["N_REAL"])+"_"+str(results["N_SYNTH"]) + "_"+results["TARGET"]+"_"+results["LLM_SAMPLING"]+"_"+str(cross_idx)
        shutil.rmtree(path_output)

        subprocess.call("rm -rf /home/mi/.local/share/Trash", shell=True)

    runtime = time.time() - start_time

    results.update({f"eval_{m}": np.mean(metrics_total[f"{m}"]) for m in metrics_total_prefix})
    results.update({f"eval_{m}_{polarity}": np.mean(metrics_total[f"{m}_{polarity}"]) for m in metrics_classwise_prefix for polarity in constants.POLARITIES})

    results["runtime"] = runtime
    results["runtime_formatted"] = format_seconds_to_time_string(runtime)
    results["eval_loss"] = np.mean(eval_loss)
    results["n_samples_train"] = n_samples_train
    results["n_samples_train_mean"] = np.mean(n_samples_train)
    results["n_samples_test"] = n_samples_test
    results["n_samples_test_mean"] = np.mean(n_samples_test)
    results["n_samples_validation"] = n_samples_validation
    results["n_samples_validation_mean"] = np.mean(n_samples_validation)
    results["n_epochs_best_validation_score"] = n_epochs_best_validation_score
    results["n_epochs_best_validation_score_mean"] = np.mean(n_epochs_best_validation_score)
    results["log_history"] = log_history
    
    return results