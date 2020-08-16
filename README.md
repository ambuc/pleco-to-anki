# pleco-to-anki
python script to turn pleco .xml exports into something anki can read

## Workflow

*  On phone, in Pleco, download as .xml. Save to Google Drive instead of local storage.
*  On computer, download .xml from Google drive.
*  On computer, run `./p2a.py ~/Downloads/<path_to_backup.xml> > /tmp/out.csv`.
*  On computer, open Anki and import from `.csv`.
*  On computer, in Anki, sync and quit.
