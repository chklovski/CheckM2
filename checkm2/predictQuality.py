from checkm2 import metadata
from checkm2 import prodigal
from checkm2 import diamond
from checkm2.defaultValues import DefaultValues
from checkm2.versionControl import VersionControl
from checkm2 import keggData
from checkm2 import modelProcessing
from checkm2 import modelPostprocessing
from checkm2 import fileManager

import os
import multiprocessing as mp
import numpy as np
import shutil
import sys
import logging
import pandas as pd

# For unnessesary tensorflow warnings:
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)



class Predictor():
    def __init__(self, bin_folder, outdir, bin_extension='.fna', threads=1, overwrite=False, lowmem=False):

        self.bin_folder = bin_folder
        self.bin_extension = bin_extension
        self.bin_files = self.__setup_bins()
        fileManager.check_empty_dir(outdir, overwrite)
        self.output_folder = outdir
        self.prodigal_folder = os.path.join(self.output_folder, DefaultValues.PRODIGAL_FOLDER_NAME)
        fileManager.make_sure_path_exists(self.prodigal_folder)
        
        self.lowmem = lowmem
        if self.lowmem:
          logging.info('Running in low-memory mode.')


        self.total_threads = threads

        logging.debug('Verifying internal checksums for all models, scalers and reference data.')
        if VersionControl().checksum_version_validate() is False:
            logging.error('Could not verify internal model checksums. Please re-download CheckM2.')
            sys.exit(1)

        logging.debug('Verifying DIAMOND DB installation path.')
        #currently unused
        self.diamond_path = fileManager.DiamondDB().get_DB_location()


    def __setup_bins(self):
        bin_files = []
        if self.bin_folder is not None:
            all_files = os.listdir(self.bin_folder)
            for f in all_files:
                if f.endswith(self.bin_extension):
                    binFile = os.path.join(self.bin_folder, f)
                    if os.stat(binFile).st_size == 0:
                        logging.warning("Skipping bin {} as it has a size of 0 bytes.".format(f))
                    else:
                        bin_files.append(binFile)

        if not bin_files:
            logging.error("No bins found. Check the extension (-x) used to identify bins.")
            sys.exit(1)

        return sorted(bin_files)

    def prediction_wf(self, genes_supplied=False, model_chosen='auto', debug_cos=False, dumpvectors=False, stdout=False):

        ''' 1: Call genes and automatically determine coding table'''

        if not genes_supplied:
            used_ttables = self.__run_prodigal()
            prodigal_files, used_ttables = fileManager.verify_prodigal_output(self.prodigal_folder, used_ttables, self.bin_extension)

        else:
            logging.info('Using user-supplied protein files.')
            prodigal_files = []
            for bin in self.bin_files:
                shutil.copyfile(bin, os.path.join(self.prodigal_folder, os.path.splitext(os.path.basename(bin))[0]))
                prodigal_files.append(bin)

        ''' 2: Calculate genome metadata from protein files'''

        metadata_df = self.__calculate_metadata(prodigal_files)
        metadata_df = pd.concat(metadata_df.values())
        metadata_df.reset_index(drop=True, inplace=True)

        # make sure metadata is arranged correctly
        metadata_order = keggData.KeggCalculator().return_proper_order('Metadata')
        metadata_order.insert(0, 'Name')
        metadata_df = metadata_df[metadata_order]

        ''' 3: Determine all KEGG annotations of input genomes using DIAMOND blastp'''

        diamond_search = diamond.DiamondRunner(self.total_threads, self.output_folder, self.lowmem)
        diamond_out = diamond_search.run(prodigal_files)

        parsed_diamond_results, ko_list_length = diamond_search.process_diamond_output(diamond_out, metadata_df['Name'].values)

        parsed_diamond_results.sort_values(by='Name', inplace=True)
        metadata_df.sort_values(by='Name', inplace=True)
        parsed_diamond_results.reset_index(drop=True, inplace=True)
        metadata_df.reset_index(drop=True, inplace=True)

        # delete duplicate 'name' column and merge
        del parsed_diamond_results['Name']

        feature_vectors = pd.concat([metadata_df, parsed_diamond_results], axis=1)

        ''' 4: Call general model & specific models and derive predictions'''
        modelProc = modelProcessing.modelProcessor(self.total_threads)

        vector_array = feature_vectors.iloc[:, 1:].values.astype(np.float)

        logging.info('Predicting completeness and contamination using general model.')
        general_results_comp, general_results_cont = modelProc.run_prediction_general(vector_array)

        logging.info('Predicting completeness and contamination using specific model.')
        specific_model_vector_len = (ko_list_length + len(
            metadata_order)) - 1  # -1 = without name TODO a bit ugly - maybe just calculate length on setup somewhere

        # also retrieve scaled data for CSM calculations
        specific_results_comp, specific_results_cont, scaled_features = modelProc.run_prediction_specific(vector_array,
                                                                                                          specific_model_vector_len)

        ''' 5: Determine any substantially complete genomes similar to reference genomes and fine-tune predictions'''

        if not model_chosen == 'specific' or not model_chosen == 'general':
            logging.info('Using cosine simlarity to reference data to select appropriate predictor model.')

            postProcessor = modelPostprocessing.modelProcessor(self.total_threads)
            final_comp, final_cont, models_chosen, csm_array = postProcessor.calculate_general_specific_ratio(
                scaled_features,
                general_results_comp,
                general_results_cont,
                specific_results_comp,
                specific_results_cont)

        logging.info('Parsing all results and constructing final output table.')

        final_results = feature_vectors[['Name']].copy()
        if model_chosen == 'both':
            final_results['Completeness_General'] = np.round(general_results_comp, 2)
            final_results['Contamination_General'] = np.round(general_results_cont, 2)
            final_results['Completeness_Specific'] = np.round(specific_results_comp, 2)
            final_results['Contamination_Specific'] = np.round(specific_results_cont, 2)
            final_results['Model_Used'] = models_chosen

        elif model_chosen == 'auto':
            final_results['Completeness'] = np.round(final_comp, 2)
            final_results['Contamination'] = np.round(final_cont, 2)
            final_results['Model_Used'] = models_chosen

        elif model_chosen == 'general':
            final_results['Completeness_General'] = np.round(general_results_comp, 2)
            final_results['Contamination_General'] = np.round(general_results_cont, 2)

        elif model_chosen == 'specific':
            final_results['Completeness_Specific'] = np.round(specific_results_comp, 2)
            final_results['Contamination_Specific'] = np.round(specific_results_cont, 2)

        else:
            logging.error('Programming error in model choice')
            sys.exit(1)

        if not genes_supplied:
            final_results['Translation_Table Used'] = final_results['Name'].apply(lambda x: used_ttables[x])

        if debug_cos is True:
            final_results['Cosine_Similarity'] = np.round(csm_array, 2)

        if dumpvectors:
            dumpfile = os.path.join(self.output_folder, 'feature_vectors.npy')
            np.save(dumpfile, scaled_features)

        logging.info('CheckM2 finished successfully.')
        final_file = os.path.join(self.output_folder, 'quality_report.tsv')
        final_results.to_csv(final_file, sep='\t', index=False)
        
        if stdout:
            print(final_results.to_string(index=False, float_format=lambda x: '%.2f' % x))

    def __set_up_prodigal_thread(self, queue_in, queue_out, used_ttable):

        while True:
            bin = queue_in.get(block=True, timeout=None)
            if bin == None:
                break

            prodigal_thread = prodigal.ProdigalRunner(self.prodigal_folder, bin)
            binname, selected_coding_table = prodigal_thread.run(bin)

            used_ttable[binname] = selected_coding_table

            queue_out.put((bin, selected_coding_table))

    def __reportProgress(self, total_bins, queueIn):
        """Report number of processed bins."""

        processed = 0

        while True:
            bin, selected_coding_table = queueIn.get(block=True, timeout=None)
            if bin == None:
                if logging.root.level == logging.INFO or logging.root.level == logging.DEBUG:
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                break

            processed += 1

            if logging.root.level == logging.INFO or logging.root.level == logging.DEBUG:
                statusStr = '    Finished processing %d of %d (%.2f%%) bins.' % (
                    processed, total_bins, float(processed) * 100 / total_bins)
                sys.stdout.write('\r{}'.format(statusStr))
                sys.stdout.flush()

    def __run_prodigal(self):

        self.threads_per_bin = max(1, int(self.total_threads / len(self.bin_files)))
        logging.info("Calling genes in {} bins with {} threads:".format(len(self.bin_files), self.total_threads))

        # process each bin in parallel
        workerQueue = mp.Queue()
        writerQueue = mp.Queue()

        for bin in self.bin_files:
            workerQueue.put(bin)

        for _ in range(self.total_threads):
            workerQueue.put(None)

        used_ttables = mp.Manager().dict()

        try:
            calcProc = []
            for _ in range(self.total_threads):
                calcProc.append(
                    mp.Process(target=self.__set_up_prodigal_thread, args=(workerQueue, writerQueue, used_ttables)))
            writeProc = mp.Process(target=self.__reportProgress, args=(len(self.bin_files), writerQueue))

            writeProc.start()

            for p in calcProc:
                p.start()

            for p in calcProc:
                p.join()

            writerQueue.put((None, None))
            writeProc.join()
        except:
            # make sure all processes are terminated
            for p in calcProc:
                p.terminate()

            writeProc.terminate()

        return used_ttables

    def __calculate_metadata(self, faa_files):

        self.threads_per_bin = max(1, int(self.total_threads / len(faa_files)))
        logging.info("Calculating metadata for {} bins with {} threads:".format(len(faa_files), self.total_threads))

        # process each bin in parallel
        workerQueue = mp.Queue()
        writerQueue = mp.Queue()

        for faa in faa_files:
            workerQueue.put(faa)

        for _ in range(self.total_threads):
            workerQueue.put(None)

        metadata_dict = mp.Manager().dict()

        try:
            calcProc = []
            for _ in range(self.total_threads):
                calcProc.append(
                    mp.Process(target=self.__set_up_metadata_thread, args=(workerQueue, writerQueue, metadata_dict)))
            writeProc = mp.Process(target=self.__report_progress_metadata, args=(len(faa_files), writerQueue))

            writeProc.start()

            for p in calcProc:
                p.start()

            for p in calcProc:
                p.join()

            writerQueue.put((None, None))
            writeProc.join()
        except:
            # make sure all processes are terminated
            for p in calcProc:
                p.terminate()

            writeProc.terminate()

        # metadata_dict = process into df (metadata_dict)
        return metadata_dict

    def __set_up_metadata_thread(self, queue_in, queue_out, metadata_dict):

        while True:
            bin = queue_in.get(block=True, timeout=None)
            if bin == None:
                break

            metadata_thread = metadata.MetadataCalculator(bin)
            name1, cdscount_series = metadata_thread.calculate_CDS()
            name2, aalength_series = metadata_thread.calculate_amino_acid_length()
            name3, aa_list, aa_counts = metadata_thread.calculate_amino_acid_counts()

            if name1 == name2 == name3:
                meta_thread_df = pd.DataFrame(
                    {'Name': [name1], 'CDS': [cdscount_series], 'AALength': [aalength_series]})
                for idx, aa in enumerate(aa_list):
                    meta_thread_df[aa] = aa_counts[idx]
            else:
                logging.error('Inconsistent name information in metadata calculation. Exiting.')
                sys.exit(1)

            metadata_dict[bin] = meta_thread_df

            queue_out.put(bin)

    def __report_progress_metadata(self, total_bins, queueIn):
        """Report number of processed bins."""

        processed = 0

        while True:
            bin = queueIn.get(block=True, timeout=None)
            if bin[0] == None:
                if logging.root.level == logging.INFO or logging.root.level == logging.DEBUG:
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                break

            processed += 1

            if logging.root.level == logging.INFO or logging.root.level == logging.DEBUG:
                statusStr = '    Finished processing %d of %d (%.2f%%) bin metadata.' % (
                    processed, total_bins, float(processed) * 100 / total_bins)
                sys.stdout.write('\r{}'.format(statusStr))
                sys.stdout.flush()
