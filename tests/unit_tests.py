import numpy as np
import pandas as pd
import torch

import os
import sys
sys.path.append('..')
print(sys.path)
exit()

from src.tex_table.tex_table import TexTable

simple_data = [[1, 2, 3], [4, 5, 6]]

def test_list():
    table = TexTable(simple_data)
    assert str(table) == '\\begin{tabular}{ccc}\n\\hline\n1 & 2 & 3 \\\\\n4 & 5 & 6 \\\\\n\\hline\n\\end{tabular}\n'
    
if __name__ == '__main__':
    test_list()