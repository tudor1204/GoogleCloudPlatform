#!/usr/bin/env python

from pathlib import Path
import pandas as pd
import numpy as np
import os
import datetime
import pickle
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score


class FraudDetectionModelTrainer:
    def __init__(
        self,
        train_dataset_path,
        test_dataset_path,
        label,
        checkpoint_path=None
    ):
        self._classes = [0, 1, 2, 3]        # 4 different fraud scenarios
        self._train_dataset_path = train_dataset_path
        self._test_dataset_path = test_dataset_path
        self._label = label
        if checkpoint_path:
            with open(checkpoint_path, 'rb') as f:
                self._model = pickle.load(f)
        else:
            self._model = SGDClassifier(warm_start=True)

    def get_model(self):
        return self._model

    def get_features_and_labels(self, dataframe):
        features = dataframe.drop(columns=self._label, axis=1)
        labels = dataframe[self._label]

        return features, labels

    def get_model_accuracy(self, features, labels):
        features_prediction = self._model.predict(features)
        accuracy = accuracy_score(features_prediction, labels)
        return accuracy

    def _read_dataset(self, dataset_path):
        dataset = pd.read_pickle(dataset_path)
        return dataset

    def _get_checkpoint_name(self):
        dataset_basename = Path(self._train_dataset_path).resolve().stem
        filename = "model_cpt_{}.pkl".format(dataset_basename)
        return filename

    def _save_model(self, checkpoint_dir):
        # Check whether the specified path exists or not
        isExist = os.path.exists(checkpoint_dir)

        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(checkpoint_dir)

        filename = self._get_checkpoint_name()
        path = checkpoint_dir + filename
        with open(path, 'wb') as f:
            pickle.dump(self._model, f)
        return path

    def train_and_save(self, checkpoint_dir):
        dataset = self._read_dataset(self._train_dataset_path)
        features, labels = self.get_features_and_labels(dataset)
        self._model.partial_fit(features, labels, classes=self._classes)
        checkpoint_path = self._save_model(checkpoint_dir)
        return checkpoint_path


    def generate_report(self, output_path):
        generated_on = str(datetime.datetime.now())
        checkpoint_name = self._get_checkpoint_name()
        dataset_name = Path(self._train_dataset_path).resolve().name
        train_features, train_labels = self.get_features_and_labels(
            self._read_dataset(self._train_dataset_path)
        )
        test_features, test_lables = self.get_features_and_labels(
            self._read_dataset(self._test_dataset_path)
        )
        training_accuracy = self.get_model_accuracy(
            train_features,
            train_labels
        )
        test_accuracy = self.get_model_accuracy(
            test_features,
            test_lables,
        )
        with open(output_path, 'a') as f:
            report = (
                "*****************************************************\n"
                "Report generated on: {}\n"
                "Training dataset: {}\n"
                "Model checkpoint: {}\n"
                "---\n"
                "Accuracy on training data: {}\n"
                "Accuracy on testing data: {}\n"
                "\n"
            ).format(
                generated_on,
                dataset_name,
                checkpoint_name,
                training_accuracy,
                test_accuracy,
            )
            f.writelines(report)










