# mobilephonetools
Various tools for dealing with binary data from mobile phones.

* <b>OmniGraphx</b>: Searches phone binary data for graphics files. Currently only supports gif
* <b>sbn2bin</b>: Converts Sony Ericsson .sbn files to .bin
* <b>hsb-extractor</b>: Extracts PCM samples from Beatnik .HSB files. Currently does not support MPEG or IMA4. Does not support "ESND" encrypted HSB files.
  * <b>wave-bigtolittle</b>: Batch converts the endianness of WAV files in a folder.
  * <b>alaw16.lut</b>: Lookup table for converting A-law waves to 16-bit PCM.
