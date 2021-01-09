# pleco-to-anki

A Python script which parses XML output from Pleco and creates
semicolon-separated CSV data for [Anki](https://apps.ankiweb.net/).

## Example

### Input:

```xml
<?xml version="1.0" ?>
<plecoflash formatversion="2" creator="Pleco User -1" generator="Pleco 2.0 Flashcard Exporter" platform="Android" created="1605883885">
  <categories/>
  <cards>
    <card language="chinese">
      <entry>
        <headword charset="sc">感冒</headword>
        <headword charset="tc">感冒</headword>
        <pron type="hypy" tones="numbers">gan3mao4</pron>
        <defn>noun common cold
verb 1 catch cold 2 dialect be interested in; like (usu. used in the negative)</defn>
      </entry>
      <dictref dictid="PACE" entryid="21428224"/>
    </card>
    ...
  </cards>
</plecoflash>
```

### Output:

```csv
<span><font color="blue">găn</font></span> <span><font color="purple">mào</font></span>;感冒;noun common cold verb 1 catch cold 2 dialect be interested in. like (usu. used in the negative)
...
```

## Prerequisites

*  `git` or `gh`, for downloading the repo.
*  `bazel`, for building/running the script.

## How to install:

*  Download the repo locally with `gh repo clone ambuc/pleco-to-anki` or
   `git clone https://github.com/ambuc/pleco-to-anki.git`.
*  Build the project with `bazel build ...`.

## Usage

For me, this script is the keystone of a larger pipeline.

### Step 1: Export from Pleco:

*  On your phone, open [Pleco](https://www.pleco.com/products/pleco-for-android/).
*  Open the menu. 
   *  Under "FLASHCARDS", select "Import / Export", then "Export Cards". 
   *  Under "File Format", set "File format" to "XML File".
   *  Under "Include Data", mark "Dictionary definitions" as true.
   *  Select "Export now" and save the `flash-<todays_date>.xml` file to
      Google Drive, Dropbox, etc.

### Step 2: Use `p2a` to generate a `.csv`.

*  On your computer, download the `.xml` file you created in the previous step.
*  Run `bazel run :p2a -- --path=your_input.xml > your_output.csv` to
   generate a new `.csv` file.
*  (Mac-only, optional): specify an 
   `--audio_out=~/Library/Application\ Support/Anki2/User\ 1/collection.media`
   path to a directory in which to write audio files. (Mac-only since this uses
   the `say` utility.)
   
This generates a new, semicolon-separated file. The first column is the pinyin
as HTML, the second column is the word, and the third column is the definition.

### Step 3: Use [Anki](https://apps.ankiweb.net/) to import the `.csv`.

*  On your computer, open [Anki](https://apps.ankiweb.net/) and import the
   `.csv` file you created in the previous step.
*  Make sure the columns map to fields in your custom card layout. Save, sync,
   and quit.
