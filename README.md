# multiFolderFileExplorer

this is a pyqt project to show files of different folders within a single view.

this code has these 3 ui layouts:
`buttons row`, `selected folders pane`, `shown files pane`

and these features:

    buttons row:
        'select folder': QFileDialog to take folders
        'remove folder': remove multiple folders and their files from `shown files pane`
        'save folders': save folders in `selected folders pane` to .fecf file
        'load folders': select .fecf .txt files to add (not replacing) folders, checks also for duplicates, ans shows them in `selected folders pane`
    selected folders pane:
        select multiple files
    shown files pane:
        thumbnails: image of file for image formatted files and default thumbnail for other formats
        select multiple files
        drag and drop internally to change the files order, with multiple files based on their drop point (below of all files, right of last row, closest icon)
        drag and drop externally to other apps
