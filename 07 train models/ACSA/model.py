from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer, EarlyStoppingCallback
from transformers import DataCollatorWithPadding
from ACSA.evaluation import compute_metrics_ACSA
import constants
import torch


def create_model_ACSA():
    return AutoModelForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path=constants.MODEL_NAME_ACSA,
        num_labels=len(constants.ASPECT_CATEGORY_POLARITIES),
        problem_type="multi_label_classification"
    ).to(torch.device(constants.DEVICE))


def get_trainer_ACSA(train_data, validation_data, tokenizer, results, cross_idx):
    # Define Arguments
    training_args = TrainingArguments(
        output_dir=constants.OUTPUT_DIR_ACSA+"_" +
        results["LLM_NAME"]+"_"+str(results["N_REAL"])+"_"+str(results["N_SYNTH"]) +
        "_"+results["TARGET"]+"_"+results["LLM_SAMPLING"]+"_"+str(cross_idx),
        learning_rate=constants.LEARNING_RATE_ACSA,
        num_train_epochs=constants.EPOCHS_ACSA,
        per_device_train_batch_size=constants.BATCH_SIZE_ACSA,
        per_device_eval_batch_size=constants.BATCH_SIZE_ACSA,
        save_strategy="epoch" if constants.EVALUATE_AFTER_EPOCH == True else "no",
        logging_dir="logs",
        logging_steps=100,
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_micro",
        fp16=torch.cuda.is_available(),
        report_to="none",
        do_eval=True if constants.EVALUATE_AFTER_EPOCH == True else False,
        evaluation_strategy="epoch" if constants.EVALUATE_AFTER_EPOCH == True else "no",
        seed=constants.RANDOM_SEED,
    )

    compute_metrics_ACSA_fcn = compute_metrics_ACSA(results, cross_idx)

    trainer = Trainer(
        model_init=create_model_ACSA,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=validation_data,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        tokenizer=tokenizer,
        compute_metrics=compute_metrics_ACSA_fcn,
        callbacks=[EarlyStoppingCallback(
            early_stopping_patience=constants.N_EPOCHS_EARLY_STOPPING_PATIENCE)]
    )

    return trainer
