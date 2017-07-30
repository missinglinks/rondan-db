
from kanaconv import KanaConv

def kanaToRomaji(st):
    conv = KanaConv()
    romanji = conv.to_romaji(st)
    return romanji