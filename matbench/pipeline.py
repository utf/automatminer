import warnings
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import KFold, cross_val_score, cross_val_predict
from matbench.data.load import load_mp
from matminer.featurizers.base import MultipleFeaturizer
from matminer.featurizers.composition import ElementProperty
from matminer.featurizers.structure import BagofBonds, BondFractions, StructuralHeterogeneity, StructureComposition, ChemicalOrdering, MaximumPackingEfficiency, DensityFeatures, GlobalSymmetryFeatures
from matminer.figrecipes.plot import PlotlyFig
warnings.filterwarnings("ignore")
pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Try predict ehull from initial structure
n = 500
print("Reading csv for {} compounds...".format(n))
df = load_mp('mp_all10.csv').sample(n=n)
df['formula'] = [f.composition for f in df['structure']]

rf = RandomForestRegressor()
cv = KFold(n_splits=10, shuffle=True)

ep = ElementProperty.from_preset("matminer")
bb = BagofBonds()
bf = BondFractions(approx_bonds=True)
sh = StructuralHeterogeneity()
co = ChemicalOrdering()
de = DensityFeatures()

composition_featurizers = [ep]
structure_featurizers = [bb, bf, sh, co, de]

fls = []

for cf in composition_featurizers:
    print("Featurizing {}...".format(cf.__class__.__name__))
    cf.fit_featurize_dataframe(df, 'formula', ignore_errors=True)
    fls += cf.feature_labels()

for sf in structure_featurizers:
    print("Featurizing {}...".format(sf.__class__.__name__))
    sf.fit_featurize_dataframe(df, 'initial structure', ignore_errors=True)
    fls += sf.feature_labels()

dfo = df[fls + ['e_hull', 'formula']]
dfo = dfo.dropna(axis=1, thresh=0.25).dropna(axis=0)
remaining_labels = [f for f in fls if f in dfo.columns.values]
dfx = dfo[remaining_labels]
X = dfx.values
y = dfo['e_hull']

print("Produced {} samples of {} features.".format(X.shape[0], X.shape[1]))
print("Cross validating...")
scores = cross_val_score(rf, X, y, scoring='neg_mean_squared_error', cv=cv, n_jobs=8)
rmse_scores = [np.sqrt(abs(s)) for s in scores]
print('Folds: %i, mean RMSE: %.3f' % (len(scores), np.mean(np.abs(rmse_scores))))

print("Predicting and saving...")
ypred = cross_val_predict(rf, X, y, cv=cv, n_jobs=8)
res = pd.DataFrame({'actual': y, 'predicted': ypred})
res.to_csv('mlresults.csv')

pf_rf = PlotlyFig(x_title='DFT Energy Above Hull (eV)',
                  y_title='Random forest Energy Above Hull (eV)',
                  title='Random forest regression',
                  filename="rf_regression.html")

df['reduced_formula'] = [f.reduced_formula for f in df['formula']]
pf_rf.xy([(y, ypred), ([min(y), max(y)], [min(y), max(y)])],
         labels=df['reduced_formula'], modes=['markers', 'lines'],
         lines=[{}, {'color': 'black', 'dash': 'dash'}],
         showlegends=False)
