"""
Base classes, mixins, and other inheritables.
"""

import logging
from matbench.utils.utils import initialize_logger, initialize_null_logger

__authors__ = ["Alex Dunn <ardunn@lbl.gov>", "Alex Ganose <aganose@lbl.gov>"]


class LoggableMixin(object):
    """A mixin class for easy logging (or absence of it)."""

    @property
    def logger(self):
        """Get the class logger.
        If the logger is None, the logging calls will be redirected to a dummy
        logger that has no output.
        """
        if hasattr(self, "_logger"):
            return self._logger
        else:
            raise AttributeError("Loggable object has no _logger attribute!")

    def get_logger(self, logger):
        """Set the class logger.
        Args:
            logger (Logger, bool): A custom logger object to use for logging.
                Alternatively, if set to True, the default matbench logger will
                be used. If set to False, then no logging will occur.
        """
        # need comparison to True and False to avoid overwriting Logger objects
        if logger is True:
            logger = logging.getLogger(self.__module__.split('.')[0])

            if not logger.handlers:
                initialize_logger()

        elif logger is False:
            logger = logging.getLogger(self.__module__.split('.')[0] + "_null")

            if not logger.handlers:
                initialize_null_logger()

        return logger


class DataframeTransformer:
    """
    A base class to allow easy transformation in the same way as
    TransformerMixin and BaseEstimator in sklearn.
    """
    def fit(self, df, target):
        """
        Fits the transformer to a dataframe, given a target.

        Args:
            df (pandas.DataFrame): The pandas dataframe to be fit.
            target (str): the target string specifying the ML target.

        Returns:
            (AutoMLAdaptor) This object (self)

        """
        raise NotImplementedError("{} has no fit method implemented!".format(self.__class__.__name__))

    def transform(self, df, target):
        """
        Transforms a dataframe.

        Args:
            df (pandas.DataFrame): The pandas dataframe to be fit.
            target (str): the target string specifying the ML target.

        Returns:
            (pandas.DataFrame): The transformed dataframe.

        """
        raise NotImplementedError("{} has no transform method implemented!".format(self.__class__.__name__))

    def fit_transform(self, df, target):
        """
        Combines the fitting and transformation of a dataframe.

        Args:
            df (pandas.DataFrame): The pandas dataframe to be fit.
            target (str): the target string specifying the ML target.

        Returns:
            (pandas.DataFrame): The transformed dataframe.

        """
        return self.fit(df, target).transform(df, target)


class AutoMLAdaptor(DataframeTransformer):
    """
    A base class to adapt from an AutoML backend to a sklearn-style fit/predict
    scheme and add a few extensions.
    """
    def transform(self, df, target):
        return self.predict(df, target)

    def predict(self, df, target):
        """
        Using a fitted object, use the best model available to transform a
        dataframe not containing the target to a dataframe containing the
        predicted target values.

        Analagous to DataframeTransformer.transform

        Args:
            df (pandas.DataFrame): The dataframe to-be-predicted
            target: The target metric to be predicted. The output column for
                the data will be "predicted {target}".

        Returns:
            (pandas.DataFrame): The dataframe updated with predictions of the
                target property.

        """
        raise NotImplementedError("{} has no predict method implemented!".format(self.__class__.__name__))

    @property
    def features(self):
        """
        The features being used for machine learning.

        Returns:
            ([str]): The feature labels
        """
        try:
            return self._features
        except AttributeError:
            raise NotImplementedError("{} has no features attr implemented!".format(self.__class__.__name__))

    @property
    def ml_data(self):
        """
        The raw ML-data being passed to the backend.

        Returns:
            (dict): At minimum, the raw X and y matrices being used for training.
                May also contain other data.
        """
        try:
            return self._ml_data
        except AttributeError:
            raise NotImplementedError("{} has no ML data attr implemented!".format(self.__class__.__name__))


    @property
    def best_models(self):
        """
        The best models returned by the AutoML backend.

        Returns:
            (list or OrderedDict}: The best models as determined by the AutoML package.
        """
        try:
            return self._best_models
        except AttributeError:
            raise NotImplementedError("{} has no best models attr implemented!".format(self.__class__.__name__))

    @property
    def backend(self):
        """
        The raw, fitted backend object, if it exists.

        Returns:
            Backend object (e.g., TPOTClassifier)

        """
        try:
            return self._backend
        except AttributeError:
            raise NotImplementedError("{} has no backend object attr implemented!".format(self.__class__.__name__))