import re
from warnings import warn
from numpy import array
from numpy.typing import ArrayLike
from pandas import DataFrame, Series

class TexTable:
    def __init__(self, data: ArrayLike, row_index: ArrayLike|None = None, col_index: ArrayLike|None = None, options: dict|None = None):
        
        # regex for measurement
        mr = r"^\d*\.?\d+(pt|mm|cm|in|ex|em|mu|sp|\baselineskip|\\columnsep|\\columnwidth|\\evensidemargin|\\linewidth|"
        mr += r"\\oddsidemargin|\\paperheight|\\paperwidth|\\parindent|\\parskip|\\tabcolsep|\\textheight|\\textwidth|\\topmargin)$"
        self.MR = re.compile(mr)
        
        # move data to a numpy array
        try:
            self.table = array(data)
        except:
            raise ValueError(f"'data' must be array-like. Instead got: {type(data)}.")
        
        # set row index using pandas if possible
        if row_index is not None:
            self.row_index = array(row_index)
        elif isinstance(data, DataFrame) or isinstance(data, Series):
            self.row_index = array(data.index)
        else:
            self.row_index = array(range(self.table.shape[0]))
            
        # set column index using pandas if possible
        if col_index is not None:
            self.col_index = array(col_index)
        elif isinstance(data, DataFrame) or isinstance(data, Series):
            self.col_index = array(data.columns)
        else:
            self.col_index = array(range(self.table.shape[1]))
            
        # set options
        self.options = {
            'align': 'c',
            'measure': '1cm',
            'hline': 'all',
            'vline': 'all',
            'box': 'all',
            'row_index': True,
            'bold_row_index': True,
            'row_index_start': 1,
            'col_index': True,
            'bold_col_index': True,
            'col_index_start': 1,
            'round': 2,
            'tab_indent': 4,
            'make_ints': True
        }
        if options is not None:
            for key in options:
                if key in self.options:
                    self.options[key] = options[key]
                else:
                    warn(f"Option '{key}' is not valid. Ignoring.")
        
        # try to round
        if self.options['round'] >= 0:
            try:
                self.table = self.table.round(self.options['round'])
            except:
                for i in range(self.table.shape[0]):
                    for j in range(self.table.shape[1]):
                        try:
                            self.table[i, j] = str(round(float(self.table[i, j]), self.options['round']))
                            if self.options['make_ints'] and self.table[i, j].endswith('.0'):
                                self.table[i, j] = str(int(self.table[i, j][:-2]))
                        except:
                            pass
                        
        # update row index and column index
        try:
            self.row_index += self.options['row_index_start']
        except:
            pass
        try:
            self.col_index += self.options['col_index_start']
        except:
            pass
                        
        self.validate()
        
    def validate(self):
        
        # ensure either 1 or 2 dimensions, and use underlying 2d array
        if self.table.ndim == 1:
            self.table = self.table.reshape(1, -1)
        elif self.table.ndim == 2:
            pass
        else:
            raise ValueError(f"'data' must have either 1 or 2 dimensions. Instead got: {self.table.ndim}.")
        
        # ensure everything is a string
        self.table = self.table.astype(str)
        self.row_index = self.row_index.astype(str)
        self.col_index = self.col_index.astype(str)
        
        # validate align
        align = self.options['align']
        if align not in ('c', 'l', 'r', 'p', 'm'): # center, left, right, paragraph, math
            warn(f"'align' must be one of: 'c', 'l', 'r', 'p', 'm'. Instead got: {align}.")
        
        # validate measure
        measure = self.options['measure']
        if align == 'p' or align == 'm': # paragraph or math - need measurement
            if not re.match(self.MR, measure):
                warn(f"'measure' must be specified when 'align' is 'p' or 'm'. Valid examples: '1cm', '2in', '3pt'.")
            
        # validate hline
        hline = self.options['hline']
        if hline not in ('all', 'header', 'none'):
            warn(f"'hline' must be one of: 'all', 'header', 'none'. Instead got: {hline}.")
        
        # validate vline
        vline = self.options['vline']
        if vline not in ('all', 'index', 'none'):
            warn(f"'vline' must be one of: 'all', 'index', 'none'. Instead got: {vline}.")
        
        # validate box
        box = self.options['box']
        if box not in ('all', 'none'):
            flag = False
            for side in ('t', 'b', 'l', 'r'):
                if side in box:
                    flag = True
                    break
            if not flag:
                msg = "'box' must be one of: 'all', 'none', or contain one or more of: 't', 'b', 'l', 'r'."
                warn(msg + f" Instead got: {box}.")
                
        # validate row index
        if self.options['row_index']:
            if len(self.row_index) != self.table.shape[0]:
                warn(f"Length of 'row_index' must match number of rows in 'data'. Instead got: {len(self.row_index)}.")
            
        # validate column index
        if self.options['col_index']:
            if len(self.col_index) != self.table.shape[1]:
                warn(f"Length of 'col_index' must match number of columns in 'data'. Instead got: {len(self.col_index)}.")
            
        # validate round
        if type(self.options['round']) != int:
            warn(f"'round' must be an integer. Instead got: {type(self.options['round'])}.")
        
    def __str__(self):
        
        self.validate()
        
        s = '\\begin{tabular}{'
        
        # left border
        if 'l' in self.options['box'] or self.options['box'] == 'all':
            s += '|'
            
        # construct column code TODO: vline index???
        col_code = self.options['align']
        if self.options['align'] == 'p' or self.options['align'] == 'm':
            col_code += '{' + self.options['measure'] + '}'
        if self.options['vline'] == 'all':
            col_code += '|'
        
        # make columns
        if self.options['row_index']: # add extra column for row index
            s += col_code
            if self.options['vline'] == 'index' or self.options['vline'] == 'all':
                s += '|'
        s += col_code * len(self.table[0])
        s = s.replace('||', '|') # remove extra if needed
        
        # right border
        if 'r' in self.options['box'] or self.options['box'] == 'all':
            s += '|'
            if s.endswith('||'): # remove extra if needed
                s = s[:-1]
        elif s.endswith('|'): # remove if accidentally added by vline process
                s = s[:-1]
        
        s += '}\n' # done with column codes
        
        # add hline if top
        if 't' in self.options['box'] or self.options['box'] == 'all':
            s += ' ' * self.options['tab_indent'] + '\\hline\n'
            
        # add col index
        if self.options['col_index']:
            s += ' ' * self.options['tab_indent']
            if self.options['row_index']: # placeholder entry for top left corner
                s += ' & '
            if self.options['bold_col_index']: # if bolding row index
                join_list = ['\\textbf{' + i + '}' for i in self.col_index]
            else:
                join_list = self.col_index
            s += ' & '.join(join_list) + ' \\\\\n'
            if self.options['hline'] == 'header' or self.options['hline'] == 'all':
                s += ' ' * self.options['tab_indent'] + '\\hline\n'
        
        # go through rows
        for i in range(len(self.table)):
            
            s += ' ' * self.options['tab_indent']
            
            # add row index if needed
            if self.options['row_index']:
                if self.options['bold_row_index']:
                    s += '\\textbf{' + self.row_index[i] + '} & '
                else:
                    s += self.row_index[i] + ' & '
                    
            # add row
            s += ' & '.join(self.table[i]) + ' \\\\\n'
            if self.options['hline'] == 'all':
                s += ' ' * self.options['tab_indent'] + '\\hline\n'
                
        # add hline if bottom
        if 'b' in self.options['box'] or self.options['box'] == 'all':
            if not s.endswith('\\hline\n'): # if not already added
                s += ' ' * self.options['tab_indent'] + '\\hline\n'
        
        # close tabular
        s += '\\end{tabular}'
        
        # escape underscores
        
        s = s.replace('_', '\\_')
        
        return s
                
    def T(self):
        self.table = self.table.T
        self.row_index, self.col_index = self.col_index, self.row_index
        self.options['row_index'], self.options['col_index'] = self.options['col_index'], self.options['row_index']
        self.options['bold_row_index'], self.options['bold_col_index'] = self.options['bold_col_index'], self.options['bold_row_index']
        self.validate()
        return self
    
    def transpose(self):
        return self.T()
    
    def set_option(self, option: str, value: str):
        self.options[option] = value
        self.validate()
        
    def set_options(self, options: dict):
        for key in options:
            self.options[key] = options[key]
        self.validate()
    
    def write(self, file: str):
        with open(file, 'w+') as f:
            f.write(str(self))