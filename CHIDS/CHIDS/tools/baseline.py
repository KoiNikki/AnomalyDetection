from multiprocessing import Pool
import itertools

from ..ML.train_model import Training
from ..conf.config import CHUNK_SIZE
from ..utils.trace import Trace
from ..utils.seen_args import SeenArgs
from ..utils.seen_syscalls import SeenSyscalls
from ..utils.anomaly_vector import AnomalyVector
from ..helpers.sysdig import Sysdig

class Baseline:
    def __init__(self, files):
        self.files = files

    def _seen_syscalls(self, scaps_dfs):
        ss_obj = SeenSyscalls(scaps_dfs)
        seen_syscalls = ss_obj.seen_syscalls()
        return seen_syscalls

    def _seen_args(self, scaps_dfs):
        sa_obj = SeenArgs(scaps_dfs)
        seen_args = sa_obj.seen_args()
        return seen_args

    def _get_scaps_traces(self, scaps_dfs):
        trace_obj = Trace(scaps_dfs)
        traces = trace_obj.trace()
        traces = list(filter(None, traces))
        return traces

    def _get_max_seq_freq(self, traces):
        merged_list_sequences = list(itertools.chain.from_iterable(traces))
        max_seq_freq =  max([len(sequence) for sequence in merged_list_sequences])
        return max_seq_freq

    def _get_anomaly_vectors(self, traces, seen_syscalls, seen_args, max_seq_freq):
        av_obj = AnomalyVector(traces, seen_syscalls, seen_args, max_seq_freq)
        all_anomaly_vectors = av_obj.get_anomaly_vectors()
        return all_anomaly_vectors


    # def _scaps_to_dfs(self):
    #     pool = Pool()
    #     Sysdig().process_scap(self.files[0])
    #     all_scaps_dfs = pool.map(Sysdig().process_scap, self.files, chunksize=CHUNK_SIZE)
    #     return all_scaps_dfs
    
    def _files_to_dfs(self):  
        all_files_dfs = []  
        
        for file in self.files:  
            file_df = Sysdig().process_file(file)  
            
            if not file_df.empty:  
                all_files_dfs.append(file_df)  

        return all_files_dfs

    def get_training_elements(self):
        scaps_dfs = self._files_to_dfs()
        seen_syscalls = self._seen_syscalls(scaps_dfs)
        seen_args = self._seen_args(scaps_dfs)
        traces = self._get_scaps_traces(scaps_dfs)
        max_freq = self._get_max_seq_freq(traces)
        anomaly_vectors = self._get_anomaly_vectors(traces, seen_syscalls, seen_args, max_freq)
        thresh_list, model = Training(anomaly_vectors).train_model()

        return seen_syscalls, seen_args, max_freq, model, thresh_list







