import os.path
import pickle
from lxml import etree
import markdown as md
import anoi
from anoi import loaders, wordnet as wn
from anoi.facade import get_facade

if os.path.exists('space.pkl'):
    with open('space.pkl', 'rb') as pkl_fp:
        space = pickle.load(pkl_fp)
    facade = get_facade(space)
    wordnet_namespace = facade.namespace
else:
    facade = get_facade()
    space = facade.space
    wordnet_namespace = facade.namespace
    with open('space.pkl', 'wb') as pkl_fp:
        pickle.dump(space, pkl_fp)
