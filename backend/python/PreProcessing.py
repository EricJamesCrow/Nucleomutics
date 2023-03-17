from pathlib import Path
import subprocess
from . import BedtoolsCommands

def adjust_dyad_positions(dyad_file: Path, output_dir):
    """Takes a dyad file with single nucleotide positions and creates a new bed file with -500 and +500 positions

    Args:
        dyad_file (.bed): A dyad map that has the dyad (center) position of the nucleosome in a bed3 format
    """
    
    # Create the new filename
    intermediate_bed = output_dir / dyad_file.with_suffix('.tmp').name

    # Use a with statement to read and write to the files
    with open(dyad_file, 'r') as f, open(intermediate_bed, 'w') as o:
        
        # Loop through the lines in the input file and expand the positions by 500 on either side
        for line in f:
            tsv = line.strip().split()
            new_start = str(int(tsv[1]) - 1001)
            new_end = str(int(tsv[2]) + 1001)
            new_line_values = [tsv[0], new_start, new_end] + tsv[3:]
            o.write('\t'.join(new_line_values) + '\n')
    return intermediate_bed

def filter_lines_with_n(dyad_fasta: Path, dyad_bed: Path, output_dir):
    # Filter lines and write to new files
    filtered_fasta = output_dir / dyad_fasta.with_name(f'{dyad_fasta.stem}_filtered.fa').name
    filtered_bed = output_dir / dyad_bed.with_stem(f'{dyad_bed.stem}_filtered.bed').name
    # open all the files
    with open(dyad_fasta, 'r') as fa, open(dyad_bed, 'r') as bed, \
         open(filtered_fasta, 'w') as new_fa, \
         open(filtered_bed, 'w') as new_bed:
        for fa_line, bed_line in zip(fa, bed):
            if 'N' not in fa_line.upper():
                new_fa.write(fa_line)
                new_bed.write(bed_line)
    return filtered_bed, filtered_fasta

def check_and_sort(input_file: Path, output_dir: Path, suffix):
    sorted_name = output_dir / input_file.with_suffix(suffix).name
    command = f'sort -k1,1 -k2,2n -k3,3n -k6,6 {input_file} > {sorted_name}'
    with subprocess.Popen(args=command, stdout=subprocess.PIPE, shell=True) as p:
        return p, sorted_name
    
def filter_acceptable_chromosomes(input_file: Path, output_dir: Path, genome = 'human'):
    human = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X']
    filtered_name = output_dir / input_file.with_suffix('.tmp3').name
    if genome == 'human':
        with open(input_file, 'r') as f, open(filtered_name, 'w') as o:
            for line in f:
                chrom = line.strip().split('\t')[0][3:]
                if chrom in human:
                    o.write(line)
    return filtered_name

def vcf_snp_to_intermediate_bed(vcf_file: Path, output_dir):
    intermediate_bed = output_dir / vcf_file.with_suffix('.tmp').name
    with open(vcf_file) as f, open(intermediate_bed, 'w') as o:
        for line in f:
            if line[0] == '#': continue
            if 'CHROM' in line:
                header = line
                continue
            tsv = line.strip().split('\t')
            if not (len(tsv[3]) == 1 and len(tsv[4]) == 1 and tsv[3] in 'ACGT' and tsv[4] in 'ACGT'): continue
            chrom = tsv[0]
            base_0 = str(int(tsv[1])-2)
            base_1 = str(int(tsv[1])+1)
            name = '.'
            score = '0'
            strand = '+'
            mutation_type = f'{tsv[3]}>{tsv[4]}'
            new_line = '\t'.join([chrom, base_0, base_1, name, score, strand, mutation_type])
            o.write(new_line+'\n')
    return intermediate_bed

def expand_context_custom_bed(intermediate_bed: Path, fasta_file: Path, output_dir):
    bed_file = output_dir / intermediate_bed.with_suffix('.tmp2').name
    _, getfasta_output = BedtoolsCommands.bedtools_getfasta(intermediate_bed, fasta_file)
    with open(getfasta_output) as f, open(intermediate_bed) as i, open(bed_file, 'w') as o:
        for fasta_line, bed_line in zip(f, i):
            fasta_context = fasta_line.strip().split('\t')[-1]
            bed_info = bed_line.strip().split('\t')
            new_line = '\t'.join([bed_info[0], str(int(bed_info[1])+1), str(int(bed_info[2])-1), bed_info[3], bed_info[4], bed_info[5], fasta_context.upper(), bed_info[6]])
            o.write(new_line+'\n')
    return bed_file

