from matbench.automl.tpot_utils import TpotAutoml
from matbench.data.load import load_glass_formation
from matbench.featurize import Featurize
from matbench.preprocess import PreProcess
from sklearn.model_selection import train_test_split
from time import time

# user inputs
target_col = 'gfa'
RS = 29
timelimitmins = 120
model_type = 'classification'
scoring = 'f1'

# load and featurize:
df_init = load_glass_formation(phase='ternary')
featzer = Featurize(df_init, ignore_cols=['phase'], ignore_errors=True)

df_feats = featzer.featurize_formula(featurizers='all')

# preprocessing of the data
prep = PreProcess(max_colnull=0.1)
df = prep.preprocess(df_feats)
df.to_csv('{}_tpot_trained_data.csv'.format(target_col))
print(df.shape)
print(df.head())
assert df.isnull().sum().sum() == 0
# train/test split (development is within tpot crossvalidation)
X_train, X_test, y_train, y_test = \
    train_test_split(df.drop(target_col, axis=1).values,
                     df[target_col], train_size=0.75, test_size=0.25,
                     random_state=RS)

print('start timing...')
start_time = time()
tpot = TpotAutoml(mode=model_type,
                  max_time_mins=timelimitmins,
                  scoring=scoring,
                  random_state=RS,
                  feature_names=df.drop(target_col, axis=1).columns,
                  n_jobs=1)
tpot.fit(X_train, y_train)
print('total fitting time: {} s'.format(time() - start_time))

top_scores = tpot.get_top_models(return_scores=True)
print('top cv scores:')
print(top_scores)
print('top models')
print(tpot.top_models)
test_score = tpot.score(X_test, y_test)
print('the best test score:')
print(test_score)

