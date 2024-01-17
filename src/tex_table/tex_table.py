import re
from warnings import warn
from numpy import array, empty_like
from numpy.typing import ArrayLike
from pandas import DataFrame, Series

class TexTable:
    def __init__(self, table: ArrayLike, row_index: ArrayLike|None = None, col_index: ArrayLike|None = None, options: dict|None = None):
        
        # try to move table to a numpy array
        try:
            self.table = array(table)
        except:
            raise ValueError(f"'table' must be array-like. Instead got: {type(table)}.")
        
        # set options to defaults
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
            'round': -1,
            'make_ints': True,
            'tab_indent': 4,
            'sig_char': '*'
        }
        
        # validate table dimensions once we have a numpy array
        self.__validate_table()
        
        # update row index and column index and validate
        self.__set_row_index(table, row_index)
        self.__set_col_index(table, col_index)
        
        # regex for validating measurements
        mr = r"^\d*\.?\d+(pt|mm|cm|in|ex|em|mu|sp|\baselineskip|\\columnsep|\\columnwidth|\\evensidemargin|\\linewidth|"
        mr += r"\\oddsidemargin|\\paperheight|\\paperwidth|\\parindent|\\parskip|\\tabcolsep|\\textheight|\\textwidth|\\topmargin)$"
        self.MR = re.compile(mr)
        
        self.sig = [['' for _ in range(len(self.table[0]))] for _ in range(len(self.table))]
        
        # update options if provided
        if options is not None:
            for key in options:
                self.set_option(key, options[key])
                        
        self.__validate()

    """Internal method for rounding."""
    def __round(self, obj):
        if self.options['round'] >= 0: # if we should round
            try: # if np array
                obj = obj.round(self.options['round'])
            except: # if not np array
                try: # try to round by casting to float
                    obj = str(round(float(obj), self.options['round']))
                    if self.options['make_ints'] and obj.endswith('.0'):
                        obj = str(int(obj[:-2]))
                except:
                    pass
        return obj
    
    """Internal method for setting the row index of the table."""
    def __set_row_index(self, table: ArrayLike, row_index: ArrayLike|None = None):
        # set row index using explicit user input > pandas > automatic if possible
        if row_index is not None:
            try:
                self.row_index = array(row_index)
            except:
                raise ValueError(f"'row_index' must be array-like. Instead got: {type(row_index)}.")
        elif isinstance(table, DataFrame) or isinstance(table, Series):
            self.row_index = array(table.index) # guaranteed
        else:
            r = range(self.options['row_index_start'], self.table.shape[0] + self.options['row_index_start'])
            self.row_index = array(r) # guaranteed by validate_table
    
    """Internal method for setting the column index of the table."""
    def __set_col_index(self, table: ArrayLike, col_index: ArrayLike|None = None):
        # set col index using explicit user input > pandas > automatic if possible
        if col_index is not None:
            try:
                self.col_index = array(col_index)
            except:
                raise ValueError(f"'col_index' must be array-like. Instead got: {type(col_index)}.")
        elif isinstance(table, DataFrame):
            self.col_index = array(table.columns) # guaranteed
        else:
            r = range(self.options['col_index_start'], self.table.shape[1] + self.options['col_index_start'])
            self.col_index = array(r) # guaranteed by validate_table
    
    """Internal method for validating table and indices."""
    def __validate_table(self):
        # ensure either 1 or 2 dimensions, and use underlying 2d array
        if self.table.ndim == 1:
            self.table = self.table.reshape(1, -1)
        elif self.table.ndim == 2:
            pass
        else:
            raise ValueError(f"'table' must have either 1 or 2 dimensions. Instead got: {self.table.ndim}.")
    
    """Internal method for validating shape of indices."""
    def __validate_indices(self):
        # ensure either 1 or 2 dimensions, and use underlying 2d array
        if self.row_index.ndim > 1 and self.options['row_index']:
            self.row_index = self.row_index.squeeze()
            if self.row_index.ndim > 1:
                raise ValueError(f"'row_index' should be flat(tenable). Instead got: {self.table.ndim} dimensions.")
        if self.col_index.ndim > 1 and self.options['col_index']:
            self.col_index = self.col_index.squeeze()
            if self.col_index.ndim > 1:
                raise ValueError(f"'col_index' should be flat(tenable). Instead got: {self.table.ndim} dimensions.")
    
    """Internal method for validating entire object."""
    def __validate(self):
        
        # ensure table and indices are valid
        self.__validate_table()
        self.__validate_indices()
        
        # ensure everything is a string
        try:
            self.table = self.table.astype(str)
        except:
            raise ValueError("'table' should not contain lists or other types not interpretable as strings.")
        self.row_index = self.row_index.astype(str)
        self.col_index = self.col_index.astype(str)
        
        # validate align
        align = self.options['align']
        if align not in ('c', 'l', 'r', 'p', 'm', 'b'): # center, left, right, paragraph, math
            warn(f"'align' must be one of: 'c', 'l', 'r', 'p', 'm', 'b'. Instead got: {align}.")
        
        # validate measure
        measure = self.options['measure']
        if align == 'p' or align == 'm' or align == 'b': # paragraph or math - need measurement
            if not re.match(self.MR, measure):
                warn(f"'measure' must be specified when 'align' is 'p', 'm', or 'b'. Valid examples: '1cm', '2in', '3pt'.")
            
        # validate hline
        hline = self.options['hline']
        if hline not in ('all', 'header', 'none'):
            raise ValueError(f"'hline' must be one of: 'all', 'header', 'none'. Instead got: {hline}.")
        
        # validate vline
        vline = self.options['vline']
        if vline not in ('all', 'index', 'none'):
            raise ValueError(f"'vline' must be one of: 'all', 'index', 'none'. Instead got: {vline}.")
        
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
                raise ValueError(msg + f" Instead got: {box}.")
                
        # validate row index
        if self.options['row_index']:
            if len(self.row_index) != self.table.shape[0]:
                raise ValueError(f"Length of 'row_index' must match number of rows in 'table'. Instead got: {len(self.row_index)}.")
            if self.options['bold_row_index'] not in (True, False):
                raise ValueError(f"'bold_row_index' must be True or False. Instead got: {self.options['bold_row_index']}.")
            if type(self.options['row_index_start']) != int:
                try:
                    self.options['row_index_start'] = int(self.options['row_index_start'])
                except:
                    raise ValueError(f"'row_index_start' must be an integer. Instead got: {type(self.options['row_index_start'])}.")
            
        # validate column index
        if self.options['col_index']:
            if len(self.col_index) != self.table.shape[1]:
                raise ValueError(f"Length of 'col_index' must match number of columns in 'table'. Instead got: {len(self.col_index)}.")
            if self.options['bold_col_index'] not in (True, False):
                raise ValueError(f"'bold_col_index' must be True or False. Instead got: {self.options['bold_col_index']}.")
            if type(self.options['col_index_start']) != int:
                try:
                    self.options['col_index_start'] = int(self.options['col_index_start'])
                except:
                    raise ValueError(f"'col_index_start' must be an integer. Instead got: {type(self.options['col_index_start'])}.")
            
        # validate round and make_ints
        if type(self.options['round']) != int:
            try:
                self.options['round'] = int(self.options['round'])
            except:
                raise ValueError(f"'round' must be an integer. Instead got: {type(self.options['round'])}.")
            if self.options['make_ints'] not in (True, False):
                raise ValueError(f"'make_ints' must be True or False. Instead got: {self.options['make_ints']}.")
            
        # validate tab_indent
        if type(self.options['tab_indent']) != int:
            try:
                self.options['tab_indent'] = int(self.options['tab_indent'])
            except:
                raise ValueError(f"'tab_indent' must be an integer. Instead got: {type(self.options['tab_indent'])}.")

        # validate sig_char
        if type(self.options['sig_char']) != str:
            raise ValueError(f"'sig_char' must be a string. Instead got: {type(self.options['sig_char'])}.")
        if len(self.options['sig_char']) != 1:
            warn(f"'sig_char' should be a single character. Instead got: {len(self.options['sig_char'])} characters.")
    
    def __str__(self):
        
        self.__validate()
        
        s = '\nTable:\n\n\\begin{tabular}{'
        
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
            s += ' & '.join([self.__round(self.table[i, j]) + self.sig[i][j] for j in range(len(self.table[i]))]) + ' \\\\\n'
            if self.options['hline'] == 'all':
                s += ' ' * self.options['tab_indent'] + '\\hline\n'
                
        # add hline if bottom
        if 'b' in self.options['box'] or self.options['box'] == 'all':
            if not s.endswith('\\hline\n'): # if not already added
                s += ' ' * self.options['tab_indent'] + '\\hline\n'
        
        # close tabular
        s += '\\end{tabular}\n'
        
        # escape underscores
        
        s = s.replace('_', '\\_')
        
        return s
                
    def T(self):
        self.table = self.table.T
        self.row_index, self.col_index = self.col_index, self.row_index
        self.options['row_index'], self.options['col_index'] = self.options['col_index'], self.options['row_index']
        self.options['bold_row_index'], self.options['bold_col_index'] = self.options['bold_col_index'], self.options['bold_row_index']
        self.__validate()
        return self
    
    """Same as T()."""
    def transpose(self):
        return self.T()
    
    """Set a single option."""
    def set_option(self, option: str, value: str):
        if option in self.options:
            self.options[option] = value
            self.__validate()
        else:
            warn(f"Option '{option}' is not valid. Ignoring.")
    
    """Set multiple options at once."""
    def set_options(self, options: dict):
        for key in options:
            if key in self.options:
                self.options[key] = options[key]
            else:
                warn(f"Option '{key}' is not valid. Ignoring.")
        self.__validate()
    
    """Write table to file."""
    def write(self, file: str):
        
        self.__validate()
        
        with open(file, 'w+') as f:
            f.write(str(self))
    
    """Display currently set options."""
    def print_options(self):
        s = '\nOptions:\n\n'
        
        for key in self.options:
            s += f"{key}: {self.options[key]}\n"
            
        print(s)
        
        return s

    """Interpret p-values as significant or not. Use reset=True to erase previous interpretation."""
    def interpret_p(self, reset: bool = False, thresholds: tuple|list = (0.05, 0.01, 0.001)):
        for i in range(self.table.shape[0]):
            for j in range(self.table.shape[1]):
                try:
                    self.sig[i][j] = '' # reset significance
                    if not reset: # if not just resetting interpretation
                        f = float(self.table[i, j]) # get float representation
                        for t in thresholds:
                            if f < t:
                                self.sig[i][j] += self.options['sig_char']
                except: # ignore non-numeric entries
                    pass
    
    """Convenience method for piping operations together."""
    def pipe(self,
             file: str,
             transpose: bool = False,
             options: dict|None = None,
             interpret_p: bool = False,
             reset: bool = False,
             thresholds: tuple|list = (0.05, 0.01, 0.001)):
        if transpose:
            self.T()
        if options is not None:
            self.set_options(options)
        if interpret_p:
            self.interpret_p(reset, thresholds)
        print(self)
        self.write(file)
        return self