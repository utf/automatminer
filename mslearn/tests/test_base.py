"""
Tests for the base classes.
"""
import unittest
import logging

import pandas as pd
from sklearn.exceptions import NotFittedError

from mslearn.base import DataframeTransformer, AutoMLAdaptor, LoggableMixin
from mslearn.utils.package_tools import check_fitted, set_fitted


class TestTransformerGood(DataframeTransformer):
    """
    A test transformer and logger.

    Args:
        config_attr: Some attr to be set at initialization
    """

    def __init__(self, config_attr):
        self.config_attr = config_attr
        self.target = None
        self.is_fit = False

    @set_fitted
    def fit(self, df, target):
        """
        Determine the target of the dataframe.

        Args:
            df (pandas.DataFrame): The dataframe to be transformed.
            target (str): The fit target

        Returns:
            TestTransformer
        """
        if target in df.columns:
            self.target = target
        else:
            raise ValueError("Target {} not in dataframe.".format(target))
        return self

    @check_fitted
    def transform(self, df, target):
        """
        Drop the target set during fitting.

        Args:
            df (pandas.DataFrame): The dataframe to be transformed.
            target (str): The transform target (not the same as fit target
                necessarily)

        Returns:
            df (pandas.DataFrame): The transformed dataframe.
        """
        df = df.drop(columns=self.target)
        return df


class TestTransformerBad(DataframeTransformer):
    """
    A test transformer, implemented incorrectly.
    """
    def __init__(self):
        pass


class TestLoggableMixin(LoggableMixin):
    """
    A class for testing logging mixin classes.

    Args:
        logger (bool or logging.Logger): The logging object.
    """
    def __init__(self, logger=True):
        self._logger = self.get_logger(logger)


class TestAdaptorBad(AutoMLAdaptor):
    """
    A test adaptor for automl backends, implemented incorrectly.
    """
    def __init__(self):
        pass

class TestAdaptorGood(AutoMLAdaptor):
    """
    A test adaptor for automl backends, implemented correctly.
    """
    def __init__(self, config_attr):
        self.config_attr = config_attr
        self.target = None
        self.is_fit = False
        self._ml_data = None
        self._best_models = None
        self._backend = None
        self._features = None

    @set_fitted
    def fit(self, df, target):
        """
        Determine the target of the dataframe.

        Args:
            df (pandas.DataFrame): The dataframe to be transformed.
            target (str): The fit target

        Returns:
            TestTransformer
        """
        if target in df.columns:
            self.target = target
        else:
            raise ValueError("Target {} not in dataframe.".format(target))

        self._best_models = ["model1", "model2"]
        self._ml_data = {"y": df[target], "X": df.drop(columns=[target])}
        self._backend = "mybackend"
        self._features = self._ml_data["X"].columns.tolist()
        return self

    @check_fitted
    def predict(self, df, target):
        """
        Drop the target set during fitting.

        Args:
            df (pandas.DataFrame): The dataframe to be transformed.
            target (str): The transform target (not the same as fit target
                necessarily)

        Returns:
            df (pandas.DataFrame): The transformed dataframe.
        """
        df = df.drop(columns=self.target)
        return df


class TestMatPipe(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})

    def test_DataFrameTransformer(self):
        ttg = TestTransformerGood(5)
        self.assertTrue(hasattr(ttg, "config_attr"))
        self.assertTrue(ttg.config_attr, 5)
        with self.assertRaises(NotFittedError):
            ttg.transform(self.df, 'b')

        ttg.fit(self.df, 'a')
        self.assertTrue(ttg.config_attr, 5)

        test = ttg.transform(self.df, 'b')
        self.assertTrue("b" in test.columns)
        self.assertTrue("c" in test.columns)
        self.assertTrue("a" not in test.columns)

        test = ttg.fit_transform(self.df, 'c')
        self.assertTrue("c" not in test.columns)
        self.assertTrue("a" in test.columns)
        self.assertTrue("b" in test.columns)

        ttb = TestTransformerBad()
        with self.assertRaises(NotImplementedError):
            ttb.fit(self.df, 'a')

        with self.assertRaises(NotImplementedError):
            ttb.transform(self.df, 'b')

    def test_LoggableMixin(self):
        tlm = TestLoggableMixin(logger=True)
        self.assertTrue(hasattr(tlm, "logger"))
        self.assertTrue(isinstance(tlm.logger, logging.Logger))

    def test_AutoMLAdaptor(self):
        tag = TestAdaptorGood(config_attr=5)

        with self.assertRaises(NotFittedError):
            tag.transform(self.df, 'a')

        with self.assertRaises(NotFittedError):
            tag.predict(self.df, 'a')

        tag.fit(self.df, 'a')
        self.assertTrue(hasattr(tag, "features"))
        self.assertTrue(hasattr(tag, "ml_data"))
        self.assertTrue(hasattr(tag, "best_models"))
        self.assertTrue(hasattr(tag, "backend"))
        self.assertTrue(tag.is_fit)
        self.assertTrue(tag.ml_data["X"].shape[1] == 2)
        self.assertTrue(tag.best_models[0] == "model1")
        self.assertTrue(tag.backend == "mybackend")
        self.assertTrue(tag.features[0] == "b")

        predicted = tag.predict(self.df, 'b')
        self.assertTrue("b" in predicted)
        self.assertTrue("c" in predicted)
        self.assertTrue("a" not in predicted)

        predicted2 = tag.fit_transform(self.df, 'c')
        self.assertTrue("b" in predicted2)
        self.assertTrue("a" in predicted2)
        self.assertTrue("c" not in predicted2)

        tab = TestAdaptorBad()
        with self.assertRaises(NotImplementedError):
            tab.fit(self.df, 'a')

        with self.assertRaises(NotImplementedError):
            tab.predict(self.df, 'a')

        with self.assertRaises(NotImplementedError):
            tab.transform(self.df, 'a')

        for attr in ["backend", "best_models", "ml_data", "features"]:
            with self.assertRaises(NotImplementedError):
                thisatte = getattr(tab, attr)


