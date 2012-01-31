from Bio.Blast import NCBIWWW, NCBIXML
import cPickle

sequences = """>strand1
GTTCCCGATACAGCGAGCCGCGGCGGCGAGCCACCTCCTTCCTCCTTGGCAGACCATGTTCCCCGTGTGGCGCATGCGCGGGTGGGGTCGTGCCCTTTGTTTGTTGCCCGGGCCCGCCTGCCCCGAAAGCCGGAGAACTCAAGGGGGGGGGGGGCCAGGCAAGGGTCACTCACGCGCCTCCCTCTGGTTGTTCGATGCGAGCATGTCCCTCAGGTCCCCTACCGAAATCTGAATGGGGTTCGCCCCTTACCCGCGCCTGCCGGCGTAGGGTAGGCACACGCTGAGCCAGTCAGTGTAGCGCGCGTGCAGCCCCGGACATCTAAGGGCATCACAGACCTGTTATTGCTCAATCTCGGGTGGCTGAACGCCACTTGTCCCTCTGGGAAGTTGGGGGACGCCGACCGCTCGGGGGTCGCGTAACTAGTTAGCATGCCAGAGTCTCGTTCGTTATCGGAATTAACCAGACAAATCGCTCCACCAACTAAGAACGGCCATGCACCACCACCCAGGGAATGGGGAAAGAGCTATCAATCTGTCAATCCTGTCCCTGTCCGGGCCGGGTGAGGTTTCCCGTGTTGAGTCAAATTAAGCCGCCCGCTCCACTCCTGGTGGTGCCCTTCCGTCAATTCCTTTAAGTTTCAGCTTTGCAACCATACTCCCCCCGGAACCCAAAGACTTTGGTTTCCCGGAAGCTGCCCGGCGGGTCATGGGAATAACGCCGCCGCATCGCCGGTCGGCATCGTTTATGGTCGGAACTACGACTGTATCTGATCGTCTTCGAACCTCCGACTTTCGTTCTTGATTAATGAAGACATTCTTGGCAAATGCTTTCGCTCTGGTCGGTCTTGCGCGGGTCCAAGAATTTGAACCTCTAGCGATGCAATACGAATGCCCCCGGCCCGTTCCTCCTGACTCATCGCCCTCAGTTCTCAAAGCAACCTAGAATAGAAGCGGCGGATCCTATATATCGCATATCT
>strand2
AATTATTCCGCTAAAAGTCATACAAGGTGGATTTGGTGAGGGCGCTCCCAACACCGGGAGGCCCTCCTGGCACAGCACGTCCCCCAGAGGGTTTACCTCAGGCCGGCCAGTCATACAGCAACAGGACCAGACTCCAGAGAGGGGTTGGAAGGTTTCACAACACAGGGAGGCGGTGCCGACCACGGGGATGGAGGGCGAACGCTGACAGCACCCCACGGGCACCCAGGGATTCCTGCCCCCATGGCGCAGTGCACAGGCCACACACGCGGCACGCGCACGATGGCACGACGGCCGCCGGTAAAGCCCCCACCGGCGTCAGCGGTGACACGCAAGTGCAGCGCGGCCCCGGCCGGCCGAGGGGACGGAGTTGGCAGGGGAGGAGAGGGAGGGGCGGGCCTCTCCTGAACGGACTCCCCTGCGGGCCCACCGCACCCAACCCAAGGGAGGACAGGCGACCCCTCAAGGGGTCCTTAAACCTCCGCGCCAAAACGCGCTAGGTACCTGGACAGCGGGGGCGGACGATGCGGGGGACAGGCATCCGGCCCCCTACCCTCGAGACTCCCTATCATGAAGGCTGGGGAGAGTGAGCGGGCCAGTCCGGGACCGGTGGCCTGGTCTCGCAGAGGCAAGGATGGTGACAGCCGCAGCGATGGGAACCCGACCGGCCCCAATGGGAGCCGTCGGTGATGGAACCGAGCCAGCGGGACGAGGCATGATGACAGCTCCAGCGGGGAGGGCACCGAGGCCCCCACACTGCCATGACTCCAAGAACCATCCCCACGCCCGCCGACACACACGTGGGGGCCACAACACGGTGCCACTCCCCTGCTGCTCAGCAAGCCTGCATGCATCAGTCTGCCCCACGACATGAACTACACAGTATCGTCGCGTCATGACATGTTGTCGTTGATCAAGCTCCCTGCACGTAGTTACTCAGCCTCTGTCGCTAGGTACGCGGACCTGGGGCTAGCCTTATCATTAAGC 
>assembly
ATGAACGCTGGCGGCGTGCCTAATANATGCAAGTCGAGCGAACAGATAAGGAGCTTGCTCCTTTGACGTTAGCGGCGGACGGGTGAGTAACACGTGGGTAACCTACCTATAAGACTGGGACAACTTCGGGAAACCGGAGCTAATACCGGATAATATGTTGAACCGCATGGTTCAATAGTGAAAGATGGTTTTGCTATCACTTATAGATGGACCCGCGCCGTATTAGCTAGTTGGTGAGGTAATGGCTCACCAAGGCAACGATACGTAGCCGACCTGAGAGGGTGATCGGCCACACTGGAACTGAGACACGGTCCAGACTCCT
"""

result_handle = NCBIWWW.qblast("blastn", "nr", sequences)
blast_records = NCBIXML.parse(result_handle)

for b,fname in zip(blast_records, ['strand1_blast.pickle', 'strand2_blast.pickle', 'assembly_blast.pickle']):
    with open(fname, 'wb') as h:
        cPickle.dump(b, h)
    
