from matminer.featurizers.base import MultipleFeaturizer
import matminer.featurizers.composition as cf
import matminer.featurizers.structure as sf
from pymatgen import Composition
from matbench.data.load import load_double_perovskites_gap
from matbench.utils.utils import MatbenchError
from warnings import warn



class Featurize(object):
    """
    Takes in a dataframe and generate features from preset columns such as
    "formula", "structure", "bandstructure", "dos", etc.

    Args:
        df (pandas.DataFrame): the input data containing at least one of preset
            inputs (e.g. "formula")
        target_cols ([str]): target columns separated from training data
        ignore_cols ([str]): if set, these columns are excluded
    """
    def __init__(self, df, target_cols, ignore_cols=None):
        for t in target_cols:
            if t not in df:
                raise MatbenchError('target "{}" not in the data!'.format(t))
        self.target_df = df[target_cols]
        self.df = df.drop(target_cols+ignore_cols, axis=1)
        self.ignore_cols = ignore_cols


    def featurize_columns(self, input_cols=None):
        """
        Featurizes the dataframe based on input_columns.

        Args:
            input_cols ([str]): columns used for featurization (e.g. "structure"),
                set to None to try all preset columns.

        Returns (None):
            self.df gets updated w/ new features if the is featurizer available
        """
        input_cols = input_cols or ["formula"]
        for column in input_cols:
            featurizer = getattr(self, "featurize_{}".format(column), None)
            if featurizer is not None:
                featurizer()
            elif column not in self.df:
                raise MatbenchError('no "{}" in the data!')
            else:
                warn('No method available to featurize "{}"'.format(column))


    def featurize_formula(self, preset_name="matminer", compcol="composition"):
        if compcol not in self.df:
            self.df[compcol] = self.df["formula"].apply(Composition)
        featurizer = MultipleFeaturizer([
            cf.ElementProperty.from_preset(preset_name=preset_name),
            cf.IonProperty()
        ])

        self.df = featurizer.featurize_dataframe(self.df, col_id='composition')
        self.df = self.df.drop([compcol], axis=1)


    def featurize_structure(self, preset_name="ops"):
        featurizer = MultipleFeaturizer([
            sf.SiteStatsFingerprint(
                site_featurizer=sf.CrystalSiteFingerprint.from_preset(
                    preset=preset_name), stats=('mean', 'std_dev', 'minimum','maximum')
            ),
            sf.DensityFeatures(),
            sf.GlobalSymmetryFeatures()
        ])
        self.df = featurizer.featurize_dataframe(col_id="structure")


    def get_train_target(self):
        return self.df, self.target_df


if __name__ == "__main__":
    df_init, lumos = load_double_perovskites_gap(return_lumo=True)
    prep = Featurize(df_init,
                       target_cols=['gap gllbsc'],
                       ignore_cols=['A1', 'A2', 'B1', 'B2'])
    prep.featurize_columns()
    prep.handle_nulls()
    X, y = prep.get_train_target()
    print('here data')
    print(X.head())

    print('here targets')
    print(y.head())