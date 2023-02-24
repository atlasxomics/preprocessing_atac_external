import csv

from slims.criteria import equals
from slims.slims import Slims

from wf.creds import username, password


NA = ['na', '#N/A', '=NA()', 'NA', 'nan', None]

def csv_to_dict(path):
    with open(path) as f:
        reader = csv.reader(f)
        return dict(zip(reader.__next__(), reader.__next__()))
    
def get_pk(cntn_id, slims):
    return slims.fetch('Content', equals('cntn_id', cntn_id))[0].pk()  

def push_result(payload, slims):
    return slims.add("Result", payload)

def slims_init(username=username, password=password):
    return Slims("slims", "https://slims.atlasxomics.com/slimsrest", username, password) 

mapping = {
    'Genome': 'rslt_cf_refGenome',
    'Pipeline version': 'rslt_cf_pipelineVersion',
    'Estimated number of cells': 'rslt_cf_estimatedNumberOfCells',
    'Confidently mapped read pairs': 'rslt_cf_confidentlyMappedReadPairs',
    'Estimated bulk library complexity': 'rslt_cf_estimatedBulkLibraryComplexity1',
    'Fraction of all fragments in cells': 'rslt_cf_fractionOfAllFragmentsInCells',
    'Fraction of all fragments that pass all filters and overlap called peaks': 'rslt_cf_fractionOfAllFragmentsThatPassAllFilt',
    'Fraction of genome in peaks': 'rslt_cf_fractionOfGenomeInPeaks',
    'Fraction of high-quality fragments in cells': 'rslt_cf_fractionOfHighQualityFragmentsInCells',
    'Fraction of high-quality fragments overlapping TSS': 'rslt_cf_fractionOfHighQualityFragmentsOverlap',
    'Fraction of high-quality fragments overlapping peaks': 'rslt_cf_fractionOfHighQualityFragmentsOrlapPe',
    'Fraction of transposition events in peaks in cells': 'rslt_cf_fractionOfTranspositionEventsInPeaksI',
    'Fragments flanking a single nucleosome': 'rslt_cf_fragmentsFlankingASingleNucleosome',
    'Fragments in nucleosome-free regions': 'rslt_cf_fragmentsInNucleosomeFreeRegions',
    'Mean raw read pairs per cell': 'rslt_cf_meanRawReadPairsPerCell1',
    'Median high-quality fragments per cell': 'rslt_cf_medianHighQualityFragmentsPerCell',
    'Non-nuclear read pairs': 'rslt_cf_nonNuclearReadPairs',
    'Number of peaks': 'rslt_cf_numberOfPeaks',
    'Percent duplicates': 'rslt_cf_percentDuplicates',
    'Q30 bases in barcode': 'rslt_cf_q30BasesInBarcode',
    'Q30 bases in read 1': 'rslt_cf_q30BasesInRead1',
    'Q30 bases in read 2': 'rslt_cf_q30BasesInRead2',
    'Q30 bases in sample index i1': 'rslt_cf_q30BasesInSampleIndexI1',
    'Sequenced read pairs': 'rslt_cf_sequencedReadPairs1',
    'Sequencing saturation': 'rslt_cf_sequencingSaturation',
    'TSS enrichment score': 'rslt_cf_tssEnrichmentScore',
    'Unmapped read pairs': 'rslt_cf_unmappedReadPairs',
    'Valid barcodes': 'rslt_cf_validBarcodes'
} 