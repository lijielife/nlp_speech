# nlp_speech
This library performs speech file conversion using [SoX](http://sox.sourceforge.net), speaker diarization using [LIUM](http://www-lium.univ-lemans.fr/diarization/doku.php/), and speech recognition using [Google Cloud Speech API](https://cloud.google.com/speech/).

## Requirements

1. Linux
1. Python (both 2.7 and 3.5 works)
1. Java (at least 1.6)

This library is developed using Python 2.7.12 on Lubuntu 16.04.1 LTS. The Java environment is 1.8.0_101.

## Setup

1. Clone the project
1. Install SoX with mp3 support: `$ sudo apt-get install sox libsox-fmt-all`
1. Install Python dependencies: `$ sudo pip install -r requirements.txt`
1. [Enable](https://support.google.com/googleapi/answer/6158841) Google Cloud Speech, Google Cloud Storage and Google Cloud Storage APIs. Then import your own keys into `/auth` (`key.json` and `api.json`)
1. Import data: `$ python data.py -i /path/to/flat/data`
1. Run the processing pipeline: `$ python speech.py -d`

## Library structure

```
data/           # Data folder
data*/          # Misc data folders
lium/           # LIUM jar for diarization
    LIUM_SpkDiarization-8.4.1.jar 
auth/
    key.json    # Google API Service Account JSON key, specific to your account
    api.json    # Google API key and storage bucket, specific to your account
data.py         # data operations
speech.py       # speech recognition operations
speech.log      # logging
```

## Google authentication: `/auth`

The `/auth` folder should contain two files:

- `key.json`, your Service Account key. The instruction to create one is [here](https://support.google.com/googleapi/answer/6158849).
- `api.json`, containing your [API key](https://support.google.com/googleapi/answer/6158862) (for async debugging) and your [storage bucket](https://cloud.google.com/storage/docs/creating-buckets) (for async also). The format is as follows:

```json
{
    "api_key": "...",
    "bucket_name": "..."
}
```

## Data folder structure

The structure of `/data` is as follows:

```
data/
    [file_id 1]/
        raw/
            [raw_file]                  # can be in any format, must provide
        resampled/
            [file_id 1].wav
        diarization/
            [file_id 1].seg             # lium output
            [diarized .wav files]
        transcript/
            googleapi/
                [file_id 1].txt         # combined transcript from diarized files (default)
                [file_id 1]-sync.txt    # transcript from Cloud Speech API (synchronous)
                [file_id 1]-async.txt   # transcript from Cloud Speech API (asynchronous)
                [file_id 1]-gold.txt    # gold standard transcript
            textgrid/    
                [file_id 1].TextGrid    # TextGrid file, to be passed to Praat
        temp/                           # intermediate json dumps of diarize_dict
            seg_to_dict.json
            dict_to_wav.json
            wav_to_trans.json
    [file_id 2]/
        ...
    ...
```

The user can create any number of `/data*` folders as necessary, e.g. `/data_completed` to store completed results and `/data_err` to store incompleted results with errors to redo.

## Documentation

### `data.py`

```
Syntax: python data.py (routine) (path) (routine-specfic args)
    routine:
        -r, --crawl: Crawl (path) for files in certain extensions into /data_crawl.
            args: extensions to be called separated by spaces (e.g. .wav .mp3)
        -i, --import: Import (path) into /data. (path) must only contain audio files i.e. must be flat
        -m, --migrate: Migrate (path) from old /data structure to new /data structure
        -c, --clear: Clear temporary files from (path). Most useful for completed folders
        -s, --stats: Output general stats about (path). Most useful for completed folders
        -p, --print-completed: Output completed file_ids from (path). Most useful for /data
    path: Path to the specified folder
```

### `speech.py`

```
Syntax: python speech.py (option)
    option:
        -d, --diarize, --default: Run the diarization pipeline, results in transcript/googleapi/*.txt and transcript/textgrid/*.TextGrid
        -s, --sync: Run the synchronous pipeline, results in transcript/googleapi/*-sync.txt
        -a, --async: Run the asynchronous pipeline, results in transcript/googleapi/*-async.txt
    no option specified: treated as -d
```