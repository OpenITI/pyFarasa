"""Perform NLP operations using the Farasa jar files.

Info on Farasa:
* http://qatsdemo.cloudapp.net/farasa/
* https://github.com/qcri/FarasaSegmenter

For the moment, only the segmenter and the POS tagger work.

The script will create a new file that contains the segmented / tagged text.

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
"""

import getopt
import os
import re
import subprocess
import sys

def _call(jarfp, infp, outfp=None):
    """Call the relevant jar file and capture the output.

    Args:
        jarfp (str): path to the relevant jar file
        infp (str): path to the input file
        outfp (str): path to the output file

    Returns:
        str
    """
    cmd = ["java", "-Dfile.encoding=UTF-8", "-jar", jarfp, "-i", infp]
    if outfp:
        cmd += ["-o", outfp]
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
##    if stderr:
##        print(stderr.decode("utf-8"))
    if not outfp:
        return stdout.decode("utf-8")
    

def segment(infp, outfp, restore_ta_marbuta=False, split_char="+"):
    """Create segmentized text (split off prefixes and suffixes)\
    using Farasa.

    Args:
        infp (str): path to the input file
        outfp (str): path to the output file
        restore_ta_marbuta (bool): if True, ta marbuta will be
            reconnected to the token.
        split_char (str): character to be used to mark affixes split off
            from tokens. Defaults to "+".

    Returns:
        None
    """
    _call("dist/FarasaSegmenterJar.jar", infp, outfp)

    # post-process if necessary:
    
    if restore_ta_marbuta or split_char!="+":
        with open(outfp, mode="r", encoding="utf-8") as file:
            text = file.read()
        if restore_ta_marbuta:
            text = re.sub("\+ة", "ة", text)
        if split_char:
            text = re.sub("\+", split_char, text)
        with open(outfp, mode="w", encoding="utf-8") as file:
            file.write(text)
    

def POS_tag(infp, outfp, only_Arabic=True, ditch_non_Arabic=False):
    """Tag parts of speech in an Arabic text using Farasa.

    Args:
        infp (str): path to the input file
        outfp (str): path to the output file
        only_Arabic (bool): if True, only Arabic text will be POS tagged.
            In that case, the script will split the text on non-Arabic
            words and only run the POS tagger on the Arabic sections.
        ditch_non_Arabic (bool): if True, all non-Arabic text
            will be removed before starting the POS tagging.

    Returns:
        None
    """
    if not only_Arabic and not ditch_non_Arabic:
        _call("dist/FarasaPOSJar.jar", infp, outfp)
    else:
        # pre-process text:
        
        with open(infp, mode="r", encoding="utf-8") as file:
            text = file.read()

        non_ar_regex = "([a-zA-Z\d .;#\n\r]{6,}[^\n\r][a-zA-Z\d.;#])"

        if ditch_non_Arabic:
            # remove non-Arabic sections:
            ar_only = re.sub(non_ar_regex, "\n", text)
            ar_only = re.sub("[#\|\$]", "", ar_only)
            ar_only = "\n".join([line.strip() \
                                 for line in ar_only.splitlines()\
                                 if line.strip()])
        else:
            # replace non-Arabic sections with a temporary symbol:
            non_ar = re.findall(non_ar_regex, text)
            ar_only = re.sub(non_ar_regex, "\nµµµ\n", text)

        # save the modified text in a temp.txt file

        with open("temp.txt", mode="w", encoding="utf-8") as file:
            file.write(ar_only)

        # run the POS tagger on the temp file:

        _call("dist/FarasaPOSJar.jar", "temp.txt", outfp)
        
        if not ditch_non_Arabic:

            # put the non-Arabic sections back:

            with open(outfp, mode="r", encoding="utf-8") as file:
                ar_only = file.read()
            pattern = r"[\n\r]*S/S µ/PUNC µ/PUNC µ/PUNC E/E[\n\r]*"
            ar_only = re.sub(pattern, "{}", ar_only)
            text = ar_only.format(*non_ar)
            text = re.sub(r"### *[\n\r]*S/S", "S/S #/PUNC #/PUNC #/PUNC", text)

            # save to outfp:

            with open(outfp, mode="w", encoding="utf-8") as file:
                file.write("".join(text))


def batchprocess(func, infolder, outfolder, *args, **kwargs):
    for fn in os.listdir(infolder):
        print(fn)
        infp = os.path.join(infolder, fn)
        outfp = os.path.join(outfolder, fn)
        func(infp, outfp, *args, **kwargs)

def main():
    info = """\
Command line arguments for farasa.py:

-h, --help: print help info
-d, --ditch_non_Arabic: to remove all non-Arabic text (for POS tagging)
-r, --restore_ta_marbuta: re-connect ta marbuta to the preceding token

-f, --func: either "segment" or "POS_tag"
-i, --inpath: path to the input file (or folder, for batchprocessing)
-o, --outpath: path to the output file (or folder, for batchprocessing)
-s, --split_char: use this character to mark prefixes and suffixes after segmentation
"""
    argv = sys.argv[1:]
    opt_str = "hdrf:i:o:s:"
    opt_list = ["help", "ditch_non_Arabic", "restore_ta_marbuta", 
                "func", "inpath", "outpath", "split_char"]

    try:
        opts, args = getopt.getopt(argv, opt_str, opt_list)
    except Exception as e:
        print(e)
        print("Input incorrect: \n"+info)
        sys.exit(2)
    ditch_non_Arabic = False
    restore_ta_marbuta = False
    func = None
    infp = None
    outfp = None
    split_char = None
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(info)
            return
        elif opt in ["-d", "--ditch_non_Arabic"]:
            ditch_non_Arabic = True
        elif opt in ["-r", "--restore_ta_marbuta"]:
            restore_ta_marbuta = True
        elif opt in ["-f", "--func"]:
            func = arg
        elif opt in ["-i", "--inpath"]:
            infp = arg
        elif opt in ["-o", "--outpath"]:
            outfp = arg
        elif opt in ["-s", "--split_char"]:
            split_char = arg

    if not func:
        func = input("Please provide a function: `segment` or `POS_tag`: ")
        if not func in ["segment", "POS_tag"]:
            print("Aborting: unknown function.")
            return 
    if not infp:
        infp = input("Please provide a path to an input file or folder: ").strip()
    if not outfp:
        outfp = input("Please provide a path to an output file or folder: ").strip()
    if func == "segment":
        if os.path.isdir(infp):
            batchprocess(segment, infp, outfp,
                         restore_ta_marbuta=restore_ta_marbuta,
                         split_char=split_char)
        elif os.path.isfile(infp):
            segment(infp, outfp, restore_ta_marbuta=restore_ta_marbuta,
                    split_char=split_char)
        else:
            print("Aborting. No such file or folder:", infp)
    elif func == "POS_tag":
        if os.path.isdir(infp):
            batchprocess(POS_tag, infp, outfp,
                         ditch_non_Arabic=ditch_non_Arabic)
        elif os.path.isfile(infp):
            POS_tag(infp, outfp, ditch_non_Arabic=ditch_non_Arabic)
        else:
            print("Aborting. No such file or folder:", infp)
        


if __name__ == "__main__":
    print("initializing")
    main()
    

##    #output = _call(jarfp, infp)
##    #print(output[:200])
##    outfolder = r"D:\London\stylometry\Tabari2\corpus_segmented"
##    #outfp = os.path.join(outfolder, "test.txt")
##    #outfp = os.path.join(outfolder, "test.txt")
##    #POS_tag(infp, outfp)
##    #batchprocess(POS_tag, r"test\input", r"test\output")
##    POS_tag(r"test\test.txt", r"test\output\test.txt",
##            ditch_non_Arabic=False, only_Arabic=True)
