import os
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np
import argparse
from create_output_file import create_output
import pandas as pd

columns_names = ['chr','pos','ref','depth','A','C','G','T','N']

ap = argparse.ArgumentParser(description = 'Takes in the output of bam-readcount \
and returns a text file containing the count of each nucleotide at the position and the \
fraction of the reference nucleotide among all reads.')
requiredGrp = ap.add_argument_group('required arguments')
requiredGrp.add_argument("-i","--input", required=True, help="input file location")


args = vars(ap.parse_args())
input = args['input']


def proper_filter(read_metrics:list):
    """Takes in a list returns a dictionary with counts of each nucleotide
    """
    nucleotides = ['A','C','G','T','N']
    keep_track = {k:0 for k in nucleotides} #Initialize each nucleotide count with 0
    for indiv_metrics in read_metrics:
        if indiv_metrics[0] in nucleotides: 
            splitted_metrics = indiv_metrics.split(':')
            keep_track[splitted_metrics[0]] += int(splitted_metrics[1])
        elif indiv_metrics[0] not in nucleotides and indiv_metrics[0] != '=':
            splitted_metrics = indiv_metrics.split(':')
            keep_track['N'] += int(splitted_metrics[1])
    return keep_track
    
def do_math(df:'DataFrame',index:int):
    """Takes in dataframe and row index, returns that rows reference fraction
    """
    reference_nucleotide = df.loc[index,'ref']
    depth = df.loc[index,'depth']
    numerator = df.loc[index,reference_nucleotide]
    return int(numerator)/int(depth)
    
#argument = 'bamreadcount/E3.RIDb'.split('/')
input = input.split('/')
mypath = input[0]
file = input[1]
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print('File',file)
#KO file is always second
k = [mypath+'/'+i for i in onlyfiles if i.startswith(file)]
k = sorted(k, key=lambda x:('KO' in x, x))
lst = []
for i in k:
    list_of_rows = []
    with open(i) as FileObj:
        for lines in FileObj:
            initial_split = lines.split('\t')
            first_4_dict = dict(zip([1,2,3,4],initial_split[:4])) #First four columns into dict with random keynames
            nucleotide_count = proper_filter(initial_split[4:])
            first_4_dict.update(nucleotide_count)
            list_of_rows.append(pd.DataFrame([first_4_dict]))
    filtered_df = pd.concat(list_of_rows).reset_index(drop=True)
    filtered_df.columns = columns_names
    filtered_df = filtered_df[filtered_df['depth'] != '0'].reset_index(drop=True)
    filtered_df['ref_fraction'] = [do_math(filtered_df,i) for i in range(len(filtered_df))]
    lst.append(filtered_df)
    output = create_output(i,'filtered',file)
    without_sub = create_output(i,'filtered')
    filtered_df.to_csv(output,sep = '\t', index = False)

cols = ['chr', 'pos', 'ref', 'depth', 'A', 'C', 'G', 'T', 'N', 'ref_fraction',
       'chr.1', 'pos.1', 'ref.1', 'depth.1', 'A.1', 'C.1', 'G.1', 'T.1', 'N.1',
       'ref_fraction.1']
       
merged_df = pd.concat([lst[0],lst[1]],axis =1)
merged_df.columns = cols
merged_dir = 'merged/' 

os.makedirs(merged_dir, exist_ok = True)
output_dir = 'merged/' + file + '.merged.txt'
#merged_dir = without_sub.split('.')
#merged_dir.insert(-1,'merged')
#merged_dir = '.'.join(merged_dir)

merged_df.to_csv(output_dir,sep = '\t', index = False)








