# TeX Table

## Description

This is a simple Python class that converts array-like objects such as Pandas DataFrames and Series, NumPy arrays, PyTorch tensors, and Python lists to $\LaTeX$ table representations.

## Setup

### Installation

To install the module, run the following command from the terminal:

```bash
pip install tex_table
```

### Importing

To import the class, use the following:

```python
from tex_table import TexTable
```

## Usage

### Creating a Table

To create a table, simply pass an array-like object to the `TexTable` constructor. For example, to create a table from a Pandas DataFrame, use the following:

```python
import pandas as pd
from tex_table import TexTable

df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

tt = TexTable(df)
```

You may also create a table from a NumPy array, PyTorch tensor, or Python list. For example:

```python
import numpy as np
from tex_table import TexTable

arr = np.array([[1, 2, 3], [4, 5, 6]])

tt = TexTable(arr)
```

```python
import torch
from tex_table import TexTable

t = torch.tensor([[1, 2, 3], [4, 5, 6]])

tt = TexTable(t)
```

```python
from tex_table import TexTable

l = [[1, 2, 3], [4, 5, 6]]

tt = TexTable(l)
```

### Printing a Table

To print a table, simply pass your `TexTable` object to the `print()` function. For example:

```python
print(tt)
```

You may use this functionality to preview what your table will look like before writing it to a file. You can copy the output from your terminal if you choose, though writing to a file may be the safer option. You can then tranpose the table or modify its options as needed.

### Modifying a Table's Content

The underlying representation of the table is simply a NumPy array of strings. The row and column indices are NumPy arrays of strings as well. To access them and manipulate them using NumPy:

```python
tt.table # the cells in the table
tt.row_index # the row index (labels on the left side of the table)
tt.col_index # the column index (labels on the top of the table)
```

### Transposing a Table

You can transpose a table (switch the rows with the columns and vice versa) as follows (both options do the same thing):

```python
tt.transpose()
```

```python
tt.T()
```

### Setting Options

You may set options for your table by passing a dictionary to the `options` parameter of the `TexTable` constructor. You may set options as follows:

```python
tt.set_option(option: str, value: str)
```

or

```python
tt.set_options(options: dict)
```

You can see all currently set options as follows:

```python
tt.print_options()
```

The following options are available:

- `'align'`: The alignment of the table cells. Default: `'c'`. Options: `'c'`, `'l'`, `'r'`, `'p'`, `'m'`, `'b'`.
- `'measure'`: The width to be used for alignments `'p'` and `'m'`. Default: `'1cm'`. Options include most common $\LaTeX$ length units.
- `'hline'`: Whether to draw horizontal lines between rows. Default: `'all'`. Options: `'all'`, `'header'`, `'none'`.
- `'vline'`: Whether to draw vertical lines between columns. Default: `'all'`. Options: `'all'`, `'index'`, `'none'`.
- `'box'`: Whether to draw a box around the table. Default: `'all'`. Options: `'all'`, `'tblr'`, `'none'`. `'t'` for top, `'b'` for bottom, `'l'` for left, and `'r'` for right. Note that `'tblr'` is equivalent to `'all'`. `'tb'` would give only the top and bottom, `'lr'` would give only the top and right, etc. All combinations are allowed.
- `'row_index'`: Whether to include the row index (labels at left of table). Default: `True`. If using a Pandas DataFrame, this will be the index of the DataFrame. Otherwise, a numerical index will be used.
- `'bold_row_index'`: Whether to bold the row index. Default: `True`.
- `'row_index_start'`: The starting index for the row index. Default: `1`. Used only if a numerical index is used.
- `'col_index'`: Whether to include the column index (labels at top of table). Default: `True`. If using a Pandas DataFrame, this will be the columns of the DataFrame. Otherwise, a numerical index will be used.
- `'bold_col_index'`: Whether to bold the column index. Default: `True`.
- `'col_index_start'`: The starting index for the column index. Default: `1`. Used only if a numerical index is used.
- `'round'`: The number of decimal places to round decimals to. Default: `-1`. If `-1`, no rounding will be done.
- `'make_ints'`: Whether to convert floats to integers if they are whole numbers. Default: `True`.
- `'tab_indent'`: The number of spaces to indent the table. Default: `4`.
- `'sig_char'`: The character to use for significant $p$-values. Default: `'*'`.

### Significance Stars

You may add significance stars (or another string of your choosing indicating significance) to your table as follows:

```python
tt.interpret_p(thresholds = (0.05, 0.01, 0.001)) # these are the defaults
```

When displaying the table, one star will be added for each threshold that the cell's value is less than or equal to. For the above example, if the $p$-value is less than or equal to 0.05, one star will be added. If the $p$-value is less than or equal to 0.01, two stars will be added. If the $p$-value is less than or equal to 0.001, three stars will be added. If the $p$-value is greater than 0.05, no stars will be added. You may change the character used for the stars by setting the `'sig_char'` option.

If you no longer wish to display the significance stars, you may remove them as follows:

```python
tt.interpret_p(reset = True)
```

Additionally, there is no need to reset before modifying the thresholds. You may simply call `interpret_p()` again with the new thresholds.

### Writing a Table to a File

To write a table to a file, use the `write()` method of your `TexTable` object. For example:

```python
tt.write('table.txt')
```

Note that writing a table can be done at any time, including after transposing the table or modifying the options. This allows you to experiment with the table's formatting as much as you need to ensure your output table is exactly as you want it.

### Pipelining Operations Together

You may run through all the above operations with a single method call. As a simple example:

```python
tt.pipe(
    transpose = True, # transpose the table - defaults to False
    options = {'align': 'c'}, # set the cell alignment to centered - by default, no options are modified
    interpret_p = True, # add significance stars - defaults to False
    reset = False, # reset the significance stars - defaults to False
    thresholds = (0.05, 0.01, 0.001), # set the significance thresholds - defaults to (0.05, 0.01, 0.001)
    print = True, # print the table to the terminal - defaults to True
    file = 'table.txt', # write the table to the file 'table.txt' - defaults to 'table.txt'
    write = True # write the table to the file - defaults to True
)
```

This method call will transpose the table, set the cell alignment to centered, add significance stars based on the thresholds given, print the table to the terminal, and write the table to the file `'table.txt'`. A file must be specified if `write=True`.

By default (i.e. `tt.pipe()`), this method will simply print the table and write it to `'table.txt'`.
