# Wordle Scratchpad by Nate

## Download Dictionary for Word List
[Webster Unabridged Dictionary Download](https://gutenberg.org/ebooks/29765.txt.utf-8)  
Download the Plain Text UTF-8 text file. Rename to `websters-unabridged.txt` and place it in the folder with the code. The parsing function is tailored to get its word list from this dictionary.  

## Log Output File
If you play Wordle, you will immediately recognize the value of this output: ![example log file](example-log-file.txt)  
  
## The User Interface
The UI is very unusual. I was experimenting with keyboard-only operation and wanted to make all user inputs go through the 'clipboard.' Therefore, the 'flow' of using the program is as follows:  
`<t>` type your guess  
`<Enter>` puts the guess on the clipboard  
`<g>` to transfer from the clipboard to guess in the program  
`<t>` type your hint  
`<Enter>` places hint on the clipboard  
`<h>` transfer the hint from clipboard to hint in the program  
At this point, you should see an output showing the number of remaining possible solutions based on the guess and hint you entered.  
`<c>` and you will see a list of the top-10 next guesses based on the scoring described in the below log file from an actual run of the program.  
`<l>` will show a list of words that contain the letters on the clipboard
Use the recommended guesses to make another guess in Wordle then repeat the steps above for your second guess and so on.  
`<s>` is used to transfer from the clipboard to practice solution.  
`<a>` is used to transfer from the clipboard to practice guess and the program will show the Wordle hint based on the solution-guess combination.  