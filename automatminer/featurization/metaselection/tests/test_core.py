import unittest
from matminer.datasets import load_dataset
from automatminer.featurization.metaselection.core import _composition_metafeatures, \
    _structure_metafeatures, dataset_metafeatures, FeaturizerMetaSelector

__author__ = ["Qi Wang <wqthu11@gmail.com>"]


class TestDatasetMetaFeatures(unittest.TestCase):
    def setUp(self):
        self.test_df = load_dataset('elastic_tensor_2015').rename(
            columns={"formula": "composition"})

    def test_composition_metafeatures(self):
        mfs = _composition_metafeatures(self.test_df)
        mfs_values = mfs["composition_metafeatures"]
        self.assertEqual(mfs_values["number_of_compositions"], 1181)
        self.assertAlmostEqual(mfs_values["percent_of_all_metal"], 0.5919, 4)
        self.assertAlmostEqual(
            mfs_values["percent_of_metal_nonmetal"], 0.3810, 4)
        self.assertAlmostEqual(mfs_values["percent_of_all_nonmetal"], 0.0271, 4)
        self.assertAlmostEqual(
            mfs_values["percent_of_contain_trans_metal"], 0.8273, 4)
        self.assertEqual(mfs_values["number_of_different_elements"], 63)
        self.assertAlmostEqual(mfs_values["avg_number_of_elements"], 2.2007, 4)
        self.assertEqual(mfs_values["max_number_of_elements"], 4)
        self.assertEqual(mfs_values["min_number_of_elements"], 1)

    def test_structure_metafeatures(self):
        mfs = _structure_metafeatures(self.test_df)
        mfs_values = mfs["structure_metafeatures"]
        self.assertEqual(mfs_values["number_of_structures"], 1181)
        self.assertAlmostEqual(mfs_values["percent_of_ordered_structures"], 1.0)
        self.assertAlmostEqual(mfs_values["avg_number_of_sites"], 12.4259, 4)
        self.assertEqual(mfs_values["max_number_of_sites"], 152)
        self.assertEqual(
            mfs_values["number_of_different_elements_in_structures"], 63)

    def test_dataset_metafeatures(self):
        mfs = dataset_metafeatures(self.test_df)
        self.assertIn("composition_metafeatures", mfs.keys())
        self.assertIn("structure_metafeatures", mfs.keys())
        self.assertIsNotNone(mfs["composition_metafeatures"])
        self.assertIsNotNone(mfs["structure_metafeatures"])


class TestFeaturizerAutoFilter(unittest.TestCase):
    def setUp(self):
        self.test_df = load_dataset('elastic_tensor_2015').rename(
            columns={"formula": "composition"})

    def test_auto_excludes(self):
        ftz_excludes = FeaturizerMetaSelector(max_na_frac=0.05).\
            auto_excludes(self.test_df)
        self.assertIn("IonProperty", ftz_excludes)
        self.assertIn("OxidationStates", ftz_excludes)
        self.assertIn("ElectronAffinity", ftz_excludes)
        self.assertIn("ElectronegativityDiff", ftz_excludes)
        self.assertIn("TMetalFraction", ftz_excludes)
        self.assertIn("YangSolidSolution", ftz_excludes)
        self.assertIn("CationProperty", ftz_excludes)
        self.assertIn("Miedema", ftz_excludes)

        ftz_excludes = \
            FeaturizerMetaSelector(max_na_frac=0.40).\
                auto_excludes(self.test_df)
        self.assertIn("IonProperty", ftz_excludes)
        self.assertIn("ElectronAffinity", ftz_excludes)
        self.assertIn("ElectronegativityDiff", ftz_excludes)
        self.assertIn("OxidationStates", ftz_excludes)
        self.assertIn("CationProperty", ftz_excludes)


if __name__ == "__main__":
    unittest.main()
