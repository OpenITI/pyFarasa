# farasaPython
Python wrapper for the farasa segmenter and POS tagger

Farasa is an nlp toolkit for Arabic, developed by the Qatar Computing Research Institute. 
It contains a segmenter, a POS tagger, a lemmatizer, a named entity recognition machine, and more.

It can be used online, via an API, or locally, using java jar files. 

farasaPython is a lightweight Python wrapper for the farasa segmenter and POS tagger. 
The script will create a new file that contains the segmented / tagged text, 
and can be used to process either single files or entire directories of files.

Usage examples:
    # in Python:
      > from farasa import batch_process, segment, POS_tag
      > segment(test.txt, test_segmented.txt, restore_ta_marbuta=True)
      > POS_tag(test.txt, test_tagged.txt, ditch_non_Arabic=True)
      > batch_process(segment, test_folder, segmented_folder, restore_ta_marbuta=True)

    # from the command line:
      $ python farasa.py -f segment -i test.txt -o test_segmented.txt
      $ python farasa.py -f POS_tag -i test.txt -o test_tagged.txt

    # For batchprocessing, provide a path to a folder instead of a file:
      $ python farasa.py -f segment -i test_folder -o segmented_folder
      $ python farasa.py -f POS_tag -i test_folder -o tagged_folder

    # command line arguments: 
      -h, --help: print help info
      -d, --ditch_non_Arabic: to remove all non-Arabic text (for POS tagging)
      -r, --restore_ta_marbuta: re-connect ta marbuta to the preceding token
      
      -f, --func: either "segment" or "POS_tag"
      -i, --inpath: path to the input file (or folder, for batchprocessing)
      -o, --outpath: path to the output file (or folder, for batchprocessing)
      -s, --split_char: use this character to mark prefixes and suffixes after segmentation


For more info on Farasa: 
* http://qatsdemo.cloudapp.net/farasa/
* https://github.com/qcri/FarasaSegmenter
