""" from https://github.com/keithito/tacotron """
import json
import re
# import pyopenjtalk
# from pypinyin import lazy_pinyin, BOPOMOFO
# import jieba
# import cn2an
from . import cleaners

_symbol_to_id = None
pattern = None
# jieba.initialize()
# pyopenjtalk._lazy_init()

# avaliabe_cleaners = [
#     "zh_ja_mixture_cleaners",
#     "japanese_cleaners2"
# ]

symbols_dict = {
    "zh_ja_mixture_cleaners":["_", ",", ".", "!", "?", "-", "~", "\u2026", "A", "E", "I", "N", "O", "Q", "U", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z", "\u0283", "\u02a7", "\u02a6", "\u026f", "\u0279", "\u0259", "\u0265", "\u207c", "\u02b0", "`", "\u2192", "\u2193", "\u2191", " "],
    "japanese_cleaners2":["_", ",", ".", "!", "?", "-", "~", "\u2026", "A", "E", "I", "N", "O", "Q", "U", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z", "\u0283", "\u02a7", "\u02a6", "\u2193", "\u2191", " "]
}


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 + 1)
    result[1::2] = lst
    return result


def build_pattern():
    brackets = ['（', '[', '『', '「', '【', ")", "】", "]", "』", "」", "）"]
    pattern = re.compile('|'.join(map(re.escape, brackets)))
    return pattern


def text_to_seq(text: str, hps):

    # if "japanese_cleaners" in hps.data.text_cleaners:
    # global pattern
    # if not pattern:
    pattern = build_pattern()
    text = pattern.sub(' ', text).strip()

    text_norm = text_to_sequence(
        text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = intersperse(text_norm, 0)
    return text_norm


def  text_to_seq_func(text: str, cleaner_names, symbols, add_blank=True):

    # if "japanese_cleaners" in hps.data.text_cleaners:
    # global pattern
    # if not pattern:
    pattern = build_pattern()
    if cleaner_names == "japanese_cleaners2":
        # 简单优化
        text = pattern.sub(' ', text).strip()

    clean_text, text_norm = text_to_sequence_func(
        text, symbols, cleaner_names=cleaner_names)
    if add_blank:
        text_norm = intersperse(text_norm, 0)
    return clean_text, text_norm


def text_to_sequence_func(text, symbols, cleaner_names):

    _symbol_to_id = {s: i for i, s in enumerate(symbols)}

    clean_text = _clean_text(text, cleaner_names)

    sequence = [
        _symbol_to_id[symbol] for symbol in clean_text if symbol in _symbol_to_id.keys()
    ]

    # for symbol in clean_text:
    #     if symbol not in _symbol_to_id.keys():
    #         continue
    #     symbol_id = _symbol_to_id[symbol]
    #     sequence += [symbol_id]
    return clean_text, sequence



def text_to_sequence(text, symbols, cleaner_names):
    '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
      Args:
        text: string to convert to a sequence
        symbols: list of symbols in the text
        cleaner_names: names of the cleaner functions to run the text through
      Returns:
        List of integers corresponding to the symbols in the text


        ATTENTION: unable to access Config variabel , don't know why
    '''

    # global _symbol_to_id

    # if not _symbol_to_id:
    _symbol_to_id = {s: i for i, s in enumerate(symbols)}

    clean_text = _clean_text(text, cleaner_names)

    sequence = [
        _symbol_to_id[symbol] for symbol in clean_text if symbol in _symbol_to_id.keys()
    ]

    # for symbol in clean_text:
    #     if symbol not in _symbol_to_id.keys():
    #         continue
    #     symbol_id = _symbol_to_id[symbol]
    #     sequence += [symbol_id]
    return sequence


def _clean_text(text, cleaner_names):
    for name in cleaner_names:
        cleaner = getattr(cleaners, name)
        if not cleaner:
            raise Exception('Unknown cleaner: %s' % name)
        text = cleaner(text)
    return text


class HParams():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if type(v) == dict:
                v = HParams(**v)
            self[k] = v

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()


def get_hparams_from_file(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        data = f.read()
    config = json.loads(data)

    hparams = HParams(**config)
    return hparams
