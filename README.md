# RAW-Processor
A python script I use to batch-convert all my obsolete .RAW images to .jpg and store in folders named by date the image was taken.

When running for the first time, verify the procedure on a small subset of your images, which should be backed up. I have not had any problmes, but the script does delete the .RAW images after conversion--that is its purpose, after all.

Rough procedure (more detailed to come)
- Run script -> add parent directory(ies) containing .RAW files
> This can be as top-level as you want. This is the directory where the script will begin its search. Any child directories will be discovered.
- In any child directory(ies) you wish, add a folder named "compressor". Put any .RAW images for conversion into the compressor folder. This can be done in as many locations as you want, as long as you are within one of your listed parent directories.
- Run the script and follow prompts for conversion.

If you use this and have any issues, feel free to reach out to me. I made this for myself, so I haven't tested it on other devices (especially other operating systems).
