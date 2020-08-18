"""Tests using Scikit-Learn's bundled estimator_checks."""

from distutils.version import LooseVersion

import pytest

from sklearn import __version__ as sklearn_version
from sklearn.datasets import load_iris
from sklearn.utils.estimator_checks import check_no_attributes_set_in_init

from scikeras.wrappers import KerasClassifier
from scikeras.wrappers import KerasRegressor

from .mlp_models import dynamic_classifier
from .mlp_models import dynamic_regressor
from .testing_utils import basic_checks
from .testing_utils import parametrize_with_checks


@parametrize_with_checks(
    estimators=[
        KerasClassifier(
            build_fn=dynamic_classifier,
            # Set batch size to a large number
            # (larger than X.shape[0] is the goal)
            # if batch_size < X.shape[0], results will very
            # slightly if X is shuffled.
            # This is only required for this tests and is not really
            # applicable to real world datasets
            batch_size=1000,
            optimizer="adam",
        ),
        KerasRegressor(
            build_fn=dynamic_regressor,
            # Set batch size to a large number
            # (larger than X.shape[0] is the goal)
            # if batch_size < X.shape[0], results will very
            # slightly if X is shuffled.
            # This is only required for this tests and is not really
            # applicable to real world datasets
            batch_size=1000,
            optimizer="adam",
            loss=KerasRegressor.r_squared,
        ),
    ],
    ids=["KerasClassifier", "KerasRegressor"],
)
def test_fully_compliant_estimators(estimator, check):
    if sklearn_version <= LooseVersion("0.23.0") and check.func.__name__ in (
        "check_classifiers_predictions",
        "check_classifiers_classes",
        "check_methods_subset_invariance",
        "check_no_attributes_set_in_init",
    ):
        # These tests have bugs that are fixed in 0.23.0
        pytest.skip("This test is broken in sklearn<0.23.0")
    check(estimator)


class SubclassedClassifier(KerasClassifier):
    def __init__(
        self, hidden_layer_sizes=(100,),
    ):
        self.hidden_layer_sizes = hidden_layer_sizes

    def _keras_build_fn(self, hidden_layer_sizes):
        return dynamic_classifier(
            n_features_in_=self.n_features_in_,
            cls_type_=self.cls_type_,
            n_classes_=self.n_classes_,
            hidden_layer_sizes=hidden_layer_sizes,
        )


def test_no_attributes_set_init():
    """Tests that subclassed models can be made that
    set all parameters in a single __init__
    """
    estimator = SubclassedClassifier()
    check_no_attributes_set_in_init(estimator.__name__, estimator)
    basic_checks(estimator, load_iris)