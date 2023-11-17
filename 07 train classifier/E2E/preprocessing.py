from torch.utils.data import Dataset as TorchDataset
import constants


def dataset_to_aspect_level_E2E(dataset):
    aspect_dataset = []
    for example in dataset:
        explicit_aspects = [tag for tag in example["tags"]
                            if tag["type"] == "label-explicit"]
        if len(explicit_aspects) > 0:
            aspect_dataset.append({
                "text": example["text"],
                "tags": explicit_aspects,
                "id": example["id"]
            })
    return aspect_dataset


def get_token_role_in_span_E2E(token_start: int, token_end: int, tag: dict):
    tag_start = tag["start"]
    tag_end = tag["end"]
    tag_polarity = tag["polarity"]

    if token_end <= token_start:
        return f"N_{tag_polarity}"
    if token_start < tag_start or token_end > tag_end:
        return f"O_{tag_polarity}"
    if token_start > tag_start:
        return f"I_{tag_polarity}"
    else:
        return f"B_{tag_polarity}"


def preprocess_example_E2E(example, tokenizer):
    input_text = example["text"]
    one_hot_output = [[0 for _ in constants.LABEL_TO_ID_E2E.keys()]
                      for _ in range(constants.MAX_TOKENS_E2E)]
    tokenized_input_text = tokenizer(input_text,
                                     return_offsets_mapping=True,
                                     padding="max_length",
                                     max_length=constants.MAX_TOKENS_E2E,
                                     truncation=True)

    for (token_start, token_end), token_labels in zip(tokenized_input_text["offset_mapping"], one_hot_output):
        for tag in example["tags"]:
            role = get_token_role_in_span_E2E(token_start, token_end, tag)

            for t in constants.LABEL_TO_ID_E2E:
                if role == t:
                    token_labels[constants.LABEL_TO_ID_E2E[t]] = 1


    return {
        "input_ids": tokenized_input_text["input_ids"],
        "attention_mask": tokenized_input_text["attention_mask"],
        "offset_mapping": tokenized_input_text["offset_mapping"],
        "labels": one_hot_output
    }


class CustomDatasetE2E(TorchDataset):
    def __init__(self, input_ids, attention_mask, offset_mapping, labels):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.offset_mapping = offset_mapping
        self.labels = labels

    def __getitem__(self, idx):
        item = {}
        item["input_ids"] = self.input_ids[idx]
        item["attention_mask"] = self.attention_mask[idx]
        item["offset_mapping"] = self.offset_mapping[idx]
        item["labels"] = self.labels[idx]
        return item

    def __len__(self):
        return len(self.labels)


def get_preprocessed_data_E2E(train_data, test_data, tokenizer):
    train_data = dataset_to_aspect_level_E2E(train_data)
    test_data = dataset_to_aspect_level_E2E(test_data)

    train_data = [preprocess_example_E2E(
        example, tokenizer) for example in train_data]
    test_data = [preprocess_example_E2E(
        example, tokenizer) for example in test_data]

    train_data = CustomDatasetE2E([example["input_ids"] for example in train_data],
                                  [example["attention_mask"]
                                      for example in train_data],
                                  [example["offset_mapping"]
                                      for example in train_data],
                                  [example["labels"] for example in train_data])
    test_data = CustomDatasetE2E([example["input_ids"] for example in test_data],
                                 [example["attention_mask"]
                                     for example in test_data],
                                 [example["offset_mapping"]
                                     for example in test_data],
                                 [example["labels"] for example in test_data])
    return train_data, test_data