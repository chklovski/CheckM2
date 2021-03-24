from checkm2 import fileManager
from checkm2.defaultValues import DefaultValues
from checkm2 import sequenceClasses
from checkm2 import keggData

import subprocess
import os
import sys
from functools import reduce
import tempfile
import logging
import pandas as pd


'''Diamond only accepts single inputs, so we concat protein files and chunk them as input using tempfile'''

class DiamondRunner():

    def __init__(self, threads, output_directory, lowmem):
        self.threads = threads

        self.chunksize = DefaultValues.DIAMOND_DEFAULT_CHUNK_SIZE
        self.evalue = DefaultValues.DIAMOND_EVALUE
        self.query_cover = DefaultValues.DIAMOND_QUERY_COVER
        self.subject_cover = DefaultValues.DIAMOND_SUBJECT_COVER
        self.id = DefaultValues.DIAMOND_PERCENT_ID
        self.separator = DefaultValues.DIAMOND_HEADER_SEPARATOR
        if lowmem:
            self.blocksize = 0.5
        else:
            self.blocksize = 2

        self.check_for_diamond()
        self.diamond_out = os.path.join(output_directory, "diamond_output")
        fileManager.make_sure_path_exists(self.diamond_out)


    def check_for_diamond(self):
        """Check to see if Diamond is on the system before we try to run it."""

        # Assume that a successful diamond help returns 0 and anything
        # else returns something non-zero

        try:
            subprocess.call(['diamond', 'help'], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
        except:
            logging.error("Make sure diamond is on your system path.")
            sys.exit(1)

        #next, confirm database is present
        self.diamond_location = fileManager.DiamondDB().get_DB_location()
        fileManager.check_if_file_exists(self.diamond_location)


    def __concatenate_proteins(self, file_list):
        seq_list = []
        for faa in file_list:
            basename = os.path.splitext(os.path.basename(faa))[0]
            parsed_faa = sequenceClasses.SeqReader().read_nucleotide_sequences(faa)

            #append name to contig name using pre-defined separator to construct a new dict key
            parsed_faa = dict(("{}{}{}".format(basename, self.separator, k), v) for k, v in parsed_faa.items())
            seq_list.append(parsed_faa)

        return reduce(lambda a, b: {**a, **b}, seq_list)

    def __call_diamond(self, seq_object, diamond_output):
        with tempfile.NamedTemporaryFile() as temp_diamond_input:

            sequenceClasses.SeqReader().write_fasta(seq_object, temp_diamond_input.name)

            diamond_working_dir = tempfile.TemporaryDirectory()

            try:
                cmd = "diamond blastp --outfmt 6 --max-target-seqs 1 " \
                      "--query {} " \
                      "-o {} " \
                      "--threads {} " \
                      "--db {} " \
                      "--query-cover {} " \
                      "--subject-cover {} " \
                      "--id {} --block-size 0.5 " \
                      "--evalue {} --block-size {} "\
                      "--tmpdir {} --quiet "\
                    .format(temp_diamond_input.name,
                            diamond_output,
                            self.threads,
                            self.diamond_location,
                            DefaultValues.DIAMOND_QUERY_COVER,
                            DefaultValues.DIAMOND_SUBJECT_COVER,
                            DefaultValues.DIAMOND_PERCENT_ID,
                            DefaultValues.DIAMOND_EVALUE,
                            float(self.blocksize),
                            diamond_working_dir.name)

                logging.debug(cmd)
                subprocess.call(cmd, shell=True)
                logging.debug('Finished Running DIAMOND')
            except Exception as e:
                logging.error('An error occured while running DIAMOND: {}'.format(e))
                sys.exit(1)
            finally:
                diamond_working_dir.cleanup()
                temp_diamond_input.close()


    def run(self, protein_files):

        if len(protein_files) < self.chunksize:
            protein_chunks = self.__concatenate_proteins(protein_files)
        else:
            #break file list into chunks of size 'chunksize'
            chunk_list = [protein_files[i:i + self.chunksize] for i in range(0, len(protein_files), self.chunksize)]
            protein_chunks = [self.__concatenate_proteins(chunk) for chunk in chunk_list]

        logging.info('Annotating input genomes with DIAMOND using {} threads'.format(self.threads))

        #Check if we need to batch or not
        if isinstance(protein_chunks, list):
            for number, chunk in enumerate(protein_chunks):
                diamond_out = os.path.join(self.diamond_out, "DIAMOND_RESULTS_{}.tsv".format(number))
                self.__call_diamond(chunk, diamond_out)

        else:
            diamond_out = os.path.join(self.diamond_out, "DIAMOND_RESULTS.tsv")
            self.__call_diamond(protein_chunks, diamond_out)

        diamond_out_list = [x for x in os.listdir(self.diamond_out) if x.startswith('DIAMOND_RESULTS')]
        if len(diamond_out_list) == 0:
            logging.error("Error: DIAMOND failed to generate output.")
            sys.exit(1)
        else:
            return diamond_out_list



    def process_diamond_output(self, diamond_out_list):


        logging.info('Processing DIAMOND output')
        #concatenate all results even if only one
        results = pd.concat([pd.read_csv(os.path.join(self.diamond_out, entry), sep='\t', usecols=[0, 1], names=['header', 'annotation']) for entry in diamond_out_list])

        #Split columns into usable series
        results[['GenomeName', 'ProteinID']] = results['header'].str.split(self.separator, 1, expand=True)
        results[['Ref100_hit', 'Kegg_annotation']] = results['annotation'].str.split('~', 1, expand=True)


        ''' Get a list of default KO id's from data
            Available categories are the keys in DefaultValues.feature_ordering
            Here, returns an ordered set of KEGG ID's and sets to 0 
        '''
        KeggCalc = keggData.KeggCalculator()
        defaultKOs = KeggCalc.return_default_values_from_category('KO_Genes')

        #Remove from results any KOs we're not currently using
        results = results[results['Kegg_annotation'].isin(defaultKOs.keys())]


        #Update counts per genome
        kegg_genome_list = []
        for genome in results['GenomeName'].unique():
            diamond_KO_subset = results[results['GenomeName'] == genome]['Kegg_annotation'].value_counts()
            sub_dict = defaultKOs.copy()
            sub_dict['Name'] = genome
            sub_dict.update(diamond_KO_subset)
            kegg_genome_list.append(sub_dict)


        KO_genes = pd.DataFrame(kegg_genome_list)

        logging.info('Calculating completeness of pathways and modules.')
        logging.debug('Calculating pathway completeness information')
        KO_pathways = KeggCalc.calculate_KO_group('KO_Pathways', KO_genes.copy())

        logging.debug('Calculating category completeness information')
        KO_categories = KeggCalc.calculate_KO_group('KO_Categories', KO_genes.copy())

        logging.debug('Calculating module completeness information')
        KO_modules = KeggCalc.calculate_module_completeness(KO_genes.copy())

        diamond_complete_results = pd.concat([KO_genes, KO_pathways, KO_modules, KO_categories], axis=1)
        return diamond_complete_results, len(defaultKOs.keys())



















